"""Callable/indexable accessors for Appian components."""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

T = TypeVar("T")


class AppianComponentAccessor(Generic[T]):
    """Expose a component both by semantic arguments and zero-based index.

    The accessor is callable, preserving APIs such as ``cell.dropdown(label=...)``,
    and subscriptable for unlabeled cell content, for example
    ``cell.dropdown[0]``. Cell accessors may also delegate operations directly
    to their first component, for example ``cell.dropdown.select(...)``.
    Component indexes are zero-based Python indexes.
    """

    def __init__(
        self,
        factory: Callable[..., T],
        indexed_factory: Callable[[int], T],
        *,
        component_name: str,
        default_factory: Callable[[], T] | None = None,
    ) -> None:
        self._factory = factory
        self._indexed_factory = indexed_factory
        self._component_name = component_name
        self._default_factory = default_factory

    def __call__(self, *args, **kwargs) -> T:
        return self._factory(*args, **kwargs)

    def __getitem__(self, index: int) -> T:
        if isinstance(index, bool) or not isinstance(index, int):
            raise TypeError(f"{self._component_name} index must be an integer.")
        if index < 0:
            raise IndexError(f"{self._component_name} index cannot be negative.")
        return self._indexed_factory(index)

    @property
    def first(self) -> T:
        """Return the first matching component using zero-based component order."""
        return self._indexed_factory(0)

    def __getattr__(self, name: str):
        """Delegate component operations to the default cell component.

        Cell accessors provide a default factory so concise BA syntax such as
        ``cell.dropdown.select(...)`` targets the first component in that
        already-resolved cell. Page-level accessors intentionally do not
        provide a default because page-wide selection should be semantic or
        explicitly indexed.
        """
        if self._default_factory is None:
            raise AttributeError(
                f"{self._component_name} requires semantic arguments or an explicit "
                "zero-based component index."
            )
        return getattr(self._default_factory(), name)


__all__ = ["AppianComponentAccessor"]
