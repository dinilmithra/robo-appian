"""Generic helpers for reading and synchronizing repeated Appian record layouts.

These helpers operate on semantic labels and visible record content so business
components do not need to know the underlying Appian DOM structure.
"""

from typing import Optional, Sequence

from playwright.sync_api import Locator, Page, expect
from robo_appian.utils.types import Scope

from robo_appian.components.Region import Region


class RecordList:
    """
    Reusable operations for repeated Appian records inside a region.

    Appian layout details stay here so application components only provide
    semantic region/field labels and business expectations.
    """

    @staticmethod
    def _matching_blocks(
        region: Locator,
        required_texts: Sequence[str],
    ) -> Locator:
        """Return visible record blocks containing all requested label/value pairs."""
        if not required_texts:
            raise ValueError("At least one required text value must be provided.")

        normalized_texts = []
        for text in required_texts:
            normalized = str(text or "").strip()
            if not normalized:
                raise ValueError("Required record text cannot be empty.")
            normalized_texts.append(normalized)

        anchor = (
            region.locator("p")
            .filter(visible=True)
            .filter(has_text=normalized_texts[0])
        )
        blocks = anchor.locator(
            "xpath=ancestor::div[@data-testid='SideBySideItem-wrapper'][1]"
        )
        for text in normalized_texts[1:]:
            blocks = blocks.filter(has_text=text)
        return blocks

    @staticmethod
    def _record_container(label_block: Locator) -> Locator:
        """Return the repeated row/container owning an Appian label block."""
        return label_block.locator("xpath=..")

    @staticmethod
    def _adjacent_value_column(label_block: Locator) -> Locator:
        """Return the value column immediately following a label column."""
        return label_block.locator(
            "xpath=following-sibling::div" "[@data-testid='SideBySideItem-wrapper'][1]"
        )

    @staticmethod
    def count(
        scope: Scope,
        region_name: str,
        record_labels: Sequence[str],
    ) -> int:
        """Return the number of visible records in the named record region.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            region_name: Optional region name used to narrow the lookup.
            record_labels: Labels used to identify candidate records.


        Returns:
            int: The number of matching records currently available.
        """
        region = Region.get(scope, region_name)
        return RecordList._matching_blocks(region, record_labels).count()

    @staticmethod
    def latest_snapshot(
        scope: Scope,
        region_name: str,
        record_labels: Sequence[str],
    ) -> Optional[str]:
        """Return the newest visible record text, or None when the list is empty.

        The snapshot is preferable to a row count for paged lists because the
        visible row count may remain constant when a new record is prepended.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            region_name: Optional region name used to narrow the lookup.
            record_labels: Labels used to identify candidate records.


        Returns:
            Optional[str]: The latest matching record snapshot, or ``None`` when no snapshot is available.
        """
        region = Region.get(scope, region_name)
        records = RecordList._matching_blocks(region, record_labels)
        if records.count() == 0:
            return None

        container = RecordList._record_container(records.first)
        return container.inner_text().strip()

    @staticmethod
    def latest_matching_locator(
        scope: Scope,
        region_name: str,
        record_labels: Sequence[str],
        expected_texts: Sequence[str],
    ) -> Locator:
        """Return a live locator for the newest record when it matches all texts.

        The returned locator stays live across Appian rerenders. If the newest
        record changes, Playwright reevaluates ``first`` against the current DOM.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            region_name: Optional region name used to narrow the lookup.
            record_labels: Labels used to identify candidate records.
            expected_texts: Text values that must be present in the matching record.


        Returns:
            Locator: The locator for the latest matching record.
        """
        if not expected_texts:
            raise ValueError("At least one expected record text must be provided.")

        region = Region.get(scope, region_name)
        records = RecordList._matching_blocks(region, record_labels)
        container = RecordList._record_container(records.first)

        for text in expected_texts:
            normalized = str(text or "").strip()
            if not normalized:
                raise ValueError("Expected record text cannot be empty.")
            container = container.filter(has_text=normalized)

        return container

    @staticmethod
    def wait_for_latest_match(
        scope: Scope,
        region_name: str,
        record_labels: Sequence[str],
        expected_texts: Sequence[str],
    ) -> Locator:
        """Wait until the newest visible record contains all expected texts.

        The locator remains live across Appian rerenders. Playwright re-evaluates
        the newest record and its text until the expectation succeeds or the
        configured Playwright default timeout expires; no manual polling or sleeps are used.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            region_name: Optional region name used to narrow the lookup.
            record_labels: Labels used to identify candidate records.
            expected_texts: Text values that must be present in the matching record.


        Returns:
            Locator: The locator for the latest matching record after it becomes available.
        """
        if not expected_texts:
            raise ValueError("At least one expected record text must be provided.")
        normalized_expected = []
        for text in expected_texts:
            normalized = str(text or "").strip()
            if not normalized:
                raise ValueError("Expected record text cannot be empty.")
            normalized_expected.append(normalized)

        latest = RecordList.latest_matching_locator(
            scope,
            region_name,
            record_labels,
            normalized_expected,
        )

        expect(
            latest,
            f"Newest record in region '{region_name}' did not contain expected "
            f"text(s) {normalized_expected}.",
        ).to_be_visible()

        return latest

    @staticmethod
    def latest_adjacent_strong_value(
        scope: Scope,
        region_name: str,
        label_block_texts: Sequence[str],
        value_index: int,
    ) -> str:
        """Read a strong-text value from the newest adjacent value column.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            region_name: Optional region name used to narrow the lookup.
            label_block_texts: Labels used to identify the record block containing the value.
            value_index: Zero-based index of the adjacent strong value to return.


        Returns:
            str: The latest adjacent emphasized value for the requested label.
        """
        if value_index < 0:
            raise ValueError("Value index cannot be negative.")

        region = Region.get(scope, region_name)
        label_block = RecordList._matching_blocks(
            region,
            label_block_texts,
        ).first
        expect(label_block).to_be_visible()

        value_column = RecordList._adjacent_value_column(label_block)
        expect(value_column).to_be_visible()

        value = value_column.locator("strong").filter(visible=True).nth(value_index)
        expect(value).to_be_visible()
        return value.inner_text().strip()
