"""kwaro CLI entry point (scaffold).

This is a placeholder entry point so the package installs and runs. The real
subcommands (chat, serve, scan, init) are planned in docs/ and implemented later.
"""

import sys


def main() -> int:
    print("kwaro - a free, open-source security scanner")
    print("Repository is in early scaffolding. See docs/ for the plan.")
    print("Planned commands: kwaro chat | kwaro serve | kwaro scan | kwaro init")
    return 0


if __name__ == "__main__":
    sys.exit(main())
