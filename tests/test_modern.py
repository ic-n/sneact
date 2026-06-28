from sneact.modern import component, render, root, select, tag, text


def test_basic_nesting():
    @component
    def greeting(name: str):
        with tag.div(class_="greeting"):
            text(f"Hello, {name}!")

    assert render(greeting("World")) == '<div class="greeting">Hello, World!</div>'


def test_components_compose():
    @component
    def row(label: str):
        with tag.li():
            text(label)

    @component
    def list_page(labels: list[str]):
        with tag.ul():
            for label in labels:
                row(label)

    html = render(list_page(["a", "b"]))
    assert html == "<ul><li>a</li><li>b</li></ul>"


def test_match_statement_as_control_flow():
    @component
    def status_badge(status: str):
        match status:
            case "ok":
                with tag.span(class_="ok"):
                    text("OK")
            case _:
                with tag.span(class_="unknown"):
                    text("?")

    assert render(status_badge("ok")) == '<span class="ok">OK</span>'
    assert render(status_badge("nope")) == '<span class="unknown">?</span>'


def test_select_expression_helper():
    assert select("ok", ok="Good", _="Default") == "Good"
    assert select("missing", ok="Good", _="Default") == "Default"


def test_root_without_component():
    with root() as page:
        with tag.div():
            text("loose markup")

    assert render(page) == "<div>loose markup</div>"


def test_bare_tag_as_context_manager():
    @component
    def list_page():
        with tag.ul:
            with tag.li:
                text("a")
            with tag.li(class_="x"):
                text("b")

    assert render(list_page()) == '<ul><li>a</li><li class="x">b</li></ul>'


def test_self_closing_tag():
    with root() as page:
        tag.img(src="cat.png")

    assert render(page) == '<img src="cat.png">'
