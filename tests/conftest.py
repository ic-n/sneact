from pytest import fixture


class FakeObject:
    def __init__(self):
        self.token = "x"
        self.segments = ("x",)


@fixture
def fake_magic_class():
    fake = FakeObject()
    return fake


@fixture
def smoke_sneact_expected_results():
    return (
        "\n".join(
            (
                "<div>",
                "<p>Tiger</p>",
                "<p>About tigers</p>",
                "<div>",
                "<p>Hello tigers. We love Tigers.</p>",
                '<img src="tiger.png">',
                "</div>",
                "</div>",
            )
        )
        + "\n"
    )


@fixture
def nested_expected_results():
    return (
        "\n".join(
            (
                "<header>",
                "<h1>Page</h1>",
                "</header>",
                "<p>Lorem you know</p>",
                "<footer>",
                "<p>Copyright Kiselev Nikolay 2020</p>",
                "</footer>",
            )
        )
        + "\n"
    )


@fixture
def conditions_expected_results():
    return (
        "\n".join(
            (
                "<div>",
                "<p>Tiger</p>",
                "<p>About tigers</p>",
                "<div>",
                '<img src="tiger.png">',
                "</div>",
                "</div>",
            )
        )
        + "\n"
    )

@fixture
def not_conditions_expected_results():
    return (
        "\n".join(
            (
                "<div>",
                "<p>Tiger</p>",
                "<p>About tigers</p>",
                "<div>",
                "<p>Hello not tigers. We love Tigers.</p>",
                '<img src="tiger.png">',
                "</div>",
                "</div>",
            )
        )
        + "\n"
    )


@fixture
def loops_expected_results():
    return (
        "\n".join(
            (
                "<div>",
                "<img src=cat.png>",
                "<img src=dog.png>",
                "<img src=frog.png>",
                "</div>",
            )
        )
        + "\n"
    )
