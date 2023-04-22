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
)
from src.pages.edit_upload import select_tag, disselect_tag
from src.search_related import find_doc
from os.path import dirname, abspath, join
from os import listdir


def populate_results(e: ControlEvent, tags: Row, text_field: TextField) -> None:
    # abs path nonsense for images when moved
    rel_dir = "data/docs"
    # Get the absolute path of the directory containing the script
    script_dir = dirname(abspath(__file__))
    script_dir = "/".join(script_dir.split("\\")[:-2])
    # Get the absolute path of the directory containing the files to be listed
    abs_dir = join(script_dir, rel_dir)

    docs = find_doc([control.text for control in tags.controls], text_field.value)

    lv = e.page.controls[0].controls[-1]
    lv.controls.clear()
    for doc in docs:
        row = Row(expand=1, wrap=False, scroll="always")
        for file in listdir(doc):
            row.controls.append(
                Image(
                    # src=f"{doc}/{file}",
                    src=f"{abs_dir}/{doc.split('/')[-1]}/{file}",
                    width=200,
                    height=200,
                    fit=ImageFit.CONTAIN,
                    repeat=ImageRepeat.NO_REPEAT,
                    border_radius=border_radius.all(10),
                )
            )
        lv.controls.append(row)
    e.page.update()


def create_search_page(page: Page) -> None:
    # control that will hold buttons that represent selected tags
    tags = Row(
        wrap=True,
        spacing=10,
        run_spacing=10,
        controls=[],
        width=page.width // 4,
    )

    # load saved tags
    with open("./data/tags", "r") as file:
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
                            on_click=lambda e: populate_results(
                                e, tags, text_search_field
                            ),
                        ),
                    ],
                ),
                Row(
                    controls=[
                        tag_drop,
                        ElevatedButton(
                            text="Select",
                            on_click=lambda e: select_tag(e, tags, tag_drop),
                        ),
                        OutlinedButton(
                            text="Disselect",
                            on_click=lambda e: disselect_tag(e, tags, tag_drop),
                        ),
                    ],
                ),
                tags,
                lv,
            ],
        )
    )
