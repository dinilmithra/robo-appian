"""Create and validate the robo-appian local Python development environment."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VENV_DIR = PROJECT_ROOT / ".venv"
POETRY_VERSION = "2.5.1"
SUPPORTED_BROWSERS = ("all", "chromium", "firefox", "webkit")


def _run(command: list[str], *, env: dict[str, str] | None = None) -> None:
    """Run a setup command from the robo-appian project root."""
    print("> " + " ".join(command))
    subprocess.run(command, cwd=PROJECT_ROOT, env=env, check=True)


def _python_in_venv(venv_dir: Path) -> Path:
    """Return the platform-specific Python executable for a virtual environment."""
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _venv_python() -> Path:
    """Return the Python executable in robo-appian's project environment."""
    return _python_in_venv(VENV_DIR)


def _bootstrap_python() -> Path:
    """Return a Python executable outside robo-appian's managed .venv when possible."""
    base_executable = getattr(sys, "_base_executable", None)
    if base_executable:
        candidate = Path(base_executable).resolve()
        if candidate.exists():
            return candidate
    return Path(sys.executable).resolve()


def _poetry_env() -> dict[str, str]:
    """Return an environment that makes Poetry own the project-local .venv."""
    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)
    env["POETRY_VIRTUALENVS_CREATE"] = "true"
    env["POETRY_VIRTUALENVS_IN_PROJECT"] = "true"
    return env


def _lock_is_current(poetry_command: list[str], env: dict[str, str]) -> bool:
    """Return True when poetry.lock exists and matches pyproject.toml."""
    lock_file = PROJECT_ROOT / "poetry.lock"
    if not lock_file.exists():
        return False

    command = [*poetry_command, "check", "--lock"]
    print("> " + " ".join(command))
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        env=env,
        check=False,
    )
    return result.returncode == 0


def _ensure_lock_current(poetry_command: list[str], env: dict[str, str]) -> None:
    """Regenerate poetry.lock when it is missing or stale."""
    if _lock_is_current(poetry_command, env):
        print("poetry.lock is current.")
        return

    print("poetry.lock is missing or stale; regenerating it with Poetry...")
    _run([*poetry_command, "lock"], env=env)


def _activation_hint() -> str:
    """Return the activation command when run from the robo-appian project root."""
    if os.name == "nt":
        return r".\.venv\Scripts\Activate.ps1"
    return "source ./.venv/bin/activate"


def _project_version() -> str:
    """Read the Poetry-managed project version without importing robo-appian."""
    pyproject = PROJECT_ROOT / "pyproject.toml"
    in_poetry = False
    for raw_line in pyproject.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("["):
            in_poetry = line == "[tool.poetry]"
            continue
        if in_poetry and line.startswith("version"):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("Unable to determine [tool.poetry] version from pyproject.toml")


def _verify_local_install(python: Path) -> None:
    """Verify the current project is installed and resolves to this source tree."""
    expected_version = _project_version()
    verify_code = f"""
from pathlib import Path
import importlib.metadata
import robo_appian

expected_root = Path({str(PROJECT_ROOT)!r}).resolve()
source = Path(robo_appian.__file__).resolve()
version = importlib.metadata.version("robo-appian")

if version != {expected_version!r}:
    raise SystemExit(
        f"robo-appian version mismatch: installed={{version}}, expected={expected_version}"
    )
if expected_root not in source.parents:
    raise SystemExit(
        f"robo-appian is not resolving from the local project: {{source}}"
    )
print(f"Verified robo-appian {{version}} from {{source}}")
"""
    _run([str(python), "-c", verify_code])


def _verify_pytest_entry_point(python: Path) -> None:
    """Verify the installed editable package exposes the pytest11 plugin entry point."""
    verify_code = r"""
from importlib.metadata import entry_points

plugins = {ep.name: ep.value for ep in entry_points(group="pytest11")}
expected = "robo_appian.pytest_plugin"
actual = plugins.get("robo_appian")
if actual != expected:
    raise SystemExit(
        "robo-appian pytest11 entry point is missing or stale: "
        f"expected={expected!r}, actual={actual!r}. "
        "Re-run tools/setup_venv.py to refresh editable package metadata."
    )
print(f"Verified pytest11 entry point: robo_appian = {actual}")
"""
    _run([str(python), "-c", verify_code])


def _install_browser(python: Path, browser: str) -> None:
    """Provision Playwright browser binaries through the robo-appian CLI."""
    command = [str(python), "-m", "robo_appian.cli", "install-browser"]
    if browser != "all":
        command.append(browser)
    _run(command)


