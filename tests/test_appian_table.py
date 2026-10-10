from unittest.mock import MagicMock, PropertyMock, patch

from playwright.sync_api import Locator, Page

from robo_appian import AppianTable


def test_appian_table_is_public_component() -> None:
    from robo_appian.appian.appian_table import AppianTable as ModuleAppianTable

    assert AppianTable is ModuleAppianTable


def test_appian_table_click_link_in_cell_uses_appian_cell_link() -> None:
    page = MagicMock(spec=Page)
    cell = MagicMock(spec=Locator)
    cell.page = page
    appian_cell = MagicMock()
    link_component = MagicMock()
    appian_cell.link.return_value = link_component

    with (
        patch.object(
            AppianTable, "_AppianTable__get_cell", return_value=cell
        ) as get_cell,
        patch("robo_appian.appian.appian_table.AppianCell", return_value=appian_cell),
        patch(
            "robo_appian.appian.appian_page.AppianPage.get", return_value=MagicMock()
        ),
    ):
        AppianTable.click_link_in_cell(
            page,
            label="Requests",
            row_number=1,
            column_name="Created By",
            link_name="robo appian",
        )

    get_cell.assert_called_once_with(
        scope=page,
        label="Requests",
        header_name="",
        table_column_name=None,
        row_number=1,
        row_name="",
        column_number=None,
        column_name="Created By",
        excat_match=True,
    )
    appian_cell.link.assert_called_once_with(name="robo appian", exact=True)
    link_component.click.assert_called_once_with()


def test_appian_table_click_link_rejects_empty_name() -> None:
    page = MagicMock(spec=Page)

    try:
        AppianTable.click_link_in_cell(
            page,
            label="Requests",
            row_number=1,
            column_name="Created By",
            link_name="   ",
        )
    except ValueError as exc:
        assert str(exc) == "Link name cannot be empty or whitespace."
    else:
        raise AssertionError("Expected ValueError for blank link name")


def test_appian_table_visible_none_keeps_visible_and_hidden_matches() -> None:
    page = MagicMock(spec=Page)
    tables = MagicMock(spec=Locator)
    page.get_by_role.return_value = tables

    table = AppianTable(page, label="Requests", visible=None)

    assert table.visible is None
    assert table.locator is tables
    page.get_by_role.assert_called_once_with("table", name="Requests", exact=True)
    tables.filter.assert_not_called()


def test_appian_table_visible_true_is_default_filter() -> None:
    page = MagicMock(spec=Page)
    tables = MagicMock(spec=Locator)
    visible_tables = MagicMock(spec=Locator)
    page.get_by_role.return_value = tables
    tables.filter.return_value = visible_tables

    table = AppianTable(page, label="Requests")

    assert table.visible is True
    assert table.locator is visible_tables
    tables.filter.assert_called_once_with(visible=True)


def test_appian_table_visible_false_filters_hidden_matches() -> None:
    page = MagicMock(spec=Page)
    tables = MagicMock(spec=Locator)
    hidden_tables = MagicMock(spec=Locator)
    page.get_by_role.return_value = tables
    tables.filter.return_value = hidden_tables

    table = AppianTable(page, label="Requests", visible=False)

    assert table.visible is False
    assert table.locator is hidden_tables
    tables.filter.assert_called_once_with(visible=False)


def test_appian_table_requires_semantic_identifier() -> None:
    page = MagicMock(spec=Page)

    try:
        AppianTable(page, visible=None)
    except ValueError as exc:
        assert str(exc) == (
            "AppianTable requires at least one of: "
            "label, header_name, row_name, column_name."
        )
    else:
        raise AssertionError("Expected AppianTable to require a semantic identifier")


def test_appian_table_blank_visibility_means_no_filter() -> None:
    page = MagicMock(spec=Page)
    tables = MagicMock(spec=Locator)
    page.get_by_role.return_value = tables

    for visible in (None, "", "   "):
        table = AppianTable(page, label="Requests", visible=visible)
        assert table.visible is None
        assert table.locator is tables

    tables.filter.assert_not_called()


