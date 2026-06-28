from sneact import Sneact, s, _
from sneact.loop import for_each, do, item
from sneact.html import div, p, img


# fmt: off

def test_conditions(loops_expected_results):
    scope = dict(
        images=["cat.png", "dog.png", "frog.png"]
    )
    page = (+Sneact(scope)
        <<div>>_
            @for_each(s.images, +do
                <<img(src=item)>>_
            )
        <<-div>>_
    )
    result = page.compile().as_html()
    assert result == loops_expected_results
