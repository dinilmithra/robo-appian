"""Typed, zero-based collections of Appian components."""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

T = TypeVar("T")


class AppianComponentCollection(Generic[T]):
    """Resolve components by position within a page, cell, or dialog."""

    def __init__(self, indexed_factory: Callable[[int], T], *, name: str) -> None:
        self._indexed_factory = indexed_factory
        self._name = name

    def __getitem__(self, index: int) -> T:
        if isinstance(index, bool) or not isinstance(index, int):
            raise TypeError(f"{self._name} index must be an integer.")
        if index < 0:
            raise IndexError(f"{self._name} index cannot be negative.")
        return self._indexed_factory(index)

    @property
    def first(self) -> T:
        """Return the first component in display order."""
        return self[0]


__all__ = ["AppianComponentCollection"]
