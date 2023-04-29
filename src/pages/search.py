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
    Container,
    Text,
)
from src.pages.edit_upload import select_tag, disselect_tag
from src.helper import find_docs, display_folder
from os.path import dirname, abspath, join
from os import listdir
from functools import partial


def populate_results(
    event: ControlEvent, tags: Row, text_field: TextField, nlp
) -> None:
    # abs path nonsense for images when moved
    rel_dir = "data/docs"
    # Get the absolute path of the directory containing the script
    script_dir = dirname(abspath(__file__))
    script_dir = "/".join(script_dir.split("\\")[:-2])
    # Get the absolute path of the directory containing the files to be listed
    abs_dir = join(script_dir, rel_dir)

    docs = find_docs([control.text for control in tags.controls], text_field.value, nlp)

    lv = event.page.controls[0].controls[-1]
    lv.controls.clear()
    for idx, doc in enumerate(docs, 1):
        row = Row(expand=1, wrap=False, scroll="always")
        row.controls.append(Text(value=idx))
        for file in listdir(doc):
            row.controls.append(
                Container(
                    content=Image(
                        # TODO: fix this nonsense. the folder name stuff requires
                        # changing a few functions
                        src=f"{abs_dir}/{doc.split('/')[-1]}/{file}",
                        width=200,
                        height=200,
                        fit=ImageFit.CONTAIN,
                        repeat=ImageRepeat.NO_REPEAT,
                        border_radius=border_radius.all(10),
                    ),
                    on_click=lambda _: display_folder(
                        f"{abs_dir}/{doc.split('/')[-1]}"
                    ),
                )
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
