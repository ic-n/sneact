from __future__ import annotations

import contextvars
from typing import Any

_FRAGMENT = "__fragment__"

_stack: contextvars.ContextVar[list["Node"]] = contextvars.ContextVar("sneact_modern_stack")


def _current_stack() -> list["Node"]:
    try:
        return _stack.get()
    except LookupError:
        raise RuntimeError(
            "No open tag/component context. Wrap your markup in a @component "
            "function, or use 'with root():' at the top level."
        ) from None


class Node:
    """A single HTML element, built by `with tag.x(...):` nesting."""

    def __init__(self, name: str, attrs: dict[str, Any]):
        self.name = name
        self.attrs = attrs
        self.children: list[Node | str] = []
        try:
            stack = _stack.get()
        except LookupError:
            pass
        else:
            if stack:
                stack[-1].children.append(self)

    def __enter__(self) -> "Node":
        _current_stack().append(self)
        return self

    def __exit__(self, *exc_info: object) -> None:
        _current_stack().pop()

    def render(self) -> str:
        if self.name == _FRAGMENT:
            return "".join(_render_child(c) for c in self.children)
        attrs = "".join(
            f' {_attr_name(k)}="{v}"' for k, v in self.attrs.items()
        )
        if not self.children:
            return f"<{self.name}{attrs}>"
        inner = "".join(_render_child(c) for c in self.children)
        return f"<{self.name}{attrs}>{inner}</{self.name}>"


def _attr_name(name: str) -> str:
    """`class_` -> `class` (trailing underscore, for Python keywords);
    `http_equiv` -> `http-equiv` (HTML attributes use hyphens)."""
    return name.removesuffix("_").replace("_", "-")


def _render_child(child: Node | str) -> str:
    return child.render() if isinstance(child, Node) else str(child)


class _TagProxy:
    """`tag.div` -- usable bare as `with tag.div:`, or called for attrs/leaves."""

    def __init__(self, name: str):
        self._name = name

    def __call__(self, **attrs: Any) -> Node:
        return Node(self._name, attrs)

    def __enter__(self) -> Node:
        self._node = Node(self._name, {})
        return self._node.__enter__()

    def __exit__(self, *exc_info: object) -> None:
        self._node.__exit__(*exc_info)


class _TagFactory:
    """`tag.div` creates a tag, usable as `with tag.div:`, `with tag.div(class_="x"):`,
    or called bare for a leaf, e.g. `tag.img(src=...)`."""

    def __getattr__(self, name: str) -> Any:
        return _TagProxy(name)


tag = _TagFactory()


def text(value: Any) -> None:
    """Append a text/value child to the currently open tag or component."""
    _current_stack()[-1].children.append(str(value))


class root:
    """Top-level fragment context, for building markup outside of a @component.

    Unlike Node, this also installs the contextvar stack, so it works even
    when nothing else has opened a context yet.
    """

    def __enter__(self) -> Node:
        self._fragment = Node.__new__(Node)
        self._fragment.name = _FRAGMENT
        self._fragment.attrs = {}
        self._fragment.children = []
        self._token = _stack.set([self._fragment])
        return self._fragment

    def __exit__(self, *exc_info: object) -> None:
        _stack.reset(self._token)


def render(node: Node) -> str:
    return node.render()
