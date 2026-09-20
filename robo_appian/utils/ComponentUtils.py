"""Shared low-level helpers used by robo_appian UI components."""

import logging
from pathlib import Path
from typing import Optional

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import (
    Locator,
    Page,
    TimeoutError as PlaywrightTimeoutError,
    expect,
)
from robo_appian.utils.types import Scope

logger = logging.getLogger(__name__)


class ComponentUtils:
    """Provide low-level Playwright operations shared by Appian components."""

    @staticmethod
    def xpath_literal(value: str) -> str:
        """Quote arbitrary text for insertion into an XPath expression.

        Args:
            value: Text that may contain single or double quotes.

        Returns:
            A valid XPath literal or ``concat`` expression.
        """
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'

        parts = value.split("'")
        return "concat(" + ', "\'", '.join(f"'{part}'" for part in parts) + ")"

    @staticmethod
    def click(locator: Locator) -> None:
        """Click a visible, enabled locator and log the dispatched interaction.

        Playwright's actionability checks determine when the target is ready. The
        method logs immediately before dispatch and after ``click()`` returns so
        failures can distinguish a click that never became actionable from one
        that Playwright successfully dispatched. One force-click recovery is
        retained only for the existing pointer-interception case.

        Args:
            locator: Resolved element or element collection to filter by visibility.
        """
        visible_locator = locator.filter(visible=True)

        expect(visible_locator).to_be_visible()
        expect(visible_locator).to_be_enabled()

        logger.info("Click target ready; dispatching Playwright click.")

        try:
            visible_locator.click()
        except PlaywrightError as exc:
            message = str(exc).lower()
            if "intercepts pointer events" not in message:
                logger.exception("Playwright click failed before completion.")
                raise

            logger.warning(
                "Click intercepted by overlapping element; retrying once with force click."
            )
            expect(visible_locator).to_be_visible()
            expect(visible_locator).to_be_enabled()
            visible_locator.click(force=True)
            logger.info("Forced Playwright click completed after pointer interception.")
            return

        logger.info("Playwright click completed successfully.")

    @staticmethod
    def click_by_text(page: Page, text: str, exact: bool = True) -> None:
        """Click the first visible element whose text matches the requested text.

        Use this only when the visible text identifies the clickable element
        itself. Duplicate matches are resolved by choosing the first visible one.

        Args:
            page: Appian page containing the target text.
            text: Text to locate.
            exact: Whether the element text must match exactly.
        """
        link = page.get_by_text(text, exact=exact).filter(visible=True).first
        expect(link).to_be_visible()
        link.click()

    @staticmethod
    def click_by_title(page: Page, title: str) -> None:
        """Click the first visible element with the requested title attribute.

        Args:
            page: Appian page containing the titled element.
            title: Title attribute value to locate.
        """
        link = page.get_by_title(title).filter(visible=True).first
        expect(link).to_be_visible()
        link.click()

    @staticmethod
    def click_by_id(page: Page, button_id: str) -> None:
        """Click the first visible, enabled element with an exact HTML ID.

        Args:
            page: Appian page containing the element.
            button_id: Literal HTML ID, including IDs that begin with numbers.
        """
        locator = page.locator(f'[id="{button_id}"]:not([disabled])')
        active_locator = locator.filter(visible=True).first
        expect(active_locator).to_be_visible()
        active_locator.click()

    @staticmethod
    def wait_for_appian_action_completed(scope: Scope) -> None:
        """Wait until Appian global processing indicators are absent.

        A short Playwright wait is used only to detect whether Appian starts a
        processing cycle. Once processing is detected, the completion assertion
        uses the configured Playwright expectation timeout.

        Args:
            scope: Appian page or locator associated with the triggered action.
        """
        logger.info("Appian processing check started.")

        processing = scope.locator(
            "#appian-nprogress, #appian-working-indicator-hidden"
        )

        try:
            processing.first.wait_for(
                state="attached",
                timeout=2_000,
            )
        except PlaywrightTimeoutError:
            logger.info("No Appian global processing indicator was detected.")
            return

        expect(
            processing,
            "The application continued processing longer than expected.",
        ).to_have_count(0)

        logger.info(
            "Appian processing completed: global processing indicators absent."
        )

    @staticmethod
    def wait_until_visible(scope: Scope, message: str = None) -> None:
        """Wait until a page or locator is visible.

        Args:
            scope: Page or locator expected to become visible.
            message: Optional assertion message used when the wait fails.
        """
        expect(scope, message).to_be_visible()

    @staticmethod
    def wait_until_hidden(scope: Scope) -> None:
        """Wait until a page or locator is hidden or detached.

        Args:
            scope: Page or locator expected to become hidden.
        """
        expect(scope).to_be_hidden()

    @staticmethod
    def tab(page: Page, occurrence: Optional[int] = None) -> None:
        """Move keyboard focus forward on the supplied page.

        Use this to trigger Appian focus-out behavior after editing a control.
        When ``occurrence`` is omitted, Tab is pressed once.

        Args:
            page: Page receiving the keyboard event.
            occurrence: Optional number of Tab key presses. Defaults to 1 when
                omitted.

        Raises:
            ValueError: If occurrence is provided and is not a positive integer.
        """
        if occurrence is None:
            occurrence = 1
        elif isinstance(occurrence, bool) or not isinstance(occurrence, int) or occurrence < 1:
            raise ValueError("Tab occurrence must be a positive integer.")

        for _ in range(occurrence):
            page.keyboard.press("Tab")

    @staticmethod
    def upload_document(
        page: Page,
        directory_path: str,
        file_name: str,
    ) -> str:
        """Set a local file on the first Appian upload input.

        The path is expanded and resolved from ``directory_path`` plus
        ``file_name``. The standard multiple-file widget is preferred; otherwise
        the first generic file input is used.

        Args:
            page: Appian page containing a file upload control.
            directory_path: Local directory containing the upload file.
            file_name: File name relative to ``directory_path``.

        Returns:
            Absolute path of the file supplied to the browser.

        Raises:
            FileNotFoundError: If the resolved local file does not exist.
        """
        resolved_path = Path(directory_path, file_name).expanduser().resolve()
        if not resolved_path.is_file():
            raise FileNotFoundError(f"Upload file not found at: {resolved_path}")

        widget_input = page.locator(
            "div.MultipleFileUploadWidget---upload_field input[type='file']"
        )
        if widget_input.count() > 0:
            widget_input.first.set_input_files(str(resolved_path))
        else:
            page.locator("input[type='file']").first.set_input_files(str(resolved_path))

        return str(resolved_path)

    @staticmethod
    def wait_for_text_visible(page: Page, text: str) -> None:
        """
        Waits for an exact text string to become visible.

        Timeout is inherited from the Playwright default configured by
        conftest.py.
        """
        logger.info("Waiting for text '%s' to be visible...", text)
        text_locator = page.get_by_text(text, exact=True).filter(visible=True).first

        try:
            text_locator.wait_for(state="visible")
            logger.info("Text '%s' is loaded and visible.", text)
        except PlaywrightTimeoutError:
            logger.error("Timeout: Text '%s' did not become visible.", text)
            raise

    @staticmethod
    def find_container(page: Page, field_label: str, header_text: str) -> Locator:
        """Build a locator for a region containing a heading and field label.

        Use this to scope duplicate fields to a semantic region. The returned
        locator is not awaited or validated; the caller owns visibility checks.

        Args:
            page: Appian page containing the region.
            field_label: Visible field text required inside the region.
            header_text: Visible text whose ancestor region is selected.

        Returns:
            A live locator for the nearest matching region.
        """
        xpath = (
            f"//*[normalize-space()='{header_text}']"
            f"/ancestor::*[@role='region']"
            f"[.//*[normalize-space()='{field_label}']][1]"
        )
        return page.locator(f"xpath={xpath}")

    @staticmethod
    def find_locator_by_xpath(page: Page, xpath: str) -> Locator:
        """Build a locator using an XPath expression.

        Args:
            page: Appian page containing the element.
            xpath: XPath expression to locate the element.

        Returns:
            A live locator for the element matching the XPath.
        """
        locator = page.locator(f"xpath={xpath}").filter(visible=True).first
        return locator

    @staticmethod
    def wait_and_find_locator_by_xpath(page: Page, xpath: str) -> Locator:
        """Build a locator using an XPath expression.

        Args:
            page: Appian page containing the element.
            xpath: XPath expression to locate the element.

        Returns:
            A live locator for the element matching the XPath.
        """
        locator = ComponentUtils.find_locator_by_xpath(page, xpath)
        expect(locator).to_be_visible()
        return locator
