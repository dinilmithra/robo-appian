from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import time

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_RETRIES = 3


def _poetry_command(*args: str) -> list[str]:
    """Build a Poetry command using the installed Poetry executable."""
    poetry = shutil.which("poetry")
    if not poetry:
        raise RuntimeError(
            "Poetry was not found on PATH. Install Poetry or add its executable to PATH."
        )
    return [poetry, *args]


def run_poetry(
    *args: str,
    capture_output: bool = False,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a Poetry project command using the active process environment."""
    command = _poetry_command(*args)
    print("> " + subprocess.list2cmdline(command))
    return subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=capture_output,
        text=True,
        env=env,
    )


def run_python(*args: str, capture_output: bool = False) -> subprocess.CompletedProcess[str]:
    """Run a module or script with the active virtual-environment Python."""
    command = [sys.executable, *args]
    print("> " + subprocess.list2cmdline(command))
    return subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=capture_output,
        text=True,
    )


def validate_runtime() -> None:
    """Require .venv-core Python and an installed Poetry executable."""
    base_prefix = getattr(sys, "base_prefix", sys.prefix)
    if sys.prefix == base_prefix:
        raise RuntimeError(
            "Publisher must run from an active virtual environment. Activate .venv-core "
            "and run the command again."
        )

    print(f"Publisher Python: {sys.executable}")
    print(f"Python version: {sys.version.split()[0]}")

    try:
        pytest_result = run_python("-m", "pytest", "--version", capture_output=True)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "pytest is not available from the active virtual environment. "
            "Run CORE environment setup and retry."
        ) from exc
    print(pytest_result.stdout.strip())

    try:
        poetry_result = run_poetry("--version", capture_output=True)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("Poetry is installed but could not be executed.") from exc
    print(poetry_result.stdout.strip())


def get_version() -> str:
    """Return the current Poetry project version."""
    return run_poetry("version", "-s", capture_output=True).stdout.strip()


def _make_writable(path: str | os.PathLike[str]) -> None:
    """Best-effort removal of a Windows read-only attribute."""
    target = Path(path)
    try:
        target.chmod(target.stat().st_mode | stat.S_IWRITE)
    except (FileNotFoundError, OSError):
        pass


def _rmtree_error(function, path, exc_info) -> None:  # type: ignore[no-untyped-def]
    """Retry deletion after clearing a read-only attribute."""
    _make_writable(path)
    function(path)


def clean_dist() -> None:
    """Remove stale release artifacts and recreate a writable dist directory."""
    if DIST_DIR.exists():
        print(f"Removing old build directory: {DIST_DIR}")
        for attempt in range(1, BUILD_RETRIES + 1):
            try:
                shutil.rmtree(DIST_DIR, onexc=_rmtree_error)
                break
            except PermissionError as exc:
                if attempt == BUILD_RETRIES:
                    raise RuntimeError(
                        f"Unable to remove {DIST_DIR}. Close Explorer/archive preview windows, "
                        "editors, antivirus scans, or another process that may be holding a "
                        "release artifact open, then retry."
                    ) from exc
                time.sleep(attempt)

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    probe = DIST_DIR / ".write-test"
    try:
        probe.write_text("ok", encoding="utf-8")
    except PermissionError as exc:
        raise RuntimeError(
            f"Build output directory is not writable: {DIST_DIR}. Check Windows ACLs or "
            "a process holding the directory open."
        ) from exc
    finally:
        probe.unlink(missing_ok=True)


def build_release() -> None:
    """Build release artifacts with retries for transient Windows file locks."""
    last_error: subprocess.CalledProcessError | None = None
    for attempt in range(1, BUILD_RETRIES + 1):
        clean_dist()
        try:
            run_poetry("build")
            return
        except subprocess.CalledProcessError as exc:
            last_error = exc
            if attempt == BUILD_RETRIES:
                break
            print(
                f"Build attempt {attempt} failed. Retrying after clearing dist "
                f"({attempt}/{BUILD_RETRIES})...",
                file=sys.stderr,
            )
            time.sleep(attempt)
    assert last_error is not None
    raise last_error


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the release workflow."""
    parser = argparse.ArgumentParser(
        description="Validate, version, build, and publish robo-appian to PyPI."
    )
    parser.add_argument(
        "version",
        nargs="?",
        default="patch",
        help="Poetry version rule or explicit version (default: patch).",
    )
    parser.add_argument(
        "--skip-tests", action="store_true", help="Skip pytest before publishing."
    )
    parser.add_argument(
        "--build-only",
        action="store_true",
        help="Build the release but do not upload it to PyPI.",
    )
    return parser.parse_args()


def main() -> int:
    """Run the validated robo-appian release workflow."""
    args = parse_args()
    validate_runtime()
    token_source: str | None = None
    token: str | None = None
    for variable in ("POETRY_PYPI_TOKEN_PYPI", "PYPI_TOKEN", "PYPI_API_TOKEN"):
        value = os.environ.get(variable)
        if value:
            token_source = variable
            token = value
            break

    publish_env = os.environ.copy()
    if token:
        # Poetry natively consumes POETRY_PYPI_TOKEN_PYPI. Keep the secret only in
        # the child-process environment and never write or print its value.
        publish_env["POETRY_PYPI_TOKEN_PYPI"] = token
        print(f"PyPI token detected from environment variable: {token_source}")
    elif not args.build_only:
        print(
            "ERROR: PyPI token is missing. Set POETRY_PYPI_TOKEN_PYPI, PYPI_TOKEN, "
            "or PYPI_API_TOKEN before publishing.",
            file=sys.stderr,
        )
        return 2

    old_version: str | None = None
    version_changed = False
    published = False
    try:
        if not args.skip_tests:
            run_python("-m", "pytest")
        run_poetry("check")

        old_version = get_version()
        run_poetry("version", args.version)
        new_version = get_version()
        version_changed = old_version != new_version
        if not version_changed:
            print(
                f"ERROR: Version is still {new_version}. PyPI releases require a new version.",
                file=sys.stderr,
            )
            return 2

        build_release()

        wheel = DIST_DIR / f"robo_appian-{new_version}-py3-none-any.whl"
        sdist = DIST_DIR / f"robo_appian-{new_version}.tar.gz"
        missing = [str(path) for path in (wheel, sdist) if not path.is_file()]
        if missing:
            print(
                "ERROR: Expected release file(s) were not generated:\n  "
                + "\n  ".join(missing),
                file=sys.stderr,
            )
            return 2

        print(f"Release {new_version} built successfully.")
        if args.build_only:
            print("Build-only mode: PyPI upload skipped.")
            return 0

        run_poetry("publish", env=publish_env)
        published = True
        print(f"Published robo-appian {new_version} to PyPI successfully.")
        return 0
    except (subprocess.CalledProcessError, RuntimeError) as exc:
        if isinstance(exc, subprocess.CalledProcessError):
            print(
                f"ERROR: Release command failed with exit code {exc.returncode}.",
                file=sys.stderr,
            )
            return_code = exc.returncode or 1
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
            return_code = 1
        return return_code
    finally:
        # A failed pre-publish build must not leave pyproject.toml bumped to a version
        # that was never released. Do not roll back after a successful upload.
        if old_version and version_changed and not published:
            try:
                current_version = get_version()
                if current_version != old_version:
                    print(
                        f"Restoring project version from {current_version} to {old_version} "
                        "because the release was not published."
                    )
                    run_poetry("version", old_version)
            except subprocess.CalledProcessError:
                print(
                    "WARNING: Could not restore the pre-release project version automatically.",
                    file=sys.stderr,
                )


if __name__ == "__main__":
    raise SystemExit(main())
