"""Structured Appian data that may be displayed as a grid or repeated list."""

from __future__ import annotations

from playwright.sync_api import Locator
from robo_automation import Scope

from robo_appian.appian.data.appian_data import AppianData, AppianDataCollection
from robo_appian.appian.data.appian_grid import AppianGrid
from robo_appian.internal.component_support import ComponentSupport


class AppianDataSet:
    """Access business data without depending on whether Appian uses a grid or list."""

    def __init__(
        self,
        scope: Scope,
        *,
        label=None,
        header=None,
        field=None,
        fields=None,
        row_name=None,
        column_name=None,
        row_number=None,
        exact=True,
        visible=True,
        timeout=None,
    ) -> None:
        if not any((label, header, field, fields, row_name, column_name)):
            raise ValueError(
                "AppianDataSet requires label, header, field, fields, row_name, or column_name."
            )
        if row_number is not None and row_number < 1:
            raise ValueError("AppianDataSet row_number must be 1 or greater.")
        self._scope = scope
        self.label = self._norm(label)
        self.header = self._norm(header)
        self.field = self._norm(field)
        self.fields = [self._norm(v) for v in (fields or [])]
        self.row_name = self._norm(row_name)
        self.column_name = self._norm(column_name)
        self.row_number = row_number
        self.exact = exact
        self.visible = ComponentSupport.normalize_visibility(visible)
        self.timeout = ComponentSupport.normalize_timeout_seconds(timeout)

    @staticmethod
    def _norm(value):
        return None if value is None else " ".join(str(value).split())

    @property
    def locator(self) -> Locator:
        raw = ComponentSupport.unwrap_scope(self._scope)
        # A heading/label normally identifies the region containing the data.
        if self.header:
            regions = raw.get_by_role("region", name=self.header, exact=self.exact)
            if regions.count() == 0:
                heading = raw.get_by_role("heading", name=self.header, exact=self.exact)
                if heading.count() == 0:
                    heading = raw.get_by_text(self.header, exact=self.exact)
                regions = heading.locator("xpath=ancestor::*[@role='region'][1]")
            root = regions
        elif self.label:
            labelled = raw.get_by_text(self.label, exact=self.exact)
            root = labelled.locator("xpath=ancestor::*[@role='region'][1]")
            if root.count() == 0:
                root = labelled.locator("xpath=ancestor::div[1]")
        else:
            root = raw.locator("table, [role='region']")

        required = [
            v for v in [self.field, *self.fields, self.row_name, self.column_name] if v
        ]
        for text in required:
            root = root.filter(has=raw.get_by_text(text, exact=self.exact))
        if self.visible is not None:
            root = root.filter(visible=self.visible)
        return root

    @property
    def first(self) -> "AppianDataSet":
        item = self._clone()
        item._indexed_locator = self.locator.first
        return item

    def __getitem__(self, index: int) -> "AppianDataSet":
        if isinstance(index, bool) or not isinstance(index, int):
            raise TypeError("dataset index must be an integer.")
        if index < 0:
            raise IndexError("dataset index cannot be negative.")
        item = self._clone()
        item._indexed_locator = self.locator.nth(index)
        return item

    def _clone(self):
        return AppianDataSet(
            self._scope,
            label=self.label,
            header=self.header,
            field=self.field,
            fields=self.fields,
            row_name=self.row_name,
            column_name=self.column_name,
            row_number=self.row_number,
            exact=self.exact,
            visible=self.visible,
            timeout=self.timeout,
        )

    def _root(self) -> Locator:
        return getattr(self, "_indexed_locator", None) or self.locator.first

    def _grid(self) -> AppianGrid | None:
        root = self._root()
        tables = root.locator("xpath=self::table | .//table")
        if tables.count() == 0:
            return None
        grid = AppianGrid(self._scope, label="dataset-grid", visible=None)
        grid._indexed_locator = tables.first
        return grid

    def _list_rows(self) -> Locator:
        root = self._root()
        # Repeated list records can be wrapped in additional Appian sections.
        # Select only the innermost section-content containers that actually
        # contain side-by-side business data so wrappers never consume a row
        # number.
        # A repeated-list business row is a side-by-side group: it has multiple
        # *direct* child items, each containing presentation content, and at
        # least one of those items contains colon-suffixed field labels.
        # Requiring direct children is important: summary/detail sections such
        # as Basic Information contain many nested presentation fields and must
        # not be mistaken for one repeated-list row.
        record = (
            "count(./div[.//div[@role='presentation']//p]) >= 2 "
            "and ./div[.//p[substring(normalize-space(string(.)), "
            "string-length(normalize-space(.)))=':']]"
        )
        return root.locator(f"xpath=.//div[{record} and not(.//div[{record}])]")

    def row(self, *, name=None, row_number=None, visible=True, exact=True):
        """Return a row with the complete AppianRow/AppianCell API."""
        grid = self._grid()
        effective = row_number if row_number is not None else self.row_number
        if grid is not None:
            return grid.row(
                name=name, row_number=effective, visible=visible, exact=exact
            )
        from robo_appian.appian.data.appian_row import AppianRow

        # Adapt list rows through a lightweight grid-compatible locator facade.
        adapter = _ListGridAdapter(self, self._list_rows())
        return AppianRow(
            adapter, name=name, row_number=effective, visible=visible, exact=exact
        )

    def cell(self, **kwargs):
        """Use the complete grid cell API on the selected dataset row."""
        effective = kwargs.pop("row_number", None) or self.row_number
        if effective is None:
            raise ValueError(
                "AppianDataSet.cell requires row_number or dataset row_number."
            )
        return self.row(row_number=effective).cell(**kwargs)

    def data(
        self,
        *,
        field: str | None = None,
        field_number: int | None = None,
        exact: bool = True,
    ) -> AppianDataCollection[AppianData]:
        """Return matching business values in displayed row order."""
        if field is None and field_number is None:
            raise ValueError("AppianDataSet.data requires field or field_number.")
        if field_number is not None and field_number < 1:
            raise ValueError("AppianDataSet.data field_number must be 1 or greater.")
        grid = self._grid()
        rows = [self.row_number] if self.row_number else None
        items: list[AppianData] = []
        if grid is not None:
            row_numbers = rows or list(range(1, grid.row_count() + 1))
            for number in row_numbers:
                cell = grid.row(row_number=number).cell(
                    column_name=field,
                    column_number=field_number,
                    visible=None,
                    exact=exact,
                )
                items.append(AppianData(lambda c=cell: c.text, field=field))
            return AppianDataCollection(items)

        list_rows = self._list_rows()
        if list_rows.count() > 0:
            indexes = (
                [self.row_number - 1]
                if self.row_number
                else list(range(list_rows.count()))
            )
            for idx in indexes:
                row = list_rows.nth(idx)
                items.append(
                    AppianData(
                        lambda r=row, f=field, n=field_number: self._list_value(
                            r, f, n, exact
                        ),
                        field=field,
                    )
                )
            return AppianDataCollection(items)

        # A read-only summary/detail section is one logical row.  Appian commonly
        # renders several ``Label: value`` pairs inside paragraphs rather than a
        # grid.  Treat that presentation as structured data so BAs use the same
        # dataset API for summaries, repeated lists, and grids.
        if self.row_number not in (None, 1):
            return AppianDataCollection([])
        root = self._root()
        if field_number is not None:
            summary = self._summary_values(root)
            value = summary[field_number - 1][1] if field_number <= len(summary) else ""
            return AppianDataCollection([AppianData(value, field=None)])
        return AppianDataCollection(
            [
                AppianData(
                    lambda r=root, f=field, e=exact: self._summary_value(r, f or "", e),
                    field=field,
                )
            ]
        )

    @staticmethod
    def _summary_values(root: Locator) -> list[tuple[str, str]]:
        """Return visible ``Label: value`` pairs from a summary/detail region."""
        # Summary labels are rendered as inline text elements, often with several
        # label/value pairs in the same paragraph.  Read DOM siblings rather than
        # depending on CSS classes or line breaks produced by the browser.
        return root.evaluate(r"""root => {
                const clean = value => (value || '').replace(/\u00a0/g, ' ').replace(/\s+/g, ' ').trim();
                const pairs = [];
                for (const paragraph of root.querySelectorAll('p')) {
                    const children = Array.from(paragraph.childNodes);
                    for (let i = 0; i < children.length; i++) {
                        const node = children[i];
                        if (node.nodeType !== Node.ELEMENT_NODE) continue;
                        const label = clean(node.textContent);
                        if (!label.endsWith(':')) continue;
                        let value = '';
                        for (let j = i + 1; j < children.length; j++) {
                            const next = children[j];
                            if (next.nodeType === Node.ELEMENT_NODE) {
                                const text = clean(next.textContent);
                                if (text.endsWith(':')) break;
                                if (text) value += (value ? ' ' : '') + text;
                            } else if (next.nodeType === Node.TEXT_NODE) {
                                const text = clean(next.textContent);
                                if (text) value += (value ? ' ' : '') + text;
                            }
                        }
                        pairs.push([clean(label.slice(0, -1)), clean(value)]);
                    }
                }
                return pairs;
            }""")

    @classmethod
    def _summary_value(cls, root: Locator, field: str, exact: bool) -> str:
        wanted = " ".join(field.split()).rstrip(":")
        for label, value in cls._summary_values(root):
            matched = label == wanted if exact else wanted.lower() in label.lower()
            if matched:
                return value
        return ""

    @staticmethod
    def _list_value(
        row: Locator, field: str | None, field_number: int | None, exact: bool
    ) -> str:
        if field_number is not None:
            parts = [p.strip() for p in row.inner_text().splitlines() if p.strip()]
            return parts[field_number - 1] if field_number <= len(parts) else ""

        wanted = " ".join((field or "").split()).rstrip(":")
        if not wanted:
            return ""

        # Appian repeated-list records commonly render several business labels
        # (for example Action:, From Workflow Step:, From Workflow Status:) in
        # one side-by-side item and the corresponding values, in the same order,
        # in the next item.  Map those displayed lines directly instead of
        # requiring each label to exist as its own DOM text element.
        return row.evaluate(
            r"""(row, args) => {
                const wanted = (args.wanted || '').replace(/\s+/g, ' ').trim().replace(/:$/, '');
                const exact = Boolean(args.exact);
                const clean = value => (value || '')
                    .replace(/\u00a0/g, ' ')
                    .replace(/\s+/g, ' ')
                    .trim();
                const splitLines = text => (text || '')
                    .split(/\r?\n/)
                    .map(clean)
                    .filter(Boolean);
                const lines = element => {
                    const rendered = splitLines(element.innerText);
                    if (rendered.length > 1) return rendered;
                    const source = splitLines(element.textContent);
                    return source.length > rendered.length ? source : rendered;
                };
                const matches = label => {
                    const normalized = clean(label).replace(/:$/, '');
                    return exact
                        ? normalized === wanted
                        : normalized.toLowerCase().includes(wanted.toLowerCase());
                };

                const items = Array.from(
                    row.children
                ).filter(item => item.querySelector(':scope > div[role="presentation"] p'));
                for (let i = 0; i < items.length - 1; i++) {
                    const labelLines = lines(items[i]).filter(line => line.endsWith(':'));
                    const labelIndex = labelLines.findIndex(matches);
                    if (labelIndex < 0) continue;

                    const allValueLines = lines(items[i + 1]);
                    // Non-field context (for example actor name or timestamp) can
                    // share these items.  Appian keeps the business values aligned
                    // at the end of the value item, so pair the last N values with
                    // the N colon-suffixed labels.
                    const valueLines = allValueLines.slice(-labelLines.length);
                    if (labelIndex < valueLines.length) {
                        return valueLines[labelIndex];
                    }
                    return clean(items[i + 1].innerText);
                }
                return '';
            }""",
            {"wanted": wanted, "exact": exact},
        )



