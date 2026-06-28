from __future__ import annotations

from typing import Any, Callable, TypeVar

T = TypeVar("T")

_MISSING = object()


def select(value: Any, /, **cases: T | Callable[[], T]) -> T | None:
    """Expression-style pattern matching for use inside `text(...)`.

    For full statements (with nested tags per branch), just use Python's
    own `match`/`case` directly inside a @component -- no helper needed.

    >>> text(select(s.status, loading="Loading...", error="Oops!", _="OK"))
    """
    match value:
        case key if key in cases:
            chosen = cases[key]
        case _:
            chosen = cases.get("_", _MISSING)
            if chosen is _MISSING:
                raise KeyError(
                    f"select(): no case matched {value!r} and no '_' default was given"
                )
    return chosen() if callable(chosen) else chosen
