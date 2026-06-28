# sneact.modern

A proof of concept for an alternative, friendlier API on top of the same
idea as Sneact: build HTML out of plain Python.

The classic Sneact API leans on operator overloading
(`<<div>>_ ... <<-div>>_`, `@when`, `@for_each`) to get a JSX-like feel.
It's fun, but it means conditionals and loops need their own
mini-DSL (`sneact.cond`, `sneact.loop`), every tag has to be closed by hand,
and there's no help from your editor if you mismatch one.

`sneact.modern` makes the opposite bet: use `with` blocks for nesting, and
get everything else — `if`, `for`, `match`, function composition — for free
from the language itself.

## Quick tour

```python
from sneact.modern import component, tag, text, render

@component
def status_badge(status: str):
    match status:
        case "ok":
            with tag.span(class_="ok"):
                text("OK")
        case "error":
            with tag.span(class_="error"):
                text("Error")
        case _:
            with tag.span(class_="unknown"):
                text("Unknown")

@component
def page(title: str, rows: list[tuple[str, str]]):
    with tag.div():
        with tag.h1():
            text(title)
        with tag.ul():
            for name, status in rows:
                with tag.li():
                    text(name)
                    status_badge(status)

html = render(page(title="Status", rows=[("a", "ok"), ("b", "error")]))
```

```html
<div>
  <h1>Status</h1>
  <ul>
    <li>a<span class="ok">OK</span></li>
    <li>b<span class="error">Error</span></li>
  </ul>
</div>
```

## Why this is different

- **No parens needed for plain tags.** `with tag.li:` works directly; use
  `with tag.li(class_="x"):` only when you need attributes.
- **No mismatched tags.** `with tag.div():` is closed by indentation, not by
  a hand-written `<<-div>>_`. Your editor folds it, formats it, and yells at
  you if you get it wrong — none of that was possible with the operator DSL.
- **Conditionals and loops aren't a DSL anymore.** `sneact.cond.when`/
  `when_not` and `sneact.loop.for_each` exist because the operator API can't
  use real Python control flow inside a tag chain. Under `with`-blocks,
  `if`, `for`, and `match`/`case` work exactly as you'd expect, with no
  special import.
- **Components are just functions.** `@component` turns a function into a
  reusable piece of markup that composes by calling it — like a React
  function component, minus the framework.
- **`select(...)` for the one case `match` can't cover**: inline expressions.
  `match`/`case` is a statement, so it can't go inside `text(...)`. `select`
  gives you the same case-based logic as an expression:

  ```python
  text(select(status, ok="All good", error="Uh oh", _="Unknown"))
  ```

## API

- `tag.<name>(**attrs)` — create an element. Use as `with tag.div(...):` to
  give it children, or call it bare (e.g. `tag.img(src=...)`) for a
  self-closing leaf. Attribute names ending in `_` (e.g. `class_`) have the
  trailing underscore stripped, since `class` is a Python keyword.
- `text(value)` — add a text child to whatever tag/component is currently
  open.
- `@component` — turn a function into something callable that returns a
  `Node`, composable inside other components.
- `root()` — a top-level context manager for building markup without
  wrapping it in a `@component` (handy in scripts/tests/REPLs).
- `render(node)` — turn a `Node` (returned by a component, or from `root()`)
  into an HTML string.
- `select(value, **cases)` — expression-style pattern matching for use
  inside `text(...)`; for everything else, just use `match`/`case`.
