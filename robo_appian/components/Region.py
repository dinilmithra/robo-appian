"""Generic helpers for scoped interaction with named UI regions and labeled values."""

import re

from playwright.sync_api import Locator, expect
from robo_automation import Scope


class Region:
    """Reusable operations for named Appian regions."""

    @staticmethod
    def get(
        scope: Scope,
        accessible_name: str,
        excat_match: bool = False,
    ) -> Locator:
        """Return the first visible semantic region identified by its accessible name.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            accessible_name: Accessible name used to identify the control.
            excat_match: Whether matching must use the complete label or text.


        Returns:
            Locator: The locator for the matching Appian region.
        """
        region_name = str(accessible_name or "").strip()
        if not region_name:
            raise ValueError("Region name cannot be empty or whitespace.")

        region = (
            scope.get_by_role("region", name=region_name, exact=excat_match)
            .filter(visible=True)
            .first
        )
        expect(region, f"Region '{region_name}' was not visible.").to_be_visible()
        return region

    @staticmethod
    def get_labeled_text(
        scope: Scope,
        region_name: str,
        label: str,
        exact_region: bool = True,
    ) -> str:
        """Return the text associated with a visible inline label in a region.

        This is intended for read-only summary/detail layouts where a paragraph
        contains one or more ``Label: value`` pairs. It deliberately uses text
        and semantic region boundaries rather than CSS classes.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            region_name: Optional region name used to narrow the lookup.
            label: Visible or accessible label used to identify the control.
            exact_region: Value supplied for ``exact_region``.


        Returns:
            str: The visible text associated with the label in the region.
        """
        normalized_label = str(label or "").strip()
        if not normalized_label:
            raise ValueError("Label cannot be empty or whitespace.")
        if not normalized_label.endswith(":"):
            normalized_label = f"{normalized_label}:"

        region = Region.get(scope, region_name, excat_match=exact_region)
        label_text = (
            region.get_by_text(normalized_label, exact=False).filter(visible=True).first
        )
        expect(
            label_text,
            f"Label '{normalized_label}' was not visible in region '{region_name}'.",
        ).to_be_visible()

        paragraph = label_text.locator("xpath=ancestor-or-self::p[1]")
        expect(paragraph).to_be_visible()
        container_text = paragraph.inner_text()

        match = re.search(
            rf"{re.escape(normalized_label)}\s*(.*?)\s*"
            rf"(?=(?:[A-Za-z][A-Za-z /#.-]*:\s)|$)",
            container_text,
            re.DOTALL,
        )
        return match.group(1).strip() if match else ""
