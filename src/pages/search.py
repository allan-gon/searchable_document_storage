# built-ins
from functools import partial

# my code
from util.constants import TAGS_FILE
from util.search_util import populate_results
from util.shared_util import select_tag, deselect_tag

# from shared?


# packages
from flet import (
    Page,
    TextField,
    Dropdown,
    dropdown,
    Row,
    ListView,
    ElevatedButton,
    OutlinedButton,
    Column,
)


def create_search_page(page: Page, nlp) -> None:
    page.controls.clear()
    # control that will hold buttons that represent selected tags
    tags = Row(
        wrap=True,
        spacing=10,
        run_spacing=10,
        controls=[],
        width=page.width // 4,
    )

    # load saved tags
    with open(TAGS_FILE, "r") as file:
        saved_tags_text = [tag.strip() for tag in file.readlines()]

    tag_drop = Dropdown(options=[dropdown.Option(text) for text in saved_tags_text])
    text_search_field = TextField(hint_text="Enter document content")
    lv = ListView(expand=True, spacing=10, padding=20)

    page.controls.append(
        Column(
            expand=True,
            controls=[
                Row(
                    controls=[
                        text_search_field,
                        ElevatedButton(
                            text="Search",
                            on_click=partial(
                                populate_results,
                                tags=tags,
                                text_field=text_search_field,
                                nlp=nlp,
                            ),
                        ),
                    ],
                ),
                Row(
                    controls=[
                        tag_drop,
                        ElevatedButton(
                            text="Select",
                            on_click=partial(select_tag, btns=tags, drop=tag_drop),
                        ),
                        OutlinedButton(
                            text="Deselect",
                            on_click=partial(deselect_tag, btns=tags, drop=tag_drop),
                        ),
                    ],
                ),
                tags,
                lv,
            ],
        )
    )
