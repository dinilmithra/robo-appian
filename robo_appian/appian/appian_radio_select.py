"""Appian radio-group component abstraction."""

from __future__ import annotations

from robo_appian.errors import RoboAppianError

from typing import TYPE_CHECKING

from playwright.sync_api import Locator, expect

from robo_appian.utils.ComponentUtils import ComponentUtils

from .appian_input_component import AppianInputComponent

if TYPE_CHECKING:
    from .appian_locator import AppianLocator
    from .appian_page import AppianPage


class AppianRadioSelect(AppianInputComponent):
    """Represent an Appian labeled radio group.

    Appian radio groups are resolved semantically: the visible field label's
    ``id`` is referenced by ``role="radiogroup"`` through ``aria-labelledby``.
    Options are then resolved *inside that group* by native radio ``value``.
    This prevents duplicate values such as Yes/No in unrelated groups from
    being selected accidentally.
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
            raise ValueError("Radio-group label cannot be empty or whitespace.")
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

    def _label_locator(self) -> Locator:
        """Resolve the semantic field-label element by its normalized text."""
        comparison = self._label_comparison()
        return self._root_locator(f"xpath=(.//*[@id and ({comparison})])[1]")

    def _radio_group_locator(self) -> Locator | None:
        """Resolve a radiogroup linked to this field label when one exists.

        Some Appian radio groups expose a semantic field label whose ``id`` is
        referenced by ``aria-labelledby``. Others render nearby presentation
        text without using that text as the group's accessible label. Avoid a
        long runtime auto-wait for the latter by checking locator count
        before reading the label id.
        """
        indexed = getattr(self, "_indexed_locator", None)
        if indexed is not None:
            return indexed

        label = self._label_locator()
        if label.count() == 0:
            return None
        label_id = label.get_attribute("id")
        if not label_id:
            return None
        label_id_literal = self._xpath_literal(label_id)
        group = self._root_locator(
            f"xpath=(.//*[@role='radiogroup' and @aria-labelledby={label_id_literal}])[1]"
        )
        if self._visible is not None:
            if self._visible is not None:
                group = group.filter(visible=self._visible)
            group = group.first
        return group if group.count() else None

    def _radio_locator(self, value: str) -> Locator:
        choice = str(value or "").strip()
        if not choice:
            raise ValueError("Radio-group value cannot be empty or whitespace.")
        value_literal = self._xpath_literal(choice)

        group = self._radio_group_locator()
        if group is not None:
            return group.locator(
                f"xpath=.//input[@type='radio' and @value={value_literal}]"
            ).first

        # Fallback for Appian groups whose presentation heading is not wired to
        # the radiogroup through aria-labelledby.
        # The legacy RadioSelect helper waited for the visible option label before
        # resolving its radio. Keep that behavior here: Locator.count() is an
        # immediate snapshot and can return 0 while Appian is still rerendering
        # the next wizard step.
        option_text = self._xpath_literal(choice)
        labels = self._root_locator(
            "xpath=.//label[@for and normalize-space(string(.))=" + option_text + "]"
        )
        if self._visible is not None:
            labels = labels.filter(visible=self._visible)
        option_label = labels.first
        expect(
            option_label,
            f"Visible radio option '{choice}' was not found for Appian field '{self._label}'.",
        ).to_be_visible(**self._timeout_kwargs())

        # Once the live label has appeared, reject ambiguous global matches.
        label_count = labels.count()
        if label_count != 1:
            raise RoboAppianError(
                f"Could not resolve Appian radio group '{self._label}' by semantic label, "
                f"and visible option '{choice}' matched {label_count} labels in the current scope."
            )

        # Appian renders the native radio immediately before its associated label.
        # Resolve through that live sibling relationship instead of caching a
        # transient dynamic id across a SAIL rerender.
        radio = option_label.locator("xpath=preceding-sibling::input[@type='radio'][1]")
        expect(
            radio, f"Radio input linked to visible option '{choice}' was not found."
        ).to_be_attached(**self._timeout_kwargs())
        return radio

    def _radio_label_locator(self, target: Locator) -> Locator:
        """Resolve the native label associated with a radio input.

        Appian visually places the radio label over the native input, so a
        the runtime ``check()`` on the input can time out because the label
        intercepts pointer events. Activating the associated ``label[for]``
        mirrors the user interaction while retaining semantic scoping.
        """
        target_id = target.get_attribute("id")
        if not target_id:
            raise RoboAppianError(
                f"Appian radio option in '{self._label}' does not have an id attribute."
            )
        target_id_literal = self._xpath_literal(target_id)
        group = target.locator("xpath=ancestor::*[@role='radiogroup'][1]")
        if group.count():
            return group.locator(f"xpath=.//label[@for={target_id_literal}]").first
        return self._root_locator(f"xpath=.//label[@for={target_id_literal}]").first

    def is_selected(self, value: str) -> bool:
        """Return whether the requested radio option is selected."""
        return self._radio_locator(value).is_checked()

    def select(self, value: str) -> "AppianRadioSelect":
        """Idempotently select a radio option inside this labeled group."""
        target = self._radio_locator(value)
        description = f"'{self._label}' value '{value}'"
        if target.is_checked():
            return self

        expect(
            target, f"Appian radio field {description} was not found."
        ).to_be_attached(**self._timeout_kwargs())
        target.scroll_into_view_if_needed()
        self._radio_label_locator(target).click(**self._timeout_kwargs())

        # Appian can re-render the control after the action, so resolve it again.
        target = self._radio_locator(value)
        expect(
            target,
            f"Appian radio field {description} did not become selected.",
        ).to_be_checked(checked=True, **self._timeout_kwargs())
        self._after_change(target)
        self._page.wait_for_appian_action_completed()
        return self


__all__ = ["AppianRadioSelect"]
