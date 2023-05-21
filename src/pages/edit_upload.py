# built-in
from functools import partial
from asyncio import run
from os import listdir, mkdir
from shutil import move

# my code
from src.helper import (
    insert,
    get_embedding,
    clear_view,
    populate_listview,
)
from src.constants import TAGS_FILE, DOCS_DIR, TEMP_DIR

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
    ControlEvent,
    View,
    SnackBar,
)


def discard(event: ControlEvent) -> None:
    clear_view(event)
    event.page.show_snack_bar(
        SnackBar(
            content=Text(value="Document Discarded"),
            open=True,
            bgcolor="#FF3030",
        )
    )
    event.page.update()


def create_tag(event: ControlEvent, drop: Dropdown, text: TextField) -> None:
    if text:
        for option in drop.options:
            if option.key == text.value:
                break
        else:
            drop.options.append(dropdown.Option(text.value))
            with open(TAGS_FILE, "w") as file:
                file.write("\n".join([option.key for option in drop.options]))
            event.page.update()


def select_tag(event: ControlEvent, btns: Row, drop: Dropdown) -> None:
    # when deleted, value must be changed
    if drop.value:
        for btn in btns.controls:
            if drop.value == btn.text:
                break
        else:
            btns.controls.append(ElevatedButton(text=drop.value))
            event.page.update()


def disselect_tag(event: ControlEvent, btns: Row, drop: Dropdown) -> None:
    if drop.value:
        for btn in btns.controls:
            if btn.text == drop.value:
                btns.controls.remove(btn)
                event.page.update()
                break


def delete_tag(event: ControlEvent, drop: Dropdown, text: TextField) -> None:
    if drop.value:
        for option in drop.options:
            if option.key == drop.value:
                drop.options.remove(option)
                text.value = ""
                with open(TAGS_FILE, "w") as file:
                    file.write("\n".join([option.key for option in drop.options]))
                event.page.update()
                break


def create_folder_name() -> str:
    if not listdir(DOCS_DIR):
        return f"{DOCS_DIR}/doc_1"
    else:
        max_num = int(listdir(DOCS_DIR)[-1].split("_")[-1])
        return f"{DOCS_DIR}/doc_{max_num + 1}"


def move_files() -> str:
    folder = create_folder_name()
    mkdir(folder)
    for file in listdir(TEMP_DIR):
        move(f"{TEMP_DIR}/{file}", folder)
    return folder


async def extract_text(folder: str, ocr) -> str:
    full_text = ""
    for file in listdir(folder):
        content = ocr.readtext(f"{folder}/{file}", detail=0)
        full_text += " " + " ".join(content)
    return full_text


def save(event: ControlEvent, tags: Row, ocr, nlp) -> None:
    folder = move_files()
    tags = [control.text for control in tags.controls]
    clear_view(event)
    text = run(extract_text(folder, ocr))  # , nlp))
    embed = get_embedding(text, nlp)
    insert(embed, folder, tags)
    event.page.show_snack_bar(
        SnackBar(
            content=Text(value="Successfully saved document"),
            open=True,
            bgcolor="#238636",
        )
    )
    event.page.update()


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
                                    # expand=1,
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
                                            text="Disselect",
                                            on_click=partial(
                                                disselect_tag,
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
                                    # expand=1,
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
                                Text(
                                    # expand=1,
                                    value="Currently Selected Tags:"
                                ),
                                tags,
                                Row(
                                    # expand=1,
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
