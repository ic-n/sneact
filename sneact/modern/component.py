from __future__ import annotations

import functools
from typing import Callable, ParamSpec

from sneact.modern.builder import Node, _FRAGMENT, _stack

P = ParamSpec("P")


def component(func: Callable[P, None]) -> Callable[P, Node]:
    """Turn a plain function into a reusable, composable piece of markup.

    Inside the function body, use `with tag.div():`, `text(...)`, plain
    `if`/`for`/`match` for control flow, and call other @component functions
    directly -- they nest into the caller's tree automatically.
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Node:
        fragment = Node.__new__(Node)
        fragment.name = _FRAGMENT
        fragment.attrs = {}
        fragment.children = []
        try:
            parent_stack = _stack.get()
        except LookupError:
            pass
        else:
            if parent_stack:
                parent_stack[-1].children.append(fragment)

        token = _stack.set([fragment])
        try:
            func(*args, **kwargs)
        finally:
            _stack.reset(token)

        return fragment

    return wrapper
