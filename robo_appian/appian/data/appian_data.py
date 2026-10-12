"""Business-facing values returned by Appian datasets."""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

T = TypeVar("T")


class AppianData:
    """One value in a structured Appian dataset."""

    def __init__(
        self, value: str | Callable[[], str], *, field: str | None = None
    ) -> None:
        self._value = value
        self.field = field

    @property
    def value(self) -> str:
        value = self._value() if callable(self._value) else self._value
        return " ".join(str(value or "").replace("\u00a0", " ").split())


class AppianDataCollection(Generic[T]):
    """Ordered dataset results; order is the order displayed by Appian."""

    def __init__(self, items: list[T]) -> None:
        self._items = items

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, index: int) -> T:
        return self._items[index]

    @property
    def first(self) -> T:
        if not self._items:
            raise LookupError("No matching data was found.")
        return self._items[0]

    @property
    def value(self) -> str:
        if not self._items:
            raise LookupError("No matching data was found.")
        if len(self._items) != 1:
            raise LookupError(
                f"{len(self._items)} data values matched. Use [0], [1], or .first to select one."
            )
        item = self._items[0]
        value = getattr(item, "value", None)
        return value() if callable(value) else value
