"""Generic helpers for validating and interacting with modal/popup content."""

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from robo_automation import Scope
from robo_appian.components.Button import Button


class Popup:
    """Complete required or conditional actions in Appian dialogs."""

    @staticmethod
    def click(scope: Scope, expected_text: str, action_label: str) -> bool:
        """Complete an action in a required dialog and wait for it to close.

        Args:
            scope: Appian scope expected to show the dialog.
            expected_text: Text fragment that identifies the dialog.
            action_label: Visible dialog button label to click.

        Returns:
            bool: ``True`` after the dialog action completes and the dialog is hidden.
        """
        dialog = scope.get_by_role("dialog").filter(has_text=expected_text)
        dialog.wait_for(state="visible")
        Button.click(dialog, action_label)
        dialog.wait_for(state="hidden")
        return True

    @staticmethod
    def click_if_present(
        scope: Scope,
        expected_text: str,
        action_label: str,
        timeout_ms: int = None,
    ) -> bool:
        """Click an action in a matching dialog only when the dialog appears.

        Use this for a conditional confirmation dialog. ``expected_text`` is a
        substring filter. Playwright waits up to the caller-supplied timeout and,
        when the dialog appears, returns only after the action closes it.

        Args:
            scope: Appian scope that may show the dialog.
            expected_text: Text fragment that identifies the dialog.
            action_label: Visible dialog button label to click.
            timeout_ms: Positive maximum time to wait for the optional dialog.

        Returns:
            bool: ``True`` when the dialog was completed; ``False`` when it did not
            appear within the supplied timeout.

        Raises:
            ValueError: If ``timeout_ms`` is missing or not positive.
        """
        if timeout_ms is None:
            raise ValueError("timeout_ms must be provided by the calling function.")
        if timeout_ms <= 0:
            raise ValueError("timeout_ms must be greater than zero.")

        dialog = scope.get_by_role("dialog").filter(has_text=expected_text)

        try:
            dialog.wait_for(state="visible", timeout=timeout_ms)
        except PlaywrightTimeoutError:
            return False

        Button.click(dialog, action_label)
        dialog.wait_for(state="hidden")
        return True
