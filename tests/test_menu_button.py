from robo_appian.appian.appian_page import AppianPage
from robo_appian.components.MenuButton import MenuButton


def test_menu_button_treats_appian_page_as_page_owner():
    appian_page = object.__new__(AppianPage)

    assert MenuButton._owner_page(appian_page) is appian_page
