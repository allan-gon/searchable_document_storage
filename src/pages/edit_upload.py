# built-in
from functools import partial

# my code
from util.constants import TAGS_FILE
from util.edit_upload_util import (
    discard,
    create_tag,
    delete_tag,
    save,
    populate_listview,
)
from util.shared_util import select_tag, deselect_tag

# packages
from flet import (
    Row,
    Page,
    Text,
    Column,
    ListView,
    ElevatedButton,
    OutlinedButton,
    FilledButton,
    Dropdown,
    dropdown,
    TextField,
    View,
)


def create_edit_upload_page(page: Page, ocr, nlp) -> None:
    # control that will hold buttons that represent selected tags
    tags = Row(
        # expand=1,
        wrap=True,
        spacing=10,
        run_spacing=10,
        controls=[],
        width=page.width // 4,
    )

    # load saved tags
    with open(TAGS_FILE, "r") as file:
        saved_tags_text = [tag.strip() for tag in file.readlines()]

    # Dropdown and TextField needed for callback
    tag_drop = Dropdown(
        expand=3, options=[dropdown.Option(text) for text in saved_tags_text]
    )
    tag_input_field = TextField(expand=1, hint_text="tag to create")

    # List View of images and remove buttons
    lv = ListView(expand=True, spacing=10)
    populate_listview(lv)

    page.views.append(
        View(
            route="/edit_upload",
            controls=[
                Row(
                    expand=True,
                    controls=[
                        Column(
                            expand=1,
                            controls=[
                                lv,
                            ],
                        ),
                        Column(
                            expand=1,
                            controls=[
                                Row(
                                    controls=[
                                        tag_drop,
                                        ElevatedButton(
                                            expand=1,
                                            text="Select",
                                            on_click=partial(
                                                select_tag,
                                                btns=tags,
                                                drop=tag_drop,
                                            ),
                                        ),
                                        OutlinedButton(
                                            expand=1,
                                            text="Deselect",
                                            on_click=partial(
                                                deselect_tag,
                                                btns=tags,
                                                drop=tag_drop,
                                            ),
                                        ),
                                        FilledButton(
                                            expand=1,
                                            text="Delete",
                                            on_click=partial(
                                                delete_tag,
                                                drop=tag_drop,
                                                text=tag_input_field,
                                            ),
                                        ),
                                    ],
                                ),
                                Row(
                                    controls=[
                                        tag_input_field,
                                        ElevatedButton(
                                            expand=1,
                                            text="Create",
                                            on_click=partial(
                                                create_tag,
                                                drop=tag_drop,
                                                text=tag_input_field,
                                            ),
                                        ),
                                    ],
                                ),
                                Text(value="Currently Selected Tags:"),
                                tags,
                                Row(
                                    controls=[
                                        OutlinedButton(
                                            expand=1,
                                            text="Discard",
                                            on_click=discard,
                                        ),
                                        ElevatedButton(
                                            expand=1,
                                            text="Save",
                                            on_click=partial(
                                                save,
                                                tags=tags,
                                                ocr=ocr,
                                                nlp=nlp,
                                            ),
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                )
            ],
        )
    )
    page.update()
