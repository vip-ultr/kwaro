"""kwaro core: workspace (clone or copy target into a temp workspace, L9).

Computes file hashes for diff-aware rescan. Cross-OS via pathlib. Pure stdlib.
No network writes; git clone only when target is a URL.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Workspace:
    root: str
    target: str = ""
    target_type: str = "local"  # local | git
    commit: str = ""
    file_hashes: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_target(cls, target: str) -> "Workspace":
        if target.startswith("http://") or target.startswith("https://") or target.endswith(".git"):
            return cls._clone_git(target)
        return cls._copy_local(target)

    @classmethod
    def _clone_git(cls, url: str) -> "Workspace":
        root = tempfile.mkdtemp(prefix="kwaro-")
        subprocess.run(["git", "clone", "--depth", "1", url, root],
                       check=True, capture_output=True)
        commit = ""
        try:
            commit = subprocess.run(["git", "-C", root, "rev-parse", "HEAD"],
                                    capture_output=True, text=True).stdout.strip()
        except Exception:
            pass
        ws = cls(root=root, target=url, target_type="git", commit=commit)
        ws._index()
        return ws

    @classmethod
    def _copy_local(cls, path: str) -> "Workspace":
        root = tempfile.mkdtemp(prefix="kwaro-")
        shutil.copytree(path, root, dirs_exist_ok=True)
        ws = cls(root=root, target=path, target_type="local")
        ws._index()
        return ws

    def _index(self) -> None:
        for dirpath, _, files in os.walk(self.root):
            for fn in files:
                if ".git" in dirpath.split(os.sep):
                    continue
                p = os.path.join(dirpath, fn)
                try:
                    # L9: key by RELATIVE path so baselines match across temp workspaces
                    rel = os.path.relpath(p, self.root)
                    self.file_hashes[rel] = self._hash_file(p)
                except OSError:
                    continue

    @staticmethod
    def _hash_file(p: str) -> str:
        h = hashlib.sha256()
        with open(p, "rb") as fh:
            for chunk in iter(lambda: fh.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    def git_diff_files(self, since_commit: str) -> List[str]:
        """L9: for git targets, return changed files (relative paths) since `since_commit`."""
        if self.target_type != "git" or not since_commit:
            return []
        try:
            out = subprocess.run(
                ["git", "-C", self.root, "diff", "--name-only", since_commit, "HEAD"],
                capture_output=True, text=True, check=True,
            ).stdout.strip().splitlines()
            return [p for p in out if p]
        except Exception:
            return []

    def diff_targets(self, baseline_hashes: dict) -> List[str]:
        """L9: relative paths to scan. For git, changed vs baseline commit; for local,
        files whose hash differs from baseline. Falls back to all when no baseline.
        Returns RELATIVE paths; callers resolve via os.path.join(root, p)."""
        if not baseline_hashes:
            return list(self.file_hashes.keys())
        if self.target_type == "git":
            changed = self.git_diff_files(baseline_hashes.get("commit", ""))
            if changed:
                return changed
        # local or git-fallback: hash-based diff
        return [p for p, h in self.file_hashes.items() if baseline_hashes.get(p) != h]

    def cleanup(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)
