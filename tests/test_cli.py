from unittest.mock import patch

import pytest

from robo_appian.cli import install_browser, main


def test_install_browser_firefox_uses_playwright_module() -> None:
    with patch("robo_appian.cli.subprocess.call", return_value=0) as call:
        assert install_browser("firefox") == 0
        command = call.call_args.args[0]
        assert command[-3:] == ["playwright", "install", "firefox"]


def test_install_browser_all_omits_browser_name() -> None:
    with patch("robo_appian.cli.subprocess.call", return_value=0) as call:
        assert install_browser("all") == 0
        command = call.call_args.args[0]
        assert command[-2:] == ["playwright", "install"]


def test_install_browser_rejects_unknown_browser() -> None:
    with pytest.raises(ValueError):
        install_browser("edge")


def test_cli_dispatches_browser_install() -> None:
    with patch("robo_appian.cli.install_browser", return_value=0) as install:
        assert main(["install-browser", "firefox"]) == 0
        install.assert_called_once_with("firefox")


def test_install_browser_without_name_installs_all() -> None:
    with patch("robo_appian.cli.subprocess.call", return_value=0) as call:
        assert install_browser() == 0
        command = call.call_args.args[0]
        assert command[-2:] == ["playwright", "install"]


def test_cli_without_browser_installs_all() -> None:
    with patch("robo_appian.cli.install_browser", return_value=0) as install:
        assert main(["install-browser"]) == 0
        install.assert_called_once_with("all")