def test_appian_table_appian_row_scopes_row_component() -> None:
    page = MagicMock(spec=Page)
    tables = MagicMock(spec=Locator)
    visible_tables = MagicMock(spec=Locator)
    rows = MagicMock(spec=Locator)
    matching_rows = MagicMock(spec=Locator)
    visible_rows = MagicMock(spec=Locator)
    page.get_by_role.return_value = tables
    tables.filter.return_value = visible_tables
    visible_tables.locator.return_value = rows
    rows.filter.return_value = matching_rows
    matching_rows.filter.return_value = visible_rows

    table = AppianTable(page, label="Requests")
    row = table.row(name="CDRH-OCD-27-M-J501", exact=False)

    assert row.visible is True
    assert row.locator is visible_rows.first
    visible_tables.locator.assert_called_with("tbody tr")
    rows.filter.assert_called_with(has_text="CDRH-OCD-27-M-J501")
    matching_rows.filter.assert_called_with(visible=True)


def test_appian_row_blank_visibility_means_no_filter() -> None:
    page = MagicMock(spec=Page)
    tables = MagicMock(spec=Locator)
    visible_tables = MagicMock(spec=Locator)
    rows = MagicMock(spec=Locator)
    matching_rows = MagicMock(spec=Locator)
    page.get_by_role.return_value = tables
    tables.filter.return_value = visible_tables
    visible_tables.locator.return_value = rows
    rows.filter.return_value = matching_rows

    table = AppianTable(page, label="Requests")
    row = table.row(name="CDRH-OCD-27-M-J501", visible="   ", exact=False)

    assert row.visible is None
    assert row.locator is matching_rows.first
    matching_rows.filter.assert_not_called()


def test_appian_row_cell_resolves_named_column() -> None:
    page = MagicMock(spec=Page)
    table_locator = MagicMock(spec=Locator)
    visible_table = MagicMock(spec=Locator)
    rows = MagicMock(spec=Locator)
    matching_rows = MagicMock(spec=Locator)
    visible_rows = MagicMock(spec=Locator)
    row_locator = MagicMock(spec=Locator)
    cells = MagicMock(spec=Locator)
    cell = MagicMock(spec=Locator)
    visible_cell = MagicMock(spec=Locator)

    page.get_by_role.return_value = table_locator
    table_locator.filter.return_value = visible_table
    visible_table.locator.side_effect = lambda selector: (
        rows if selector == "tbody tr" else MagicMock(spec=Locator)
    )
    rows.filter.return_value = matching_rows
    matching_rows.filter.return_value = visible_rows
    visible_rows.first = row_locator
    row_locator.locator.return_value = cells
    cells.nth.return_value = cell
    cell.filter.return_value = visible_cell

    table = AppianTable(page, label="Requests")
    row = table.row(name="CDRH-OCD-27-M-J501", exact=False)

    with patch.object(table, "_column_index", return_value=15) as column_index:
        result = row.cell(column_name="Created By")

    column_index.assert_called_once_with("Created By", exact=True)
    cells.nth.assert_called_once_with(15)
    cell.filter.assert_called_once_with(visible=True)
    assert result.locator is visible_cell


def test_appian_row_cell_uses_table_column_hint_when_omitted() -> None:
    page = MagicMock(spec=Page)
    table = AppianTable(page, row_name="CDRH-OCD-27-M-J501", column_name="Created By")
    row = table.row(row_number=1)

    row_locator = MagicMock(spec=Locator)
    cells = MagicMock(spec=Locator)
    cell = MagicMock(spec=Locator)
    visible_cell = MagicMock(spec=Locator)
    row_locator.locator.return_value = cells
    cells.nth.return_value = cell
    cell.filter.return_value = visible_cell

    with (
        patch.object(table, "_column_index", return_value=3) as column_index,
        patch.object(
            type(row), "locator", new_callable=PropertyMock, return_value=row_locator
        ),
    ):
        result = row.cell()

    column_index.assert_called_once_with("Created By", exact=True)
    assert result.locator is visible_cell


