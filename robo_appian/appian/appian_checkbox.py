"""Appian checkbox component abstraction."""

from __future__ import annotations

from typing import TYPE_CHECKING

from playwright.sync_api import Locator, expect

from robo_appian.errors import RoboAppianError
from robo_appian.utils.ComponentUtils import ComponentUtils

from .appian_input_component import AppianInputComponent

if TYPE_CHECKING:
    from .appian_locator import AppianLocator
    from .appian_page import AppianPage


class AppianCheckbox(AppianInputComponent):
    """Represent an Appian native checkbox identified by visible label text.

    The component supports the two semantic checkbox structures used by Appian:

    * a visible ``label[for]`` linked directly to ``input[type='checkbox']``;
    * a boolean field label whose ``id`` is referenced by ``role='group'`` via
      ``aria-labelledby``.

    Generated Appian CSS classes are intentionally not used for identification.
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
            raise ValueError("Checkbox label cannot be empty or whitespace.")
        super().__init__(page=page, timeout=timeout)
        self._label = " ".join(label.split())
        self._exact = exact
        self._scope = scope
        self._visible = ComponentUtils.normalize_visibility(visible)

    @property
    def visible(self) -> bool | None:
        """Return the visibility constraint used to resolve this component."""
        return self._visible

    @staticmethod
    def _xpath_literal(value: str) -> str:
        return ComponentUtils.xpath_literal(value)

    @staticmethod
    def _normalized_xpath(expression: str) -> str:
        lowercase = "abcdefghijklmnopqrstuvwxyz"
        uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        return (
            "translate(normalize-space(translate("
            + expression
            + ", '\u00a0', ' ')), "
            + f"'{lowercase}', '{uppercase}')"
        )

    def _root_locator(self, selector: str) -> Locator:
        if self._scope is not None:
            return self._scope.locator.locator(selector)
        return self._page.locator(selector)

    def _label_comparison(self) -> str:
        normalized = self._normalized_xpath("string(.)")
        expected = self._xpath_literal(self._label.upper())
        if self._exact:
            return f"{normalized} = {expected}"
        return f"contains({normalized}, {expected})"

    def _checkbox_locator(self) -> Locator:
        """Return a live locator for either supported Appian checkbox structure.

        The locator must stay *live* while the runtime waits.  Appian often
        rerenders immediately after navigation/clicks, so probing ``count()``
        here and choosing a fallback eagerly can freeze the component to an
        empty locator before the checkbox is attached.

        Resolution therefore combines two dynamic semantic locators:

        * a checkbox whose accessible name comes from its visible choice
          ``label[for]``;
        * a checkbox inside ``role="group"`` whose ``aria-labelledby`` points
          at the requested field label (used by boolean fields such as ``IT``).

        No generated Appian CSS classes are used.
        """
        indexed = getattr(self, "_indexed_locator", None)
        if indexed is not None:
            return indexed

        if self._scope is not None:
            root = self._scope.locator
            named_checkbox = root.get_by_role(
                "checkbox",
                name=self._label,
                exact=self._exact,
            )
        else:
            named_checkbox = self._page.get_by_role(
                "checkbox",
                name=self._label,
                exact=self._exact,
            )

        comparison = self._label_comparison()
        group_checkbox = self._root_locator(
            "xpath=.//*[@role='group' and @aria-labelledby = "
            "//*[@id and (" + comparison + ")]/@id]//input[@type='checkbox']"
        )

        # ``or_`` keeps both branches live.  The runtime reevaluates them while
        # assertions/actions wait, so a checkbox added by a SAIL rerender can
        # be discovered without reconstructing the component.
        combined = named_checkbox.or_(group_checkbox)
        if self._visible is not None:
            combined = combined.filter(visible=self._visible)
        return combined.first

    def _checkbox_label_locator(self, target: Locator) -> Locator:
        """Resolve the native label associated with a checkbox input.

        Appian can visually place the associated ``label[for]`` over the native
        checkbox input. In that DOM shape the runtime ``check()``/``uncheck()``
        waits for the input to receive pointer events and eventually times out
        because the label correctly receives the click instead. Activating the
        associated native label mirrors a user click and avoids depending on
        generated Appian CSS classes.
        """
        target_id = target.get_attribute("id")
        if not target_id:
            raise RoboAppianError(
                f"Appian checkbox '{self._label}' does not have an id attribute."
            )
        target_id_literal = self._xpath_literal(target_id)
        group = target.locator("xpath=ancestor::*[@role='group'][1]")
        if group.count():
            return group.locator(f"xpath=.//label[@for={target_id_literal}]").first
        return self._root_locator(f"xpath=.//label[@for={target_id_literal}]").first

    def is_visible(self) -> bool:
        """Return whether a matching checkbox currently exists in this scope."""
        return self._checkbox_locator().count() > 0

    def is_checked(self, timeout: float | None = None) -> bool:
        """Return the checkbox's current checked state.

        Args:
            timeout: Optional timeout in seconds used only to wait for the
                checkbox to be attached.  Once present, return its current
                checked state immediately; an unchecked checkbox must not make
                this method wait for a state transition that was never requested.
        """
        checkbox = self._checkbox_locator()
        expect(checkbox, f"Checkbox '{self._label}' was not found.").to_be_attached(
            **self._timeout_kwargs(timeout)
        )
        return checkbox.is_checked()

    def _set_checked(self, desired: bool) -> "AppianCheckbox":
        checkbox = self._checkbox_locator()
        expect(checkbox, f"Checkbox '{self._label}' was not found.").to_be_attached(
            **self._timeout_kwargs()
        )

        # Idempotent in both directions: interact only when state must change.
        if checkbox.is_checked() == desired:
            return self

        checkbox.scroll_into_view_if_needed()
        label = self._checkbox_label_locator(checkbox)
        expect(
            label,
            f"Native label for Appian checkbox '{self._label}' was not found.",
        ).to_be_attached(**self._timeout_kwargs())
        label.click(**self._timeout_kwargs())

        # Appian can replace the control during a SAIL rerender.
        checkbox = self._checkbox_locator()
        expect(
            checkbox,
            f"Checkbox '{self._label}' did not reach checked={desired}.",
        ).to_be_checked(checked=desired, **self._timeout_kwargs())
        self._after_change(checkbox)
        ComponentUtils.wait_for_appian_action_completed(self._page)
        return self

    def check(self) -> "AppianCheckbox":
        """Check the checkbox only when it is currently unchecked."""
        return self._set_checked(True)

    def uncheck(self) -> "AppianCheckbox":
        """Uncheck the checkbox only when it is currently checked."""
        return self._set_checked(False)

    def set_checked(self, checked: bool) -> "AppianCheckbox":
        """Set the checkbox to ``checked`` using idempotent state handling."""
        return self._set_checked(bool(checked))

    def select(self, selected: bool = True) -> "AppianCheckbox":
        """Compatibility alias for ``set_checked(selected)``."""
        return self.set_checked(selected)


__all__ = ["AppianCheckbox"]
