"""Menu contract tests with DOM-like locators; no live browser needed."""
import ast
from html.parser import HTMLParser
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

SOURCE = Path(__file__).resolve().parents[2] / "robo_appian/appian/components/appian_menu.py"


class BrowserTimeout(TimeoutError):
    pass


class Node:
    def __init__(self, role, name, text="", *, children=(), attrs=None, visible=True):
        self.role, self.name, self.text = role, name, text
        self.children, self.attrs = list(children), attrs or {}
        self.visible, self.clicks = visible, 0
        self.on_click = None


class Locator:
    def __init__(self, nodes=()):
        self.nodes = list(nodes)

    @classmethod
    def get(cls, raw):
        return SimpleNamespace(raw_page=raw)

    def get_by_role(self, role, *, name=None, exact=True):
        def descendants(node):
            for child in node.children:
                yield child
                yield from descendants(child)
        return Locator(n for root in self.nodes for n in descendants(root)
                       if n.role == role and (name is None or (n.name == name if exact else name in n.name)))

    def filter(self, *, visible=None, has_text=None):
        return Locator(n for n in self.nodes if (visible is None or n.visible == visible)
                       and (has_text is None or has_text in n.text))

    def or_(self, other):
        return Locator(list(dict.fromkeys([*self.nodes, *other.nodes])))

    @property
    def first(self):
        return Locator(self.nodes[:1])

    def nth(self, i):
        return Locator(self.nodes[i:i+1])

    def is_visible(self):
        return bool(self.nodes and self.nodes[0].visible)

    def count(self):
        return len(self.nodes)

    def get_attribute(self, name):
        return self.nodes[0].attrs.get(name)

    def inner_text(self):
        return self.nodes[0].text

    def click(self):
        node = self.nodes[0]
        if node.on_click:
            node.on_click()
        node.clicks += 1


class Expect:
    calls = []

    def __init__(self, locator):
        self.locator = locator

    def to_be_visible(self, **kwargs):
        self.calls.append(kwargs)
        if not self.locator.nodes or not self.locator.nodes[0].visible:
            raise BrowserTimeout("not visible")

    def to_have_attribute(self, name, value, **kwargs):
        self.calls.append(kwargs)
        if self.locator.get_attribute(name) != value:
            raise BrowserTimeout("attribute did not change")


def load_menu():
    tree = ast.parse(SOURCE.read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef))
    ns = {"expect": Expect, "Page": object, "Locator": Locator,
          "ComponentSupport": SimpleNamespace(
              normalize_visibility=lambda x: x,
              normalize_timeout_seconds=lambda x: x,
              timeout_kwargs=lambda x: {} if x is None else {"timeout": x * 1000},
              click=lambda locator: locator.click(),
          )}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), cls], type_ignores=[])), str(SOURCE), "exec"), ns)
    return ns["AppianMenu"]


Menu = load_menu()


