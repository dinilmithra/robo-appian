"""Command-line utilities for robo-appian setup."""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence

_SUPPORTED_BROWSERS = ("chromium", "firefox", "webkit", "all")


def install_browser(browser: str | None = None) -> int:
    """Install browser-managed browser binaries using this Python environment.

    If ``browser`` is omitted or set to ``"all"``, install the full set of
    browser-managed browsers.
    """
    normalized = (browser or "all").strip().lower()
    if normalized not in _SUPPORTED_BROWSERS:
        raise ValueError(
            f"Unsupported browser {browser!r}. Choose one of: "
            + ", ".join(_SUPPORTED_BROWSERS)
        )

    command = [sys.executable, "-m", "playwright", "install"]
    if normalized != "all":
        command.append(normalized)
    return subprocess.call(command)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the robo-appian command-line interface."""
    parser = argparse.ArgumentParser(prog="robo-appian")
    subparsers = parser.add_subparsers(dest="command", required=True)

    install_parser = subparsers.add_parser(
        "install-browser",
        help="Install a Playwright-managed browser binary.",
    )
    install_parser.add_argument(
        "browser",
        nargs="?",
        default="all",
        choices=_SUPPORTED_BROWSERS,
        help="Browser to install. Omit or use 'all' to install the full set.",
    )

    args = parser.parse_args(argv)
    if args.command == "install-browser":
        return install_browser(args.browser)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
