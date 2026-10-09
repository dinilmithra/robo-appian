"""Generic helpers for validating and interacting with modal/popup content."""

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from robo_appian.appian import AppianLocator, AppianPage, AppianScope


class Popup:
    """Complete required or conditional actions in Appian dialogs."""

    @staticmethod
    def _page(scope: AppianScope) -> AppianPage:
        """Return the owning Appian page for ``scope``."""
        if isinstance(scope, AppianPage):
            return scope
        return AppianPage.get(scope.locator.page)

    @staticmethod
    def _dialog(scope: AppianScope, expected_text: str) -> AppianLocator:
        """Return the matching dialog as an Appian locator."""
        dialog = scope.get_by_role("dialog").filter(has_text=expected_text)
        return AppianLocator.get(dialog)

    @staticmethod
    def click(scope: AppianScope, expected_text: str, action_label: str) -> bool:
        """Complete an action in a required dialog and wait for it to close."""
        dialog = Popup._dialog(scope, expected_text)
        dialog.wait_for(state="visible")
        Popup._page(scope).appian_button(name=action_label, exact=False, scope=dialog).click()
        dialog.wait_for(state="hidden")
        return True

    @staticmethod
    def click_if_present(
        scope: AppianScope,
        expected_text: str,
        action_label: str,
        timeout_ms: int = None,
    ) -> bool:
        """Click an action in a matching dialog only when the dialog appears."""
        if timeout_ms is None:
            raise ValueError("timeout_ms must be provided by the calling function.")
        if timeout_ms <= 0:
            raise ValueError("timeout_ms must be greater than zero.")

        dialog = Popup._dialog(scope, expected_text)
        try:
            dialog.wait_for(state="visible", timeout=timeout_ms)
        except PlaywrightTimeoutError:
            return False

        Popup._page(scope).appian_button(name=action_label, exact=False, scope=dialog).click()
        dialog.wait_for(state="hidden")
        return True