def _poetry_version_ok(command: list[str]) -> bool:
    """Return True when the command resolves to the pinned Poetry version."""
    try:
        result = subprocess.run(
            [*command, "--version"],
            cwd=PROJECT_ROOT,
            env=_poetry_env(),
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    output = (result.stdout or result.stderr).strip()
    return result.returncode == 0 and POETRY_VERSION in output


def _find_existing_poetry(bootstrap_python: Path) -> list[str] | None:
    """Find an existing Poetry installation without performing network access."""
    poetry_exe = shutil.which("poetry")
    if poetry_exe:
        command = [poetry_exe]
        if _poetry_version_ok(command):
            print(f"Using existing Poetry: {poetry_exe}")
            return command
        print(
            f"Ignoring Poetry on PATH because it is not version {POETRY_VERSION}: "
            f"{poetry_exe}"
        )

    command = [str(bootstrap_python), "-m", "poetry"]
    if _poetry_version_ok(command):
        print(f"Using Poetry installed for bootstrap Python: {bootstrap_python}")
        return command
    return None


def _create_poetry_bootstrap(bootstrap_dir: Path, timeout: int) -> list[str]:
    """Create an optional temporary Poetry environment outside project .venv."""
    print(f"Creating temporary Poetry bootstrap environment: {bootstrap_dir}")
    venv.EnvBuilder(with_pip=True, clear=True).create(bootstrap_dir)
    poetry_python = _python_in_venv(bootstrap_dir)
    command = [
        str(poetry_python),
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--no-input",
        "--retries",
        "1",
        "--timeout",
        str(timeout),
        f"poetry=={POETRY_VERSION}",
    ]
    print("> " + " ".join(command))
    try:
        subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            env=os.environ.copy(),
            check=True,
            timeout=max(timeout * 3, 30),
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            "Timed out while bootstrapping Poetry. Install Poetry through your approved "
            "package source and rerun setup without --bootstrap-poetry."
        ) from exc
    poetry_command = [str(poetry_python), "-m", "poetry"]
    _run([*poetry_command, "--version"])
    return poetry_command

def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse setup options."""
    parser = argparse.ArgumentParser(
        description="Create and validate the robo-appian development environment."
    )
    parser.add_argument(
        "--browser",
        choices=SUPPORTED_BROWSERS,
        help=(
            "Optionally install Playwright browser binaries after setup. "
            "Use 'all' for the full browser set."
        ),
    )
    parser.add_argument(
        "--with-docs",
        action="store_true",
        help="Install the optional documentation dependency group.",
    )
    parser.add_argument(
        "--bootstrap-poetry",
        action="store_true",
        help=(
            "Allow setup to download/install the pinned Poetry version in a temporary "
            "environment when Poetry is not already available. Disabled by default to "
            "avoid hangs behind restricted package indexes or proxies."
        ),
    )
    parser.add_argument(
        "--bootstrap-timeout",
        type=int,
        default=30,
        help="Network timeout in seconds used only with --bootstrap-poetry (default: 30).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Create .venv, synchronize dependencies, and validate robo-appian."""
    args = _parse_args(argv)

    if sys.version_info[:2] < (3, 12) or sys.version_info[:2] >= (3, 13):
        raise RuntimeError(
            "robo-appian requires Python >=3.12,<3.13. "
            f"Current interpreter is {sys.version.split()[0]}."
        )

    bootstrap_python = _bootstrap_python()
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Bootstrap Python: {bootstrap_python}")
    print(f"Python version: {sys.version.split()[0]}")

    env = _poetry_env()
    poetry_command = _find_existing_poetry(bootstrap_python)
    temp_poetry: tempfile.TemporaryDirectory[str] | None = None

    try:
        if poetry_command is None:
            if not args.bootstrap_poetry:
                raise RuntimeError(
                    f"Poetry {POETRY_VERSION} is required but was not found. "
                    "Install the pinned Poetry version through your approved package "
                    "source so 'poetry --version' succeeds, then rerun setup. "
                    "If direct package-index access is available, explicitly use "
                    "--bootstrap-poetry."
                )
            temp_poetry = tempfile.TemporaryDirectory(prefix="robo-appian-poetry-")
            bootstrap_dir = Path(temp_poetry.name) / "poetry"
            poetry_command = _create_poetry_bootstrap(
                bootstrap_dir, max(args.bootstrap_timeout, 1)
            )

        # Do not destroy a usable project environment until Poetry itself has been
        # resolved successfully. This keeps a blocked bootstrap/network operation
        # from removing an existing .venv.
        if VENV_DIR.exists():
            print(f"Removing existing virtual environment: {VENV_DIR}")
            shutil.rmtree(VENV_DIR)

        _ensure_lock_current(poetry_command, env)
        _run([*poetry_command, "env", "use", str(bootstrap_python)], env=env)

        sync_command = [*poetry_command, "sync"]
        if args.with_docs:
            sync_command.extend(["--with", "docs"])
        _run(sync_command, env=env)
    finally:
        if temp_poetry is not None:
            temp_poetry.cleanup()

    python = _venv_python()
    if not python.exists():
        raise RuntimeError(f"Poetry did not create the expected environment: {python}")

    _verify_local_install(python)
    _verify_pytest_entry_point(python)

    if args.browser:
        _install_browser(python, args.browser)

    print("\nrobo-appian virtual environment is ready.")
    print(f"Python: {python}")
    print(f"Activate: {_activation_hint()}")
    if not args.browser:
        print(
            "Browsers: not installed by setup. Run "
            "'robo-appian install-browser [firefox|chromium|webkit|all]' when needed."
        )
    print(
        "Note: robo_appian-*.dist-info in .venv is normal installation metadata for "
        "the current project. Imports are verified to resolve from the local source tree."
    )
    print(
        "Poetry is external to robo-appian/.venv; the project environment contains only "
        "project/runtime/development dependencies."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
