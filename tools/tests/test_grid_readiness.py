"""Exercise the actual grid and page factory against a delayed table view."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

PROJECT = Path(__file__).resolve().parents[2]


def compile_nodes(path, names, namespace):
    tree = ast.parse(path.read_text())
    selected = [n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and n.name in names]
    future = ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[future, *selected], type_ignores=[])), str(path), "exec"), namespace)


class TableView:
    """Live table lookup: filtered views observe changes made by an assertion."""
    def __init__(self, dom, predicates=()):
        self.dom, self.predicates = dom, predicates

    def get_by_role(self, role, *, name=None, exact=True):
        return TableView(self.dom, self.predicates + (lambda t: role == "table" and (name is None or (t["name"] == name if exact else name in t["name"])),))

    def filter(self, *, visible=None, has=None):
        return TableView(self.dom, self.predicates + (() if visible is None else (lambda t: t["visible"] == visible,)))

    @property
    def first(self):
        return self

    def matches(self):
        return [t for t in self.dom.tables if t["attached"] and all(p(t) for p in self.predicates)]

    def is_visible(self):
        return bool(self.matches() and self.matches()[0]["visible"])


class DOM(TableView):
    def __init__(self, *, visible=True, delayed=True, missing=False):
        self.tables = [] if delayed else [{"name": "Funding Lines", "attached": True, "visible": visible}]
        self.pending = None if missing else {"name": "Funding Lines", "attached": True, "visible": visible}
        self.waits = []
        super().__init__(self)

    def render(self):
        if self.pending is not None and not self.tables:
            self.tables.append(self.pending)


class Expect:
    def __init__(self, view, message=""):
        self.view, self.message = view, message

    def check(self, kind, kwargs):
        self.view.dom.waits.append((kind, kwargs))
        self.view.dom.render()
        ready = self.view.is_visible() if kind == "visible" else bool(self.view.matches())
        if not ready:
            raise AssertionError(self.message)

    def to_be_visible(self, **kwargs): self.check("visible", kwargs)
    def to_be_attached(self, **kwargs): self.check("attached", kwargs)


def normalize_visible(value):
    if isinstance(value, str):
        return {"true": True, "false": False, "none": None}[value.lower()]
    return value


def normalize_timeout(value):
    if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0):
        raise ValueError("timeout must be positive")
    return value


def components():
    ns = {"expect": Expect, "ComponentSupport": SimpleNamespace(
        normalize_visibility=normalize_visible,
        normalize_timeout_seconds=normalize_timeout,
        timeout_kwargs=lambda value: {} if value is None else {"timeout": normalize_timeout(value) * 1000},
        unwrap_scope=lambda page: page.dom,
    )}
    compile_nodes(PROJECT / "robo_appian/appian/data/appian_grid.py", {"AppianGrid"}, ns)
    path = PROJECT / "robo_appian/appian/page/appian_page.py"
    tree = ast.parse(path.read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "AppianPage")
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "grid")
    future = ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[future, fn], type_ignores=[])), str(path), "exec"), ns)
    class Page:
        grid = ns["grid"]
        def __init__(self, dom): self.dom = dom
    return Page, ns["AppianGrid"]


Page, Grid = components()


class GridReadinessTests(unittest.TestCase):
    def test_default_factory_waits_for_delayed_visible_table(self):
        dom = DOM()
        self.assertEqual(dom.tables, [])
        grid = Page(dom).grid(label="Funding Lines")
        self.assertIsInstance(grid, Grid)
        self.assertTrue(grid.is_visible())
        self.assertEqual(dom.waits, [("visible", {})])

    def test_optional_probe_does_not_wait_or_force_rendering(self):
        dom = DOM()
        grid = Page(dom).grid(label="Funding Lines", wait=False)
        self.assertFalse(grid.is_visible())
        self.assertEqual(dom.tables, [])
        self.assertEqual(dom.waits, [])
        self.assertIs(grid.wait_until_visible(), grid)
        self.assertTrue(grid.is_visible())

    def test_hidden_grid_waits_for_an_attached_hidden_match(self):
        dom = DOM(visible=False)
        grid = Page(dom).grid(label="Funding Lines", visible=False)
        self.assertFalse(grid.is_visible())
        self.assertEqual(len(grid.locator.matches()), 1)
        self.assertEqual(dom.waits, [("attached", {})])

    def test_unfiltered_grid_can_be_attached_and_hidden(self):
        dom = DOM(visible=False)
        grid = Page(dom).grid(label="Funding Lines", visible=None)
        self.assertEqual(len(grid.locator.matches()), 1)
        self.assertEqual(dom.waits, [("attached", {})])

    def test_missing_table_does_not_satisfy_any_visibility_mode(self):
        for visible in (True, False, None):
            with self.subTest(visible=visible), self.assertRaises(AssertionError):
                Page(DOM(missing=True)).grid(label="Funding Lines", visible=visible)

    def test_seconds_override_is_used_for_visible_and_hidden_waits(self):
        for visible, kind in ((True, "visible"), (False, "attached"), (None, "attached")):
            with self.subTest(visible=visible):
                dom = DOM(visible=visible is True)
                Page(dom).grid(label="Funding Lines", visible=visible, timeout=8)
                self.assertEqual(dom.waits, [(kind, {"timeout": 8000})])

    def test_per_call_wait_override_preserves_component_timeout(self):
        dom = DOM()
        grid = Page(dom).grid(label="Funding Lines", timeout=8, wait=False)
        grid.wait_until_ready(timeout=2)
        self.assertEqual(dom.waits, [("visible", {"timeout": 2000})])
        self.assertEqual(grid.timeout, 8)

    def test_string_visibility_keeps_previous_normalization(self):
        dom = DOM(visible=False)
        grid = Page(dom).grid(label="Funding Lines", visible="false")
        self.assertIs(grid.visible, False)
        self.assertEqual(dom.waits, [("attached", {})])

    def test_factory_retains_all_identifiers_and_matching_options(self):
        page = Page(DOM())
        grid = page.grid(label=" Funding Lines ", header=" Parent header ", row_name=" Item 1001 ", column_name=" Status ", exact=False, visible=None, timeout=8, wait=False)
        self.assertEqual((grid._component_label, grid._component_header, grid.row_name, grid.column_name), ("Funding Lines", "Parent header", "Item 1001", "Status"))
        self.assertFalse(grid._component_exact)
        self.assertIsNone(grid.visible)
        self.assertEqual(grid.timeout, 8)
        self.assertIs(grid.appian_page, page)

    def test_cell_supports_named_numbered_and_default_table_identifiers(self):
        grid = Page(DOM()).grid(row_name="Item 1001", column_name="Status", wait=False)
        row = Mock()
        grid.row = Mock(return_value=row)
        grid.cell()
        grid.row.assert_called_with(name="Item 1001", row_number=None, visible=None, exact=True)
        row.cell.assert_called_with(column_name="Status", column_number=None, visible=True, exact=True)
        grid.cell(row_number=2, column_number=3, visible=None, exact=False)
        grid.row.assert_called_with(name=None, row_number=2, visible=None, exact=False)
        row.cell.assert_called_with(column_name=None, column_number=3, visible=None, exact=False)

    def test_column_forwards_existing_table_options(self):
        grid = Page(DOM()).grid(label="Funding Lines", wait=False)
        grid.appian_column = Mock()
        grid.column(name="Status", column_number=2, visible=None, exact=False)
        grid.appian_column.assert_called_once_with(name="Status", column_number=2, visible=None, exact=False)

    def test_no_identifier_and_invalid_options_still_fail(self):
        page = Page(DOM())
        for kwargs in ({}, {"label": " "}, {"label": "Funding Lines", "timeout": -1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                page.grid(**kwargs)
        with self.assertRaises(TypeError):
            page.grid(label="Funding Lines", wait="false")


if __name__ == "__main__":
    unittest.main()