class MenuTests(unittest.TestCase):
    def setUp(self):
        Expect.calls = []
        self.sign_out = Node("button", "Sign Out", attrs={"value": "Sign Out"})
        self.other = Node("button", "Sign Out", text="Sign Out")
        self.button = Node("button", "User options", attrs={"aria-expanded": "false"})
        self.button.on_click = lambda: self.button.attrs.update({"aria-expanded": "true"})
        self.dialog = Node("dialog", "User options", children=[self.sign_out])
        self.page = Locator([Node("document", "", children=[self.button, self.dialog, self.other])])
        self.page.wait_for_appian_action_completed = Mock()
        self.page.expect_popup = Mock()

    def test_logout_clicks_named_dialog_input_button_without_popup_wait(self):
        result = Menu(self.page, "User options").menu(name="Sign Out").click(opens_new_page=False)
        self.assertIs(result, self.page)
        self.assertEqual(self.sign_out.clicks, 1)
        self.assertEqual(self.other.clicks, 0)
        self.assertEqual(self.button.clicks, 1)
        self.page.expect_popup.assert_not_called()
        self.page.wait_for_appian_action_completed.assert_called_once_with(timeout=None)

    def test_site_switch_option_returns_wrapped_popup(self):
        switch_button = Node("button", "CORE Admin Console")
        destination = Node("option", "CORE User Hub", text="CORE User Hub")
        self.page.nodes[0].children = [switch_button, destination]
        popup = self.popup()
        self.assertIs(Menu(self.page, "CORE Admin Console").menu(name="CORE User Hub").click(opens_new_page=True).raw_page, popup)
        self.assertEqual(destination.clicks, 1)
        self.assertEqual(switch_button.clicks, 1)

    def test_requested_site_switch_chain_can_skip_popup_wait(self):
        switch_button = Node("button", "CORE Admin Console")
        destination = Node("option", "CORE User Hub", text="CORE User Hub")
        self.page.nodes[0].children = [switch_button, destination]
        result = Menu(self.page, name="CORE Admin Console").menu(name="CORE User Hub").click(opens_new_page=False)
        self.assertIs(result, self.page)
        self.assertEqual((switch_button.clicks, destination.clicks), (1, 1))
        self.page.expect_popup.assert_not_called()

    def test_ancestor_click_failure_does_not_click_leaf(self):
        def fail():
            raise BrowserTimeout("cannot open ancestor")
        self.button.on_click = fail
        with self.assertRaises(BrowserTimeout):
            Menu(self.page, "User options").menu(name="Sign Out").click()
        self.assertEqual(self.sign_out.clicks, 0)
        self.page.wait_for_appian_action_completed.assert_not_called()

    def test_new_page_keeps_original_context_and_returns_public_wrapper(self):
        source = SOURCE.parents[1] / "page/appian_page.py"
        cls = next(n for n in ast.parse(source.read_text()).body if isinstance(n, ast.ClassDef) and n.name == "AppianPage")
        method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "new_page")
        namespace = {}
        exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])), str(source), "exec"), namespace)
        class PageWrapper:
            new_page = namespace["new_page"]
            get = Mock(return_value=object())
        wrapper = PageWrapper()
        wrapper._robo_page = Mock()
        actual = wrapper.new_page()
        raw_context = wrapper._robo_page._page.context
        raw_context.new_page.assert_called_once_with()
        PageWrapper.get.assert_called_once_with(raw_context.new_page.return_value)
        self.assertIs(actual, PageWrapper.get.return_value)

    def test_uploaded_html_anchor_resolves_by_explicit_button_role(self):
        # Exact control attributes from the supplied closed-menu HTML snapshot.
        # It does not include an expanded dialog or the Sign Out action.
        html = '<a aria-label="User options" tabindex="0" role="button" aria-expanded="false" class="elements---global_a"></a>'
        nodes = []
        class Parser(HTMLParser):
            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                nodes.append(Node(attrs.get("role", tag), attrs.get("aria-label", ""), attrs=attrs))
        Parser().feed(html)
        self.page.nodes[0].children = nodes
        menu = Menu(self.page, "User options")
        self.assertIs(menu._locator().nodes[0], nodes[0])
        self.assertEqual(nodes[0].attrs["aria-expanded"], "false")

    def test_captured_signout_button_text_is_selected_in_user_options_dialog(self):
        # Expanded snapshot 00060: dialog[aria-label="User options"] contains
        # <button type="button"><span>...<span>Sign Out</span></span></button>.
        self.sign_out.attrs = {"type": "button"}
        self.sign_out.text = "Sign Out"
        self.assertIs(Menu(self.page, "User options").menu(name="Sign Out").click(opens_new_page=False), self.page)
        self.assertEqual(self.sign_out.clicks, 1)
        self.assertEqual(self.other.clicks, 0)

    def test_visibility_checks_anchor_role_button_without_opening_or_waiting(self):
        menu = Menu(self.page, "User options")
        self.assertTrue(menu.is_visible())
        self.assertEqual(self.button.clicks, 0)
        self.assertEqual(Expect.calls, [])
        self.button.visible = False
        self.assertFalse(menu.is_visible())
        self.page.nodes[0].children = []
        self.assertFalse(menu.is_visible())

    def test_chain_construction_does_not_click_or_wait(self):
        item = Menu(self.page, "User options").menu(name="Sign Out")
        self.assertIsInstance(item, Menu)
        self.assertEqual(self.button.clicks, 0)
        self.assertEqual(self.sign_out.clicks, 0)
        self.assertEqual(Expect.calls, [])
        self.page.expect_popup.assert_not_called()

    def test_nested_path_opens_each_ancestor_and_clicks_leaf_once(self):
        self.button.name = "Administration"
        self.dialog.name = "Administration"
        submenu = Node("button", "User Management", attrs={"aria-expanded": "false"})
        user_action = Node("menuitem", "Users", text="Users", visible=False)
        def expand():
            submenu.attrs["aria-expanded"] = "true"
            user_action.visible = True
        submenu.on_click = expand
        self.dialog.children = [submenu]
        submenu_dialog = Node("dialog", "User Management", children=[user_action])
        self.page.nodes[0].children.append(submenu_dialog)
        item = Menu(self.page, "Administration").menu(name="User Management").menu(name="Users")
        self.assertEqual(self.button.clicks, 0)
        self.assertIs(item.click(), self.page)
        self.assertEqual((self.button.clicks, submenu.clicks, user_action.clicks), (1, 1, 1))
        self.page.expect_popup.assert_not_called()

    def test_root_click_opens_trigger_once(self):
        self.assertIs(Menu(self.page, "User options").click(), self.page)
        self.assertEqual(self.button.clicks, 1)
        self.assertEqual(self.sign_out.clicks, 0)

    def test_child_visibility_does_not_open_ancestors(self):
        self.sign_out.visible = False
        self.assertFalse(Menu(self.page, "User options").menu(name="Sign Out").is_visible())
        self.assertEqual(self.button.clicks, 0)
        self.assertEqual(Expect.calls, [])

    def test_old_select_and_value_keyword_are_absent(self):
        menu = Menu(self.page, "User options")
        self.assertFalse(hasattr(menu, "select"))
        with self.assertRaises(TypeError):
            menu.menu(value="Sign Out")
        self.assertEqual(self.button.clicks, 0)

    def test_name_matching_respects_exact_flag(self):
        with self.assertRaises(BrowserTimeout):
            Menu(self.page, "User options").menu(name="Sign").click()
        self.assertEqual(self.sign_out.clicks, 0)
        self.assertIs(Menu(self.page, "User options", exact=False).menu(name="Sign").click(), self.page)
        self.assertEqual(self.sign_out.clicks, 1)

    def test_already_open_menu_is_not_toggled_closed(self):
        self.button.attrs["aria-expanded"] = "true"
        Menu(self.page, "User options").menu(name="Sign Out").click(opens_new_page=False)
        self.assertEqual(self.button.clicks, 0)

    def test_timeout_seconds_are_converted_for_expect(self):
        Menu(self.page, "User options", timeout=10).menu(name="Sign Out").click(opens_new_page=False)
        self.assertTrue(Expect.calls)
        self.assertTrue(all(c == {"timeout": 10000} for c in Expect.calls))

    def test_same_page_click_failure_propagates(self):
        def fail():
            raise BrowserTimeout("click failed")
        self.sign_out.on_click = fail
        with self.assertRaises(BrowserTimeout):
            Menu(self.page, "User options").menu(name="Sign Out").click(opens_new_page=False)
        self.page.wait_for_appian_action_completed.assert_not_called()

    def test_unknown_action_is_not_resolved_from_unrelated_buttons(self):
        self.dialog.children = []
        with self.assertRaises(BrowserTimeout):
            Menu(self.page, "User options").menu(name="Sign Out").click(opens_new_page=False)
        self.assertEqual(self.other.clicks, 0)

    def test_profile_options_include_input_value(self):
        self.assertEqual(Menu(self.page, "User options").options(), ["Sign Out"])

    def popup(self, *, absent=False):
        popup_page = Mock()
        class Event:
            value = popup_page
            def __enter__(self): return self
            def __exit__(self, kind, value, traceback):
                if kind is None and absent:
                    raise BrowserTimeout("no popup")
                return False
        self.page.expect_popup.return_value = Event()
        return popup_page

    def test_popup_click_returns_public_appian_page(self):
        popup = self.popup()
        self.assertIs(Menu(self.page, "User options").menu(name="Sign Out").click(opens_new_page=True).raw_page, popup)
        popup.wait_for_load_state.assert_called_once_with("domcontentloaded")

    def test_required_popup_timeout_propagates_after_single_click(self):
        self.popup(absent=True)
        with self.assertRaises(BrowserTimeout):
            Menu(self.page, "User options").menu(name="Sign Out").click(opens_new_page=True)
        self.assertEqual(self.sign_out.clicks, 1)

    def test_popup_click_timeout_is_not_mistaken_for_absent_popup(self):
        self.popup()
        self.sign_out.on_click = lambda: (_ for _ in ()).throw(BrowserTimeout("click"))
        with self.assertRaises(BrowserTimeout):
            Menu(self.page, "User options").menu(name="Sign Out").click(opens_new_page=True)

    def test_new_page_load_failure_propagates(self):
        popup = self.popup()
        popup.wait_for_load_state.side_effect = BrowserTimeout("new page load")
        with self.assertRaises(BrowserTimeout):
            Menu(self.page, "User options").menu(name="Sign Out").click(opens_new_page=True)

    def test_one_based_menu_indexes_and_argument_validation(self):
        menu = Menu(self.page, "User options")
        menu.menu(index=1).click(opens_new_page=False)
        self.assertEqual(self.sign_out.clicks, 1)
        for kwargs in ({}, {"name": "Sign Out", "index": 1}, {"index": 0}, {"index": True}, {"name": " "}):
            with self.assertRaises(ValueError):
                menu.menu(**kwargs)


if __name__ == "__main__":
    unittest.main()