def test_appian_table_appian_column_cell_resolves_row() -> None:
    page = MagicMock(spec=Page)
    table = AppianTable(page, label="Requests")
    column = table.appian_column(name="Created By")
    row = MagicMock()
    row_locator = MagicMock(spec=Locator)
    cells = MagicMock(spec=Locator)
    cell = MagicMock(spec=Locator)
    visible_cell = MagicMock(spec=Locator)
    row.locator = row_locator
    row_locator.locator.return_value = cells
    cells.nth.return_value = cell
    cell.filter.return_value = visible_cell

    with (
        patch.object(table, "row", return_value=row) as row_method,
        patch.object(table, "_column_index", return_value=15) as column_index,
    ):
        result = column.cell(row_name="CDRH-OCD-27-M-J501")

    row_method.assert_called_once_with(
        name="CDRH-OCD-27-M-J501",
        row_number=None,
        visible=None,
        exact=True,
    )
    column_index.assert_called_once_with("Created By", exact=True)
    cells.nth.assert_called_once_with(15)
    cell.filter.assert_called_once_with(visible=True)
    assert result.locator is visible_cell


def test_appian_table_appian_column_supports_number() -> None:
    page = MagicMock(spec=Page)
    table = AppianTable(page, label="Requests")
    column = table.appian_column(column_number=3, visible=None)

    assert column.visible is None
    assert column.column_index == 2


def test_appian_column_requires_name_or_number() -> None:
    page = MagicMock(spec=Page)
    table = AppianTable(page, label="Requests")

    try:
        table.appian_column()
    except ValueError as exc:
        assert str(exc) == "AppianColumn requires name or column_number."
    else:
        raise AssertionError("Expected AppianColumn to require a semantic identifier")


def test_appian_row_cell_blank_visibility_means_no_filter() -> None:
    page = MagicMock(spec=Page)
    table = AppianTable(page, label="Requests")
    row = table.row(row_number=1, visible=None)
    row_locator = MagicMock(spec=Locator)
    cells = MagicMock(spec=Locator)
    cell = MagicMock(spec=Locator)

    with patch.object(
        type(row), "locator", new_callable=PropertyMock, return_value=row_locator
    ):
        row_locator.locator.return_value = cells
        cells.nth.return_value = cell
        result = row.cell(column_number=1, visible="   ")

    cell.filter.assert_not_called()
    assert result.locator is cell


def test_appian_table_cell_uses_explicit_row_and_column() -> None:
    page = MagicMock(spec=Page)
    table = AppianTable(page, label="Requests")
    row = MagicMock()
    expected = MagicMock()
    row.cell.return_value = expected

    with patch.object(table, "row", return_value=row) as row_method:
        result = table.cell(
            row_name="CDRH-OCD-27-M-J501",
            column_name="Created By",
            visible=None,
        )

    row_method.assert_called_once_with(
        name="CDRH-OCD-27-M-J501",
        row_number=None,
        visible=None,
        exact=True,
    )
    row.cell.assert_called_once_with(
        column_name="Created By",
        column_number=None,
        visible=None,
        exact=True,
    )
    assert result is expected


def test_appian_table_cell_reuses_table_row_and_column_hints() -> None:
    page = MagicMock(spec=Page)
    table = AppianTable(
        page,
        row_name="CDRH-OCD-27-M-J501",
        column_name="Created By",
    )
    row = MagicMock()
    expected = MagicMock()
    row.cell.return_value = expected

    with patch.object(table, "row", return_value=row) as row_method:
        result = table.cell()

    row_method.assert_called_once_with(
        name="CDRH-OCD-27-M-J501",
        row_number=None,
        visible=None,
        exact=True,
    )
    row.cell.assert_called_once_with(
        column_name="Created By",
        column_number=None,
        visible=True,
        exact=True,
    )
    assert result is expected


def test_appian_table_cell_supports_one_based_numbers() -> None:
    page = MagicMock(spec=Page)
    table = AppianTable(page, label="Requests")
    row = MagicMock()
    expected = MagicMock()
    row.cell.return_value = expected

    with patch.object(table, "row", return_value=row) as row_method:
        result = table.cell(row_number=2, column_number=3)

    row_method.assert_called_once_with(
        name=None,
        row_number=2,
        visible=None,
        exact=True,
    )
    row.cell.assert_called_once_with(
        column_name=None,
        column_number=3,
        visible=True,
        exact=True,
    )
    assert result is expected


