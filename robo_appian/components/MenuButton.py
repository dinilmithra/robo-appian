"""Generic helpers for opening menu buttons and choosing menu actions."""

from playwright.sync_api import Locator, Page, expect
from robo_automation import Scope
from robo_appian.utils.ComponentUtils import ComponentUtils
from robo_automation import RoboPage


class MenuButton:
    """Reusable operations for Appian menu-button controls."""

    @staticmethod
    def __find_by_label(scope: Scope, label: str) -> Locator:
        """
        Finds a visible header navigation menu button by its label text.
        """
        role_buttons = scope.get_by_role("button", name=label, exact=False)
        menu_button = (
            role_buttons.and_(
                ComponentUtils.unwrap_scope(scope).locator(
                    "button[type='button'][data-owl-test-label='menuLayout-button']"
                )
            )
            .filter(visible=True)
            .first
        )
        expect(menu_button).to_be_visible()
        return menu_button

    @staticmethod
    def __click_if_not_expanded(menu_button: Locator) -> bool:
        """
        Clicks a menu button only when it is not expanded.
        Returns True when a click is performed, otherwise False.
        """
        aria_expanded = (menu_button.get_attribute("aria-expanded") or "").lower()

        if aria_expanded != "true":
            ComponentUtils.click(menu_button)
            return True

        return False

    @staticmethod
    def __find_id_from_aria_owns(menu_button: Locator) -> str:
        """
        Extracts the menu id from a button's aria-owns attribute.
        Example: "abc123_tetherWrapper" -> "abc123"
        """
        aria_owns = (menu_button.get_attribute("aria-owns") or "").strip()
        if not aria_owns:
            raise ValueError("Menu button does not have a valid 'aria-owns' value.")

        suffix = "_tetherWrapper"
        if aria_owns.endswith(suffix):
            return aria_owns[: -len(suffix)]

        return aria_owns

    @staticmethod
    def __find_menu_listbox(scope: Scope, menu_id: str) -> Locator:
        """
        Finds the visible menu listbox <ul> for the given menu id.
        Example: menu_id='abc123' -> ul id='abc123_menuItems'.
        """
        listbox = (
            ComponentUtils.unwrap_scope(scope)
            .locator(f'ul[id="{menu_id}_menuItems"][role="listbox"]')
            .first
        )
        expect(listbox).to_be_visible()
        return listbox

    @staticmethod
    def __find_menu_item_by_value(listbox: Locator, value: str) -> Locator:
        """
        Finds a visible menu option <li role='option'> by its display text.
        """
        item = (
            listbox.get_by_role("option", name=value, exact=False)
            .filter(visible=True)
            .first
        )
        expect(item).to_be_visible()
        return item

    @staticmethod
    def _owner_page(scope: Scope):
        """Return the page-like owner for a page or locator scope.

        Page wrappers such as RoboPage and AppianPage are already page owners.
        Locator wrappers are unwrapped first and use their Playwright owner page.
        """
        raw_scope = ComponentUtils.unwrap_scope(scope)
        return raw_scope.page if isinstance(raw_scope, Locator) else scope

    @staticmethod
    def select(scope: Scope, label: str, value: str) -> Page:
        """Choose a header-menu option that opens a new browser scope.

        Use this for application switching menus such as CORE Admin Console to
        CORE User Hub. Button and option names are matched partially. The method
        requires the option click to create a popup and returns after that scope
        reaches ``domcontentloaded``.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Visible menu-button label.
            value: Visible option text to select.

        Returns:
            Page: The newly opened browser automation scope; subsequent interactions must use it.

        Raises:
            ValueError: If the menu button has no valid ARIA-owned menu ID.
            AssertionError: If the menu or option does not become visible.
        """

        menu_button = MenuButton.__find_by_label(scope, label)
        MenuButton.__click_if_not_expanded(menu_button)
        menu_id = MenuButton.__find_id_from_aria_owns(menu_button)
        if not menu_id:
            raise ValueError("Menu button does not have a valid 'aria-owns' value.")

        listbox = MenuButton.__find_menu_listbox(scope, menu_id)
        item = MenuButton.__find_menu_item_by_value(listbox, value)
        owner_page = MenuButton._owner_page(scope)
        with owner_page.expect_popup() as new_page_info:
            ComponentUtils.click(item)

        new_page = new_page_info.value
        new_page.wait_for_load_state("domcontentloaded")
        return new_page
