"""Appian dropdown component abstraction."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from playwright.sync_api import Locator, expect

from robo_appian.utils.ComponentUtils import ComponentUtils

if TYPE_CHECKING:
    from .appian_locator import AppianLocator
    from .appian_page import AppianPage

logger = logging.getLogger(__name__)


class AppianDropdown:
    """Represent an Appian dropdown identified by its field label.

    Appian renders dropdowns as ``role=combobox`` elements whose
    ``aria-labelledby`` attribute references the field label. The associated
    option list is connected through ``aria-controls``. This component relies
    on those semantic relationships rather than generated Appian CSS classes.
    """

    def __init__(
        self,
        *,
        page: "AppianPage",
        label: str,
        exact: bool = True,
        scope: "AppianLocator | None" = None,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> None:
        if not isinstance(label, str) or not label.strip():
            raise ValueError("Dropdown label cannot be empty or whitespace.")
        self._page = page
        self._label = " ".join(label.split())
        self._exact = exact
        self._scope = scope
        self._visible = ComponentUtils.normalize_visibility(visible)
        self._timeout = ComponentUtils.normalize_timeout_seconds(timeout)

    @property
    def label(self) -> str:
        """Return the field label used to identify this dropdown."""
        return self._label

    @property
    def visible(self) -> bool | None:
        """Return the visibility constraint used to resolve this dropdown."""
        return self._visible

    @property
    def timeout(self) -> float | None:
        """Return this component's timeout override in seconds, if any."""
        return self._timeout

    def _timeout_kwargs(self, timeout: float | int | None = None) -> dict[str, float]:
        effective = self._timeout if timeout is None else timeout
        return ComponentUtils.timeout_kwargs(effective)

    @staticmethod
    def _normalized_label_expression() -> str:
        return "normalize-space(translate(string(.), '\u00a0', ' '))"

    def _label_condition(self) -> str:
        """Return the semantic label predicate, tolerating Appian required marks."""
        base = self._label.rstrip()
        if base.endswith("*"):
            base = base[:-1].rstrip()

        text = self._normalized_label_expression()
        expected = ComponentUtils.xpath_literal(base)
        if not self._exact:
            return f"contains({text}, {expected})"

        required = ComponentUtils.xpath_literal(f"{base}*")
        required_spaced = ComponentUtils.xpath_literal(f"{base} *")
        return (
            f"({text} = {expected} or {text} = {required} "
            f"or {text} = {required_spaced})"
        )

    def _locator(self) -> Locator:
        """Return a live semantic locator for the matching combobox."""
        indexed = getattr(self, "_indexed_locator", None)
        if indexed is not None:
            return indexed
        raw_scope = (
            self._scope.locator
            if self._scope is not None
            else self._page.robo_page._page
        )
        condition = self._label_condition()
        xpath = (
            "xpath=.//*[@role='combobox' and @aria-labelledby = "
            f"preceding::*[@id and {condition}]/@id]"
        )
        locator = raw_scope.locator(xpath)
        if self._visible is not None:
            locator = locator.filter(visible=self._visible)
        return locator

    def _resolved_locator(self) -> Locator:
        """Return the first dropdown matching the configured visibility rule."""
        return self._locator().first

    def wait_until_visible(self, timeout: float | None = None) -> "AppianDropdown":
        """Wait until the dropdown is visible, then return this component."""
        expect(
            self._resolved_locator(),
            f"Dropdown '{self._label}' was not visible.",
        ).to_be_visible(**self._timeout_kwargs(timeout))
        return self

    def is_visible(self) -> bool:
        """Return whether a matching dropdown is currently visible."""
        return self._locator().is_visible()

    def is_disabled(self) -> bool:
        """Return whether Appian marks the dropdown disabled."""
        return self._resolved_locator().get_attribute("aria-disabled") == "true"

    def is_enabled(self, timeout: float | int | None = None) -> bool:
        """Return whether the dropdown is enabled, optionally waiting.

        With no ``timeout`` argument this is an immediate state query and does
        not inherit the component timeout or Playwright ``WAIT_TIME``. When a
        positive timeout in seconds is supplied, wait up to that duration for
        Appian to make the live combobox enabled. A timeout returns ``False``
        rather than raising.
        """
        dropdown = self._resolved_locator()
        if timeout is None:
            if dropdown.count() == 0:
                return False
            return dropdown.get_attribute("aria-disabled", timeout=0) != "true"

        timeout_kwargs = ComponentUtils.timeout_kwargs(timeout)
        try:
            expect(
                dropdown,
                f"Dropdown '{self._label}' did not become enabled.",
            ).not_to_have_attribute("aria-disabled", "true", **timeout_kwargs)
            expect(
                dropdown,
                f"Dropdown '{self._label}' did not become enabled.",
            ).to_be_enabled(**timeout_kwargs)
            return True
        except AssertionError:
            return False

    def value(self) -> str:
        """Return the current visible dropdown value."""
        dropdown = self._resolved_locator()
        expect(dropdown, f"Dropdown '{self._label}' was not rendered.").to_be_attached(
            **self._timeout_kwargs()
        )
        return " ".join(dropdown.inner_text().split())

    def is_selected(self, value: str) -> bool:
        """Return whether ``value`` is the dropdown's current selection."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Dropdown value cannot be empty or whitespace.")
        expected_value = " ".join(value.split())
        return self.value() == expected_value

    def _blur(self, dropdown: Locator | None = None) -> None:
        """Immediately move focus out of the current Appian combobox."""
        target = dropdown if dropdown is not None else self._resolved_locator()
        target.evaluate("element => element.blur()")

    def _expand(self, dropdown: Locator) -> None:
        expect(dropdown, f"Dropdown '{self._label}' was not visible.").to_be_visible(
            **self._timeout_kwargs()
        )
        expect(dropdown, f"Dropdown '{self._label}' was not enabled.").to_be_enabled(
            **self._timeout_kwargs()
        )
        expect(
            dropdown,
            f"Dropdown '{self._label}' remained aria-disabled.",
        ).not_to_have_attribute("aria-disabled", "true", **self._timeout_kwargs())
        if dropdown.get_attribute("aria-expanded") == "true":
            return
        dropdown.click(**self._timeout_kwargs())
        expect(
            dropdown,
            f"Dropdown '{self._label}' did not expand.",
        ).to_have_attribute("aria-expanded", "true", **self._timeout_kwargs())

    def _listbox(self, dropdown: Locator) -> Locator:
        """Resolve the option list linked from the combobox via aria-controls."""
        listbox_id = dropdown.get_attribute("aria-controls")
        if not listbox_id:
            raise AssertionError(
                f"Dropdown '{self._label}' does not expose aria-controls."
            )
        listbox = self._page.locator(
            "xpath=//*[@role='listbox' and @id="
            + ComponentUtils.xpath_literal(listbox_id)
            + "]"
        ).first
        expect(
            listbox,
            f"Dropdown '{self._label}' option list was not visible.",
        ).to_be_visible(**self._timeout_kwargs())
        return listbox

    def _search_input(self, dropdown: Locator, listbox: Locator) -> Locator | None:
        """Return the optional search input associated with an expanded dropdown.

        Searchable Appian dropdowns render an input whose id is based on the
        same field id used by the combobox/listbox relationship.  Resolve the
        field id semantically from ``aria-labelledby`` first, falling back to
        the listbox ``aria-labelledby`` relationship.  The returned locator is
        evaluated only after expansion, so optional search UI created during
        the Appian rerender is not frozen into an early false locator.
        """
        field_id = dropdown.get_attribute("aria-labelledby") or listbox.get_attribute(
            "aria-labelledby"
        )
        if not field_id:
            return None

        # aria-labelledby can technically contain multiple ids. Appian's
        # dropdown uses the field label id as the first/only token.
        field_id = field_id.split()[0]
        search_id = f"{field_id}_searchInput"
        search = self._page.locator(
            "xpath=//input[@id=" + ComponentUtils.xpath_literal(search_id) + "]"
        ).first
        if search.count() == 0:
            return None
        expect(
            search,
            f"Dropdown search input for '{self._label}' was not visible.",
        ).to_be_visible(**self._timeout_kwargs())
        return search

    def options(self) -> list[str]:
        """Return the currently available option labels.

        The dropdown is expanded if needed. For searchable dropdowns this
        returns the options currently rendered before any filtering.
        """
        dropdown = self._resolved_locator()
        self._expand(dropdown)
        listbox = self._listbox(dropdown)
        options = listbox.get_by_role("option")
        return [
            " ".join(options.nth(index).inner_text().split())
            for index in range(options.count())
        ]

    def select(
        self,
        value: str | int | None = None,
        *,
        search_text: str | None = None,
        index: int | str | None = None,
        exact: bool = True,
    ) -> "AppianDropdown":
        """Select an option by value or 1-based index.

        ``search_text`` optionally filters a searchable Appian dropdown before
        selecting either ``value`` or ``index``. Numeric string indexes such as
        ``"1"`` are accepted. Exactly one of ``value`` or ``index`` must be
        supplied. A positional integer value is treated as an index for backward
        compatibility.
        """
        if isinstance(value, bool):
            raise TypeError("Dropdown selection value cannot be a boolean.")

        requested: str | None = None
        positional_index: int | None = None
        if isinstance(value, int):
            positional_index = value
        elif value is not None:
            if not isinstance(value, str):
                raise TypeError("Dropdown selection value must be a string or integer.")
            requested = value

        if positional_index is not None and index is not None:
            raise ValueError("Dropdown select requires exactly one of value or index.")
        if requested is not None and index is not None:
            raise ValueError("Dropdown select requires exactly one of value or index.")
        if requested is None and positional_index is None and index is None:
            raise ValueError("Dropdown select requires exactly one of value or index.")

        selected_index: int | None = positional_index
        if index is not None:
            if isinstance(index, bool):
                raise TypeError("Dropdown option index cannot be a boolean.")
            if isinstance(index, str):
                stripped = index.strip()
                if not stripped.isdigit():
                    raise ValueError(
                        "Dropdown option index must be a positive integer."
                    )
                selected_index = int(stripped)
            elif isinstance(index, int):
                selected_index = index
            else:
                raise TypeError(
                    "Dropdown option index must be an integer or numeric string."
                )

        if requested is not None:
            if not requested.strip():
                raise ValueError("Dropdown value cannot be empty or whitespace.")
            requested = " ".join(requested.split())

        if selected_index is not None and selected_index < 1:
            raise ValueError("Dropdown option index must be 1 or greater.")

        normalized_search: str | None = None
        if search_text is not None:
            if not isinstance(search_text, str) or not search_text.strip():
                raise ValueError("Dropdown search_text cannot be empty or whitespace.")
            normalized_search = " ".join(search_text.split())

        if requested is not None and normalized_search is None:
            # Dependent Appian dropdowns can rerender from a placeholder into a
            # disabled, auto-selected value before they become editable.  When
            # a component timeout is configured, wait for either terminal
            # condition: the requested value is already selected (success), or
            # the control becomes editable (continue with an explicit select).
            # Re-resolve on every poll so Appian rerenders never leave us
            # observing a stale combobox.
            if self.is_selected(requested):
                self._blur()
                return self
            if self._timeout is not None:
                deadline = time.monotonic() + self._timeout
                while time.monotonic() < deadline:
                    current = self._resolved_locator()
                    if " ".join(current.inner_text().split()) == requested:
                        logger.info(
                            "Appian dropdown auto-selected requested value while "
                            "dependent control was loading: label='%s', value='%s'.",
                            self._label,
                            requested,
                        )
                        self._blur(current)
                        return self
                    if current.get_attribute("aria-disabled") != "true":
                        break
                    self._page.robo_page._page.wait_for_timeout(100)

        dropdown = self._resolved_locator()
        self._expand(dropdown)
        listbox = self._listbox(dropdown)

        search = self._search_input(dropdown, listbox)
        if normalized_search is not None:
            if search is None:
                raise AssertionError(
                    f"Dropdown '{self._label}' does not expose a searchable input."
                )
            search.fill(normalized_search, **self._timeout_kwargs())
        elif search is not None and requested is not None:
            search.fill(requested, **self._timeout_kwargs())

        if selected_index is not None:
            # Appian commonly renders the placeholder ``Select a Value`` as a
            # real role=option at position zero.  Public index selection is
            # intentionally based on selectable business values, so index=1
            # means the first real value rather than re-selecting the
            # placeholder.  Evaluate the live option list after expansion (and
            # after optional search filtering) because Appian can rebuild and
            # renumber the options during a rerender.
            options = listbox.get_by_role("option").filter(visible=True)
            selectable_options: list[tuple[Locator, str]] = []
            for option_index in range(options.count()):
                candidate = options.nth(option_index)
                candidate_text = " ".join(candidate.inner_text().split())
                if not candidate_text or candidate_text.casefold() == "select a value":
                    continue
                selectable_options.append((candidate, candidate_text))

            option_count = len(selectable_options)
            if selected_index > option_count:
                raise IndexError(
                    f"Dropdown option index {selected_index} is out of range for "
                    f"'{self._label}' ({option_count} selectable options)."
                )
            option, selected_text = selectable_options[selected_index - 1]
        else:
            option = (
                listbox.get_by_role("option", name=requested, exact=exact)
                .filter(visible=True)
                .first
            )
            selected_text = requested

        expect(
            option,
            f"Dropdown option '{selected_text}' was not visible for '{self._label}'.",
        ).to_be_visible(**self._timeout_kwargs())

        logger.info(
            "Before Appian dropdown selection: label='%s', value='%s'.",
            self._label,
            selected_text,
        )
        option.click(**self._timeout_kwargs())
        expect(
            listbox,
            f"Dropdown option list for '{self._label}' remained visible.",
        ).to_be_hidden(**self._timeout_kwargs())

        refreshed = self._resolved_locator()
        expect(
            refreshed,
            f"Dropdown '{self._label}' remained expanded after selection.",
        ).to_have_attribute("aria-expanded", "false", **self._timeout_kwargs())
        expect(
            refreshed,
            f"Dropdown '{self._label}' did not retain '{selected_text}'.",
        ).to_contain_text(selected_text, **self._timeout_kwargs())
        logger.info(
            "After Appian dropdown selection: label='%s', value='%s'.",
            self._label,
            selected_text,
        )
        self._blur(refreshed)
        return self


__all__ = ["AppianDropdown"]