def test_appian_table_cell_requires_row_and_column_context() -> None:
    page = MagicMock(spec=Page)
    table = AppianTable(page, label="Requests")

    try:
        table.cell(column_name="Created By")
    except ValueError as exc:
        assert str(exc) == (
            "AppianAppianTable.cell requires row_name or row_number, "
            "unless the table was created with row_name."
        )
    else:
        raise AssertionError("Expected AppianAppianTable.cell to require row context")

    try:
        table.cell(row_number=1)
    except ValueError as exc:
        assert str(exc) == (
            "AppianAppianTable.cell requires column_name or column_number, "
            "unless the table was created with column_name."
        )
    else:
        raise AssertionError(
            "Expected AppianAppianTable.cell to require column context"
        )


def test_appian_row_select_clicks_resolved_row_and_waits_for_appian() -> None:
    page = MagicMock(spec=Page)
    table = AppianTable(page, label="Requests")
    row = table.row(name="CDRH-OCD-27-M-J501", exact=False)
    row_locator = MagicMock(spec=Locator)

    with (
        patch.object(
            type(row), "locator", new_callable=PropertyMock, return_value=row_locator
        ),
        patch(
            "robo_appian.appian.appian_row.ComponentUtils.wait_for_appian_action_completed"
        ) as wait_for_appian,
    ):
        result = row.select()

    row_locator.click.assert_called_once_with()
    wait_for_appian.assert_called_once_with(table.appian_page)
    assert result is row


def test_appian_table_cell_returns_appian_cell_component() -> None:
    from robo_appian import AppianCell

    page = MagicMock(spec=Page)
    table = AppianTable(page, label="Requests")
    row = MagicMock()
    row_cell = MagicMock(spec=AppianCell)

    with patch.object(table, "row", return_value=row):
        row.cell.return_value = row_cell
        result = table.cell(row_number=1, column_number=16)

    assert result is row_cell


def test_appian_cell_exposes_scoped_appian_component_factories() -> None:
    from robo_appian import (
        AppianButton,
        AppianCell,
        AppianCheckbox,
        AppianDate,
        AppianLink,
        AppianRadioSelect,
        AppianTab,
        AppianTextbox,
    )

    page = MagicMock(spec=Page)
    cell_locator = MagicMock(spec=Locator)
    cell = AppianCell(cell_locator, page=page)

    components = [
        cell.button(name="Approve"),
        cell.textbox(label="Comment"),
        cell.checkbox(label="Include"),
        cell.radio(label="Decision"),
        cell.link(name="robo appian"),
        cell.tab(name="Details"),
        cell.date(label="Date Needed By"),
    ]

    assert isinstance(components[0], AppianButton)
    assert isinstance(components[1], AppianTextbox)
    assert isinstance(components[2], AppianCheckbox)
    assert isinstance(components[3], AppianRadioSelect)
    assert isinstance(components[4], AppianLink)
    assert isinstance(components[5], AppianTab)
    assert isinstance(components[6], AppianDate)
    assert all(component._scope is cell for component in components)


def test_appian_cell_button_click_uses_cell_scope() -> None:
    from robo_appian import AppianCell

    page = MagicMock(spec=Page)
    cell_locator = MagicMock(spec=Locator)
    button_locator = MagicMock(spec=Locator)
    cell = AppianCell(cell_locator, page=page)
    button = cell.button(name="Approve")

    with patch.object(button, "_wait_until_ready_locator", return_value=button_locator):
        button.click()

    button_locator.click.assert_called_once_with()
    assert button._scope is cell


def test_appian_cell_nested_table_is_scoped_to_cell() -> None:
    from robo_appian import AppianCell

    page = MagicMock(spec=Page)
    cell_locator = MagicMock(spec=Locator)
    cell = AppianCell(cell_locator, page=page)

    nested = cell.table(label="Nested Requests", visible=None)

    assert nested._component_scope is cell
    assert nested.visible is None


