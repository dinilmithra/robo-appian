"""Generic helpers for scoped interaction with named UI regions and labeled values."""

import re

from playwright.sync_api import Locator, Page, expect


class Region:
    """Generic helpers for interacting with semantically named page regions."""

    @staticmethod
    def get(
        page: Page,
        accessible_name: str,
        exact: bool = True,
    ) -> Locator:
        """Return the first visible semantic region identified by its accessible name."""
        region_name = str(accessible_name or "").strip()
        if not region_name:
            raise ValueError("Region name cannot be empty or whitespace.")

        region = (
            page.get_by_role("region", name=region_name, exact=exact)
            .filter(visible=True)
            .first
        )
        expect(region, f"Region '{region_name}' was not visible.").to_be_visible()
        return region

    @staticmethod
    def get_labeled_text(
        page: Page,
        region_name: str,
        label: str,
        exact_region: bool = True,
    ) -> str:
        """
        Return the text associated with a visible inline label in a region.

        This is intended for read-only summary/detail layouts where a paragraph
        contains one or more ``Label: value`` pairs. It deliberately uses text
        and semantic region boundaries rather than CSS classes.
        """
        normalized_label = str(label or "").strip()
        if not normalized_label:
            raise ValueError("Label cannot be empty or whitespace.")
        if not normalized_label.endswith(":"):
            normalized_label = f"{normalized_label}:"

        region = Region.get(page, region_name, exact=exact_region)
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