class _ListGridAdapter:
    """Internal adapter allowing list records to reuse AppianRow/AppianCell behavior."""

    def __init__(self, dataset: AppianDataSet, rows: Locator) -> None:
        self.dataset = dataset
        self._rows = rows
        self.appian_page = dataset._scope
        self.column_name = dataset.column_name

    @property
    def locator(self) -> Locator:
        return self._rows

    def row_locator(self, *, name=None, row_number=None, visible=True, exact=True):
        rows = self._rows
        if name is not None:
            rows = rows.filter(has_text=name)
        if visible is not None:
            rows = rows.filter(visible=visible)
        if row_number is not None:
            return rows.nth(row_number - 1)
        return rows.first

    def cell_locator(self, row, *, column_name=None, column_number=None, exact=True):
        if column_number is not None:
            # Each side-by-side value area acts as a logical cell for list data.
            cells = row.locator("xpath=./div[div[@role='presentation']]")
            return cells.nth(column_number - 1)
        labels = row.get_by_text(column_name or "", exact=exact)
        if labels.count() == 0:
            return row.locator("xpath=.//*[false()]")
        group = labels.first.locator(
            "xpath=ancestor::div[div[@role='presentation']][1]"
        )
        return group.locator(
            "xpath=following-sibling::div[div[@role='presentation']][1]"
        )

    def _column_index(self, column_name: str, *, exact: bool = True) -> int:
        raise ValueError("List-style datasets use data(field=...) for named values.")
