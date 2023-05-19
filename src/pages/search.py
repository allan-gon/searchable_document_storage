# built-ins
from functools import partial
from os.path import abspath
from os import listdir

# my code
from src.pages.edit_upload import select_tag, disselect_tag
from src.constants import DOCS_DIR, TAGS_FILE, TEMP_DIR
from src.helper import find_docs, create_pdf, launch_pdf, clear_folder

# packages
from flet import (
    Page,
    TextField,
    Dropdown,
    dropdown,
    Row,
    ListView,
    Image,
    ElevatedButton,
    OutlinedButton,
    Column,
    ControlEvent,
    ImageFit,
    ImageRepeat,
    border_radius,
    Text,
)


def launch_doc(event: ControlEvent, lv: ListView) -> None:
    for row in lv.controls:
        if row.controls[-1] == event.control:
            images = [image.src for image in row.controls[1:-1]]
            clear_folder(TEMP_DIR)
            create_pdf(images)
            launch_pdf()


def populate_results(
    event: ControlEvent, tags: Row, text_field: TextField, nlp
) -> None:
    abs_dir = abspath(DOCS_DIR)

    docs = find_docs([control.text for control in tags.controls], text_field.value, nlp)

    lv = event.page.controls[0].controls[-1]
    lv.controls.clear()
    for idx, doc in enumerate(docs, 1):
        row = Row(expand=1, wrap=False, scroll="always")
        row.controls.append(Text(value=idx))
        for file in listdir(doc):
            row.controls.append(
                Image(
                    # TODO: fix this nonsense. the folder name stuff requires
                    # changing a few functions
                    src=f"{abs_dir}/{doc.split('/')[-1]}/{file}",
                    width=200,
                    height=200,
                    fit=ImageFit.CONTAIN,
                    repeat=ImageRepeat.NO_REPEAT,
                    border_radius=border_radius.all(10),
                ),
            )
        row.controls.append(
            ElevatedButton(text="View", on_click=partial(launch_doc, lv=lv))
        )

        lv.controls.append(row)
    event.page.update()


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
                            text="Disselect",
                            on_click=partial(disselect_tag, btns=tags, drop=tag_drop),
                        ),
                    ],
                ),
                tags,
                lv,
            ],
        )
    )