def test_appian_cell_exposes_appian_dropdown() -> None:
    from unittest.mock import MagicMock

    from playwright.sync_api import Locator, Page
    from robo_automation import RoboPage
    from robo_appian import AppianCell, AppianDropdown, AppianPage

    page = MagicMock(spec=Page)
    appian_page = AppianPage(RoboPage.get(page))
    raw_cell = MagicMock(spec=Locator)
    cell = AppianCell(raw_cell, page=appian_page)

    dropdown = cell.dropdown(label="Status")
    compatibility_dropdown = cell.dropdown(label="Status")

    assert isinstance(dropdown, AppianDropdown)
    assert dropdown._scope is cell
    assert isinstance(compatibility_dropdown, AppianDropdown)
    assert compatibility_dropdown._scope is cell


def test_appian_cell_dropdown_supports_zero_based_index_without_label() -> None:
    from robo_appian import AppianCell, AppianDropdown, AppianPage
    from robo_automation import RoboPage

    page = MagicMock(spec=Page)
    appian_page = AppianPage(RoboPage.get(page))
    raw_cell = MagicMock(spec=Locator)
    comboboxes = MagicMock(spec=Locator)
    visible_comboboxes = MagicMock(spec=Locator)
    first_combobox = MagicMock(spec=Locator)
    raw_cell.locator.return_value = comboboxes
    comboboxes.filter.return_value = visible_comboboxes
    visible_comboboxes.nth.return_value = first_combobox
    first_combobox.first = first_combobox
    cell = AppianCell(raw_cell, page=appian_page)

    dropdown = cell.dropdown[0]

    assert isinstance(dropdown, AppianDropdown)
    assert dropdown._resolved_locator() is first_combobox
    raw_cell.locator.assert_called_with("[role='combobox']")
    visible_comboboxes.nth.assert_called_once_with(0)


def test_appian_cell_short_accessors_support_index_for_all_component_types() -> None:
    from robo_appian import (
        AppianButton,
        AppianCell,
        AppianCheckbox,
        AppianDate,
        AppianDropdown,
        AppianLink,
        AppianRadioSelect,
        AppianTab,
        AppianTextbox,
    )
    from robo_appian.appian.appian_table import AppianTable

    page = MagicMock(spec=Page)
    raw_cell = MagicMock(spec=Locator)
    cell = AppianCell(raw_cell, page=page)

    components = [
        cell.button[0],
        cell.textbox[0],
        cell.dropdown[0],
        cell.checkbox[0],
        cell.radio[0],
        cell.link[0],
        cell.tab[0],
        cell.date[0],
        cell.table[0],
    ]

    assert isinstance(components[0], AppianButton)
    assert isinstance(components[1], AppianTextbox)
    assert isinstance(components[2], AppianDropdown)
    assert isinstance(components[3], AppianCheckbox)
    assert isinstance(components[4], AppianRadioSelect)
    assert isinstance(components[5], AppianLink)
    assert isinstance(components[6], AppianTab)
    assert isinstance(components[7], AppianDate)
    assert isinstance(components[8], AppianTable)
    assert all(hasattr(component, "_indexed_locator") for component in components)


def test_appian_cell_short_accessors_remain_callable_semantic_factories() -> None:
    from robo_appian import AppianCell, AppianDropdown

    page = MagicMock(spec=Page)
    raw_cell = MagicMock(spec=Locator)
    cell = AppianCell(raw_cell, page=page)

    dropdown = cell.dropdown(label="CAN")

    assert isinstance(dropdown, AppianDropdown)
    assert dropdown.label == "CAN"
    assert dropdown._scope is cell


def test_appian_cell_component_accessor_rejects_negative_and_non_integer_indexes() -> (
    None
):
    import pytest
    from robo_appian import AppianCell

    page = MagicMock(spec=Page)
    raw_cell = MagicMock(spec=Locator)
    cell = AppianCell(raw_cell, page=page)

    with pytest.raises(IndexError):
        _ = cell.dropdown[-1]
    with pytest.raises(TypeError):
        _ = cell.dropdown["0"]  # type: ignore[index]
