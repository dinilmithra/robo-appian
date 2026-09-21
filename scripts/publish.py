from __future__ import annotations
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = PROJECT_ROOT / "dist"

def run(*args: str) -> None:
    print("> poetry " + " ".join(args))
    subprocess.run(["poetry", *args], cwd=PROJECT_ROOT, check=True)

def get_version() -> str:
    result = subprocess.run(["poetry", "version", "-s"], cwd=PROJECT_ROOT, check=True, capture_output=True, text=True)
    return result.stdout.strip()

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate, version, build, and publish robo-appian to PyPI.")
    parser.add_argument("version", nargs="?", default="patch", help="Poetry version rule or explicit version (default: patch).")
    parser.add_argument("--skip-tests", action="store_true", help="Skip pytest before publishing.")
    parser.add_argument("--build-only", action="store_true", help="Build the release but do not upload it to PyPI.")
    return parser.parse_args()

def main() -> int:
    args = parse_args()
    token = os.environ.get("POETRY_PYPI_TOKEN_PYPI") or os.environ.get("PYPI_TOKEN")
    if not args.build_only and not token:
        print("ERROR: PyPI token is missing. Set POETRY_PYPI_TOKEN_PYPI or PYPI_TOKEN before publishing.", file=sys.stderr)
        return 2
    if token:
        os.environ["POETRY_PYPI_TOKEN_PYPI"] = token
    try:
        if not args.skip_tests:
            run("run", "pytest")
        run("check")
        old_version = get_version()
        run("version", args.version)
        new_version = get_version()
        if old_version == new_version:
            print(f"ERROR: Version is still {new_version}. PyPI releases require a new version.", file=sys.stderr)
            return 2
        if DIST_DIR.exists():
            print(f"Removing old build directory: {DIST_DIR}")
            shutil.rmtree(DIST_DIR)
        run("build")
        wheel = DIST_DIR / f"robo_appian-{new_version}-py3-none-any.whl"
        sdist = DIST_DIR / f"robo_appian-{new_version}.tar.gz"
        missing = [str(path) for path in (wheel, sdist) if not path.is_file()]
        if missing:
            print("ERROR: Expected release file(s) were not generated:\n  " + "\n  ".join(missing), file=sys.stderr)
            return 2
        print(f"Release {new_version} built successfully.")
        if args.build_only:
            print("Build-only mode: PyPI upload skipped.")
            return 0
        run("publish")
        print(f"Published robo-appian {new_version} to PyPI successfully.")
        return 0
    except subprocess.CalledProcessError as exc:
        print(f"ERROR: Release command failed with exit code {exc.returncode}.", file=sys.stderr)
        return exc.returncode or 1

if __name__ == "__main__":
    raise SystemExit(main())
