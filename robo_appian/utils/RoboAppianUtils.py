"""Cross-component utility helpers for the robo_appian package."""

from pathlib import Path
import tomllib


class RoboAppianUtils:
    """Common utility functions shared across robo_appian."""

    @staticmethod
    def get_version():
        """Get the version of the robo_appian package from pyproject.toml.

        Returns:
            str: Version string (e.g., "0.0.2"). Returns "0.0.0" if unable to read.
        """
        try:
            toml_path = Path(__file__).parents[2] / "pyproject.toml"
            with open(toml_path, "rb") as handle:
                data = tomllib.load(handle)
                return data.get("tool", {}).get("poetry", {}).get("version", "0.0.0")
        except Exception:
            return "0.0.0"
