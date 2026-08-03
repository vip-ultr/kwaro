# Publishing kwaro (cross-OS)

kwaro is a pure-Python, zero-runtime-dependency package, so ONE wheel
(`py3-none-any`) serves Windows, macOS, and Linux. Publishing means getting that
wheel into four channels. The artifacts are prepared in-repo; the credentialed
uploads need a maintainer (PyPI token, and push access to the tap/bucket repos).

## Channel 1 - PyPI (required, covers all OS at the pip level)

Artifacts already built in `dist/` (after `uv build`):

- `dist/kwaro-0.6.0-py3-none-any.whl`
- `dist/kwaro-0.6.0.tar.gz`

Verify them first (no publish without a green check):

```bash
uv build                                   # recreates dist/ from current tree
python3 -m pytest tests/ -q                # must be 35 passed
twine check dist/*                         # sdist + wheel metadata valid
```

Publish (needs a PyPI API token with upload rights for the `kwaro` project):

```bash
uv publish                                # or: twine upload dist/*
```

After this, `pip install kwaro` works on Windows/macOS/Linux. Verify:

```bash
python3 -m pip install --break-system-packages kwaro   # or in a clean venv
kwaro --help
```

## Channel 2 - GitHub Releases (asset download, no registry)

The `v0.6.0` tag exists. Attach the two `dist/` files as release assets so users
can download without a registry. Do this from the GitHub web UI (Releases ->
v0.6.0 -> Edit -> attach `dist/kwaro-0.6.0-py3-none-any.whl` and
`dist/kwaro-0.6.0.tar.gz`), or via `gh`:

```bash
gh release upload v0.6.0 dist/kwaro-0.6.0-py3-none-any.whl dist/kwaro-0.6.0.tar.gz
```

## Channel 3 - Homebrew (macOS + Linux)

Create a tap repo `vip-ultr/homebrew-kwaro`, then add `Formula/kwaro.rb`
(canonical copy kept at `packaging/homebrew/kwaro.rb` in this repo). The formula
pulls the PyPI sdist; the sha256 below is for `kwaro-0.6.0.tar.gz`
(`cf09fbb3248f92960f56e02002951fd0835409a42c4e4c2174e8c4958a943d93`).

```bash
brew tap vip-ultr/kwaro
brew install kwaro
```

To bump versions: update `url`, `sha256`, and the `version` method in
`packaging/homebrew/kwaro.rb`, then sync the tap repo.

## Channel 4 - Scoop (Windows)

Create a Scoop bucket repo (e.g. `vip-ultr/scoop-kwaro`) and add `kwaro.json`
(canonical copy at `packaging/scoop/kwaro.json`). It depends on Python and runs
`pip install kwaro==<version>`, so no binary hash to maintain.

```bash
scoop bucket add kwaro https://github.com/vip-ultr/scoop-kwaro
scoop install kwaro
```

To bump versions: update `version` and the `pip install kwaro==<version>` line in
`packaging/scoop/kwaro.json`, then sync the bucket repo.

## Cross-OS verification before/after publish

CI already runs pytest on ubuntu/macos/windows x Python 3.10-3.12. After publish,
sanity-check each OS install path:

- Windows:   `pip install kwaro` then `kwaro --help`
- macOS:     `pip install kwaro` (or `brew install kwaro`) then `kwaro --help`
- Linux:     `pip install kwaro` (or `brew install kwaro`) then `kwaro --help`

## Notes

- The CLI stays zero-dep. `serve` (browser UI) is an optional extra; base install
  never pulls fastapi/uvicorn/websockets.
- Do NOT require Docker to install or run. Docker is out of scope per locked
  decision L11/L12.
- Never rewrite CHANGELOG history. Each release is additive.
