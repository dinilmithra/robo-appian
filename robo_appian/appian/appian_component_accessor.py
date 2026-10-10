"""Callable/indexable accessors for Appian components."""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

T = TypeVar("T")


class AppianComponentAccessor(Generic[T]):
    """Expose a component both by semantic arguments and zero-based index.

    The accessor is callable, preserving APIs such as ``cell.dropdown(label=...)``,
    and subscriptable for unlabeled cell content, for example
    ``cell.dropdown[0]``. Component indexes are zero-based Python indexes.
    """

    def __init__(
        self,
        factory: Callable[..., T],
        indexed_factory: Callable[[int], T],
        *,
        component_name: str,
    ) -> None:
        self._factory = factory
        self._indexed_factory = indexed_factory
        self._component_name = component_name

    def __call__(self, *args, **kwargs) -> T:
        return self._factory(*args, **kwargs)

    def __getitem__(self, index: int) -> T:
        if isinstance(index, bool) or not isinstance(index, int):
            raise TypeError(f"{self._component_name} index must be an integer.")
        if index < 0:
            raise IndexError(f"{self._component_name} index cannot be negative.")
        return self._indexed_factory(index)


__all__ = ["AppianComponentAccessor"]
