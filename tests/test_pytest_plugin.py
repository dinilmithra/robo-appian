"""Unit-level validation for robo-appian pytest fixture lifecycle wiring."""

from __future__ import annotations

from robo_appian.pytest_plugin import (
    _default_context_lifecycle,
    _default_page_lifecycle,
)


class _Page:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class _Context:
    def __init__(self) -> None:
        self.closed = False
        self.page = _Page()

    def new_page(self):
        return self.page

    def close(self) -> None:
        self.closed = True


class _Browser:
    def __init__(self) -> None:
        self.options = None
        self.context = _Context()

    def new_context(self, **options):
        self.options = options
        return self.context


def test_default_context_lifecycle_wraps_and_closes_context() -> None:
    browser = _Browser()
    lifecycle = _default_context_lifecycle(browser, {"cookies": []}, None)
    context = next(lifecycle)
    assert context is browser.context
    assert browser.options == {"storage_state": {"cookies": []}}
    lifecycle.close()
    assert browser.context.closed is True


def test_default_page_lifecycle_creates_and_closes_page() -> None:
    context = _Context()
    lifecycle = _default_page_lifecycle(context, None)
    page = next(lifecycle)
    assert page is not None
    lifecycle.close()
    assert context.page.closed is True
