# Release Process

How kwaro is versioned, released, and communicated. Modern, low-ceremony, automated
where possible. (Locked-decision L12.)

## Versioning

- Semantic Versioning 2.0 (`MAJOR.MINOR.PATCH`).
- `0.x.y`: pre-1.0, API may change between minors. We still keep changes documented.
- `1.0.0`: when the find -> prove -> fix -> verify loop is stable across the major
  languages and the privacy/sandbox posture is locked.

## Changelog

- `CHANGELOG.md` is kept, formatted per Keep a Changelog.
- Each release groups: Added, Changed, Fixed, Removed. Never rewrite history.
- Entries are written as the work lands (not all at release time).

## Tags and releases

```bash
git tag -s v0.1.0 -m "v0.1.0: core engine + static analyzers"
git push origin v0.1.0
```
- Tags are signed (GPG) where the maintainer has keys; DCO sign-off on commits.
- GitHub Release notes are generated from the CHANGELOG section for that version.

## Publishing to PyPI

- Build: `python -m build` (sdist + wheel). Wheel is pure-Python, no compiled parts.
- Publish: `uv publish` / `twine upload dist/*` from CI on a tagged, green build.
- The CLI must `pip install kwaro` and `python -m kwaro` with ZERO extra deps.

## Cross-OS verification

- CI matrix: ubuntu-latest, macos-latest, windows-latest, Python 3.10/3.11/3.12.
- The fixture-repo eval runs on all three OSes every PR.

## First-release checklist (v0.6.0)

- [x] Core engine + config + SQLite (Phase 1)
- [x] Providers: Ollama + OpenAI-compat (Phase 2)
- [x] Static analyzers + generic profile (Phase 3)
- [x] Pipeline + PoC generate-only (Phase 4)
- [x] CLI: scan, SARIF/JSON, diff rescan (Phase 5)
- [x] Browser UI via `serve` extra (Phase 6)
- [ ] README quickstart + 60-second demo GIF
- [x] CHANGELOG, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT
- [x] Fixture-repo eval green on all OSes (CI matrix: ubuntu/macos/windows, py3.10-3.12)
- [ ] PyPI publish (dry-run verified; actual publish is a maintainer action)

## Communication

- Launch post leads with the demo (GC1): scan a known-vuln repo, prove + fix +
  verify, locally, free. Not architecture bullets.
- Post in r/selfhosted, r/opensource, HN, security Discords, and X with the GIF.
