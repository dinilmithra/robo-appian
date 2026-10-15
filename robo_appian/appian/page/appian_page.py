"""Appian-specific page wrapper."""

from __future__ import annotations

from pathlib import Path
import time
from collections.abc import Callable
from typing import Any, Mapping, Sequence

from playwright.sync_api import Page, expect

from robo_automation import RoboAutomationError, RoboPage

from robo_appian.errors import RoboAppianNavigationError

from ..components.appian_button import AppianButton
from ..components.appian_checkbox import AppianCheckbox
from ..components.appian_component_collection import AppianComponentCollection
from ..components.appian_date import AppianDate
from ..components.appian_dropdown import AppianDropdown
from ..components.appian_dialog import AppianDialog
from ..components.appian_radio_select import AppianRadioSelect
from ..components.appian_textbox import AppianTextbox
from ..components.appian_text import AppianText
from ..components.appian_tab import AppianTab
from ..components.appian_link import AppianLink
from ..components.appian_menu import AppianMenu
from ..locator.appian_locator import AppianLocator
from robo_appian.appian.data.appian_grid import AppianGrid
from robo_appian.appian.data.appian_dataset import AppianDataSet

class AppianPage:
    """Transparent Appian wrapper around ``RoboPage``.

    Appian-specific helpers are additive. Unknown attributes and methods are
    delegated to ``RoboPage``, which in turn delegates to underlying page.
    This preserves the complete underlying page API on an AppianPage object.
    """

    locator_class = AppianLocator

    def __init__(self, robo_page: RoboPage) -> None:
        if not isinstance(robo_page, RoboPage):
            raise TypeError("AppianPage requires a RoboPage.")
        self._robo_page = robo_page

    @classmethod
    def get(cls, page: Page | RoboPage | "AppianPage") -> "AppianPage":
        """Return an Appian wrapper around a RoboPage or underlying page."""
        if isinstance(page, cls):
            return page
        return cls(RoboPage.get(page))

    @property
    def robo_page(self) -> RoboPage:
        """Return the wrapped RoboPage."""
        return self._robo_page

    def __getattr__(self, name: str) -> Any:
        """Delegate unknown attributes through RoboPage to underlying page."""
        return getattr(self._robo_page, name)

    def __dir__(self) -> list[str]:
        """Include RoboPage and underlying page members in introspection."""
        return sorted(set(super().__dir__()) | set(dir(self._robo_page)))

    def upload(
        self,
        file_path: str | Path | Sequence[str | Path],
        *,
        label: str | None = None,
        exact: bool = True,
        visible: bool | None = None,
        timeout: float | int | None = None,
    ) -> "AppianPage":
        """Upload one or more documents.

        Args:
            file_path: File path, or a sequence of file paths, to upload.
            label: Displayed label used to identify the upload control when needed.
            exact: Whether ``label`` must match exactly. Defaults to ``True``.
            visible: ``True`` for visible controls, ``False`` for hidden controls, or
                ``None`` to consider either. Upload inputs are commonly hidden, so
                the default is ``None``.
            timeout: Maximum wait in seconds. ``None`` uses the configured timeout.

        Returns:
            AppianPage: This page, allowing fluent continuation.

        Raises:
            FileNotFoundError: If any supplied file does not exist.
            ValueError: If no files are supplied.
        """
        from robo_appian.internal.component_support import ComponentSupport

        paths = [file_path] if isinstance(file_path, (str, Path)) else list(file_path)
        if not paths:
            raise ValueError("At least one upload file is required.")

        resolved = [Path(item).expanduser().resolve() for item in paths]
        missing = [path for path in resolved if not path.is_file()]
        if missing:
            raise FileNotFoundError(f"Upload file not found at: {missing[0]}")

        if label is not None:
            control = self._robo_page._page.get_by_label(label, exact=exact)
        else:
            control = self._robo_page._page.locator("input[type='file']")
        if visible is not None:
            control = control.filter(visible=visible)
        control = control.first
        control.set_input_files(
            [str(path) for path in resolved], **ComponentSupport.timeout_kwargs(timeout)
        )
        self.wait_for_appian_action_completed(timeout=timeout)
        return self

    def wait_until(
        self,
        condition: Callable[[], bool],
        *,
        timeout: float | int | None = None,
        poll_interval: float = 0.2,
        message: str = "Expected Appian condition was not satisfied in time.",
    ) -> None:
        """Wait for a callable Appian condition without fixed sleeps in test code.

        The condition is evaluated immediately and then after short browser-managed
        polling intervals until it returns ``True`` or the timeout expires.
        ``timeout`` is expressed in seconds. Callers that need an environment-specific
        limit should pass that configured value explicitly.
        """
        if not callable(condition):
            raise TypeError("condition must be callable.")
        if isinstance(poll_interval, bool) or not isinstance(
            poll_interval, (int, float)
        ):
            raise TypeError("poll_interval must be a positive number of seconds.")
        interval = float(poll_interval)
        if interval <= 0:
            raise ValueError("poll_interval must be greater than zero.")

        from robo_appian.internal.component_support import ComponentSupport

        normalized = ComponentSupport.normalize_timeout_seconds(timeout)
        timeout_seconds = normalized if normalized is not None else 30.0
        deadline = time.monotonic() + timeout_seconds
        last_error: Exception | None = None
        while True:
            try:
                if condition():
                    return
            except (AssertionError, IndexError, LookupError, ValueError) as exc:
                last_error = exc
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                detail = f" Last observed error: {last_error}" if last_error else ""
                raise TimeoutError(message + detail)
            self._robo_page._page.wait_for_timeout(min(interval, remaining) * 1000)

    def wait_for_appian_action_completed(
        self, *, timeout: float | int | None = None
    ) -> None:
        """Wait until Appian global processing indicators are absent.

        Args:
            timeout: Maximum wait in seconds. ``None`` uses the configured
                browser/context default timeout (normally ``WAIT_TIME``).

        Raises:
            TypeError: If ``timeout`` is not a number or ``None``.
            ValueError: If ``timeout`` is not a positive finite number.
            TimeoutError: If Appian continues processing beyond the timeout.
        """
        from robo_appian.internal.component_support import ComponentSupport

        timeout_kwargs = ComponentSupport.timeout_kwargs(timeout)
        processing = self._robo_page._page.locator(
            "#appian-nprogress, #appian-working-indicator-hidden"
        )
        expect(
            processing,
            "The application continued processing longer than expected.",
        ).to_have_count(0, **timeout_kwargs)

    def same_page(self, other: object) -> bool:
        """Return whether another wrapper owns the same underlying page."""
        if isinstance(other, AppianPage):
            other = other.robo_page
        return isinstance(other, RoboPage) and self._robo_page.same_page(other)

    def same_context(self, other: object) -> bool:
        """Return whether another wrapper belongs to the same browser context."""
        if isinstance(other, AppianPage):
            other = other.robo_page
        return isinstance(other, RoboPage) and self._robo_page.same_context(other)

    def open_pages(self) -> list["AppianPage"]:
        """Return Appian wrappers for open pages in the current context."""
        return [type(self).get(page) for page in self._robo_page.open_pages()]

    def get_by_attributes(
        self,
        attributes: Mapping[str, Any],
        excat_match: bool | None = None,
    ) -> AppianLocator:
        """Return an AppianLocator found by arbitrary HTML attributes."""
        return self.locator_class.get_by_attributes(
            self._robo_page._page,
            attributes=attributes,
            excat_match=excat_match,
        )

    def get_by_id(
        self,
        element_id: str,
        excat_match: bool | None = None,
    ) -> AppianLocator:
        """Return an AppianLocator found by HTML id."""
        return self.locator_class.get_by_id(
            self._robo_page._page,
            element_id=element_id,
            excat_match=excat_match,
        )

    def goto(self, url: str, **kwargs):
        """Navigate to an Appian URL using the public Appian error boundary."""
        try:
            return self._robo_page.goto(url, **kwargs)
        except RoboAutomationError as exc:
            code = (
                "ROBO_APPIAN_NAVIGATION_ABORTED"
                if getattr(exc, "code", "") == "ROBO_NAVIGATION_ABORTED"
                else "ROBO_APPIAN_NAVIGATION_ERROR"
            )
            raise RoboAppianNavigationError(
                str(exc),
                code=code,
                details=getattr(exc, "details", None),
            ) from exc

    def reload(self, **kwargs):
        """Reload an Appian page using the public Appian error boundary."""
        try:
            return self._robo_page.reload(**kwargs)
        except RoboAutomationError as exc:
            raise RoboAppianNavigationError(
                str(exc),
                code="ROBO_APPIAN_RELOAD_ERROR",
                details=getattr(exc, "details", None),
            ) from exc

    def button(
        self,
        *,
        name: str,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianButton:
        """Return an Appian button component identified by ``name``.

        Args:
            name: Visible or accessible button name.
            exact: Whether the complete normalized button name must match.

        Returns:
            The Appian button component bound to this page.
        """
        return AppianButton(
            page=self,
            name=name,
            exact=exact,
            visible=visible,
            timeout=timeout,
        )

    def textbox(
        self,
        label: str | None = None,
        *,
        placeholder: str | None = None,
        header: str | None = None,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianTextbox:
        """Return an Appian textbox identified by label, placeholder, or header.

        Specify exactly one identifier. Header lookup binds the matching header
        text to the first supported textbox that follows it.
        """
        return AppianTextbox(
            page=self,
            label=label,
            placeholder=placeholder,
            header=header,
            exact=exact,
            visible=visible,
            timeout=timeout,
        )

    def text(
        self,
        text: str,
        *,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianText:
        """Return read-only Appian text identified by its displayed value."""
        return AppianText(
            page=self,
            text=text,
            exact=exact,
            visible=visible,
            timeout=timeout,
        )

    def dropdown(
        self,
        *,
        label: str,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianDropdown:
        """Return an Appian dropdown identified by its field label.

        Resolution follows Appian's accessibility relationships: the field
        label id is referenced by the combobox ``aria-labelledby`` attribute,
        and the combobox links to its option list through ``aria-controls``.
        """
        return AppianDropdown(
            page=self,
            label=label,
            exact=exact,
            visible=visible,
            timeout=timeout,
        )

    def checkbox(
        self,
        label: str | None = None,
        *,
        header: str | None = None,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianCheckbox:
        """Return an Appian checkbox identified by its displayed label or header."""
        target = label if label is not None else header
        if target is None:
            raise ValueError("Checkbox label or header is required.")
        return AppianCheckbox(
            page=self,
            label=target,
            exact=exact,
            visible=visible,
            timeout=timeout,
        )

    def radio(
        self,
        label: str | None = None,
        *,
        header: str | None = None,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianRadioSelect:
        """Return an Appian radio group identified by its displayed label or header."""
        target = label if label is not None else header
        if target is None:
            raise ValueError("Radio label or header is required.")
        return AppianRadioSelect(
            page=self,
            label=target,
            exact=exact,
            visible=visible,
            timeout=timeout,
        )

    def link(
        self,
        name: str | None = None,
        *,
        header: str | None = None,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianLink:
        """Return an Appian link identified by its displayed name or header."""
        target = name if name is not None else header
        if target is None:
            raise ValueError("Link name or header is required.")
        return AppianLink(
            page=self,
            name=target,
            exact=exact,
            visible=visible,
            timeout=timeout,
        )

    def menu(
        self,
        name: str,
        *,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianMenu:
        """Return an Appian menu identified by its displayed name."""
        return AppianMenu(
            self, name=name, exact=exact, visible=visible, timeout=timeout
        )

    def tab(
        self,
        *,
        name: str,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianTab:
        """Return an Appian tab identified by its visible tab name."""
        return AppianTab(
            page=self,
            name=name,
            exact=exact,
            visible=visible,
            timeout=timeout,
        )

    def grid(
        self,
        *,
        label: str | None = None,
        header: str | None = None,
        row_name: str | None = None,
        column_name: str | None = None,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianGrid:
        """Return an Appian grid identified by one or more semantic hints.

        At least one of ``label``, ``header``, ``row_name``, or
        ``column_name`` is required. ``visible=True`` selects visible tables,
        ``visible=False`` selects hidden tables, and ``visible=None`` applies
        no visibility filter so both visible and hidden matches are retained.
        """
        return AppianGrid(
            self,
            label=label,
            header=header,
            row_name=row_name,
            column_name=column_name,
            exact=exact,
            visible=visible,
            timeout=timeout,
        )

    def dataset(
        self,
        *,
        label: str | None = None,
        header: str | None = None,
        field: str | None = None,
        fields: list[str] | None = None,
        row_name: str | None = None,
        column_name: str | None = None,
        row_number: int | None = None,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianDataSet:
        """Return structured Appian grid or list data using business-visible identifiers."""
        return AppianDataSet(
            self,
            label=label,
            header=header,
            field=field,
            fields=fields,
            row_name=row_name,
            column_name=column_name,
            row_number=row_number,
            exact=exact,
            visible=visible,
            timeout=timeout,
        )

    def date(
        self,
        *,
        label: str | None = None,
        placeholder: str | None = None,
        header: str | None = None,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianDate:
        """Return an Appian date field identified by label, placeholder, or header."""
        return AppianDate(
            page=self,
            label=label,
            placeholder=placeholder,
            header=header,
            exact=exact,
            visible=visible,
            timeout=timeout,
        )

    def dialog(
        self,
        *,
        name: str | None = None,
        text: str | None = None,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianDialog:
        """Return an Appian modal dialog by accessible name or displayed text."""
        return AppianDialog(
            self, name=name, text=text, exact=exact, visible=visible, timeout=timeout
        )

    # Plural component collections use zero-based position in display order.
    @property
    def dialogs(self) -> AppianComponentCollection[AppianDialog]:
        """Access Appian modal dialogs semantically or by zero-based index."""

        def indexed(index: int) -> AppianDialog:
            return AppianDialog(self, index=index)

        return AppianComponentCollection(indexed, name="dialog")

    @property
    def buttons(self) -> AppianComponentCollection[AppianButton]:
        def indexed(index: int) -> AppianButton:
            component = AppianButton(page=self, name=f"button[{index}]")
            component._indexed_locator = (
                self.get_by_role("button").filter(visible=True).nth(index)
            )
            return component

        return AppianComponentCollection(indexed, name="button")

    @property
    def textboxes(self) -> AppianComponentCollection[AppianTextbox]:
        def indexed(index: int) -> AppianTextbox:
            component = AppianTextbox(page=self, label=f"textbox[{index}]")
            raw = self.locator(f"xpath=.//*[{component._control_predicate()}]")
            component._indexed_locator = raw.filter(visible=True).nth(index)
            return component

        return AppianComponentCollection(indexed, name="textbox")

    @property
    def dropdowns(self) -> AppianComponentCollection[AppianDropdown]:
        def indexed(index: int) -> AppianDropdown:
            component = AppianDropdown(page=self, label=f"dropdown[{index}]")
            component._indexed_locator = (
                self.locator("[role='combobox']").filter(visible=True).nth(index)
            )
            return component

        return AppianComponentCollection(indexed, name="dropdown")

    @property
    def checkboxes(self) -> AppianComponentCollection[AppianCheckbox]:
        def indexed(index: int) -> AppianCheckbox:
            component = AppianCheckbox(page=self, label=f"checkbox[{index}]")
            component._indexed_locator = (
                self.locator("input[type='checkbox']").filter(visible=True).nth(index)
            )
            return component

        return AppianComponentCollection(indexed, name="checkbox")

    @property
    def radios(self) -> AppianComponentCollection[AppianRadioSelect]:
        def indexed(index: int) -> AppianRadioSelect:
            component = AppianRadioSelect(page=self, label=f"radio[{index}]")
            groups = self.locator(
                "xpath=.//*[@role='radiogroup' or (@role='group' and .//input[@type='radio'])]"
            )
            component._indexed_locator = groups.filter(visible=True).nth(index)
            return component

        return AppianComponentCollection(indexed, name="radio")

    @property
    def links(self) -> AppianComponentCollection[AppianLink]:
        def indexed(index: int) -> AppianLink:
            component = AppianLink(page=self, name=f"link[{index}]")
            component._indexed_locator = (
                self.get_by_role("link").filter(visible=True).nth(index)
            )
            return component

        return AppianComponentCollection(indexed, name="link")

    @property
    def tabs(self) -> AppianComponentCollection[AppianTab]:
        def indexed(index: int) -> AppianTab:
            component = AppianTab(page=self, name=f"tab[{index}]")
            state = self.get_by_text(AppianTab._STATE_PATTERN)
            component._indexed_locator = (
                self.get_by_role("link")
                .filter(has=state)
                .filter(visible=True)
                .nth(index)
            )
            return component

        return AppianComponentCollection(indexed, name="tab")

    @property
    def dates(self) -> AppianComponentCollection[AppianDate]:
        def indexed(index: int) -> AppianDate:
            component = AppianDate(page=self, label=f"date[{index}]")
            component._indexed_locator = (
                self.locator(f"xpath=.//*[{component._control_predicate()}]")
                .filter(visible=True)
                .nth(index)
            )
            return component

        return AppianComponentCollection(indexed, name="date")

    @property
    def grids(self) -> AppianComponentCollection[AppianGrid]:
        def indexed(index: int) -> AppianGrid:
            component = AppianGrid(self, label=f"grid[{index}]")
            component._indexed_locator = (
                self.locator("table").filter(visible=True).nth(index)
            )
            return component

        return AppianComponentCollection(indexed, name="grid")


__all__ = ["AppianPage"]
