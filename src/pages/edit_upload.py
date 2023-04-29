from os.path import dirname, abspath, join
from os import remove, listdir, mkdir
from shutil import move
from flet import (
    Row,
    Page,
    Text,
    Image,
    Column,
    ListView,
    ElevatedButton,
    OutlinedButton,
    FilledButton,
    Dropdown,
    dropdown,
    TextField,
    FilePickerFileType,
    ControlEvent,
    View,
    SnackBar,
)
from src.helper import insert, get_embedding, clear_view
from functools import partial
from asyncio import run


def create_tag(event: ControlEvent, drop: Dropdown, text: TextField) -> None:
    if text:
        for option in drop.options:
            if option.key == text.value:
                break
        else:
            drop.options.append(dropdown.Option(text.value))
            with open("./data/tags", "w") as file:
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
                with open("./data/tags", "w") as file:
                    file.write("\n".join([option.key for option in drop.options]))
                event.page.update()
                break


def remove_btn(event: ControlEvent, lv: ListView) -> None:
    for row in lv.controls:
        if row.controls[-1] == event.control:
            remove(row.controls[0].src)
            lv.controls.remove(row)

            break
    event.page.update()


def create_folder_name() -> str:
    if not listdir("./data/docs"):
        return "./data/docs/doc_1"
    else:
        max_num = int(listdir("./data/docs")[-1].split("_")[-1])
        return f"./data/docs/doc_{max_num + 1}"


def move_files() -> str:
    folder = create_folder_name()
    mkdir(folder)
    for file in listdir("./data/temp"):
        move(f"./data/temp/{file}", folder)
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
        wrap=True,
        spacing=10,
        run_spacing=10,
        controls=[],
        width=page.width // 4,
    )

    # the following path nonsense is because of a problem loading images
    # that get copied to a folder using relative path
    # flet doesn't load the images so abs path is required to make it work
    rel_dir = "data/temp"
    # Get the absolute path of the directory containing the script
    script_dir = dirname(abspath(__file__))
    script_dir = "/".join(script_dir.split("\\")[:-2])
    # Get the absolute path of the directory containing the files to be listed
    abs_dir = join(script_dir, rel_dir)

    # load saved tags
    with open("./data/tags", "r") as file:
        saved_tags_text = [tag.strip() for tag in file.readlines()]

    # Dropdown and TextField needed for callback
    tag_drop = Dropdown(options=[dropdown.Option(text) for text in saved_tags_text])
    tag_input_field = TextField(hint_text="tag to create")

    # List View of images and remove buttons
    lv = ListView(expand=True, spacing=10, padding=20)
    for file in listdir(abs_dir):
        lv.controls.append(
            Row(
                expand=True,
                controls=[
                    Image(src=f"{abs_dir}/{file}", width=3 * 192, height=3 * 108),
                    ElevatedButton("Remove", on_click=partial(remove_btn, lv=lv)),
                ],
            )
        )

    page.views.append(
        View(
            route="/edit_upload",
            controls=[
                Row(
                    expand=True,
                    controls=[
                        Column(
                            expand=True,
                            controls=[
                                ElevatedButton(
                                    text="Upload more files",
                                    on_click=lambda _: page.overlay[0].pick_files(
                                        file_type=FilePickerFileType.IMAGE,
                                        allow_multiple=True,
                                    ),
                                ),
                                lv,
                            ],
                        ),
                        Column(
                            controls=[
                                Row(
                                    controls=[
                                        tag_drop,
                                        ElevatedButton(
                                            text="Select",
                                            on_click=partial(
                                                select_tag,
                                                btns=tags,
                                                drop=tag_drop,
                                            ),
                                        ),
                                        OutlinedButton(
                                            text="Disselect",
                                            on_click=partial(
                                                disselect_tag,
                                                btns=tags,
                                                drop=tag_drop,
                                            ),
                                        ),
                                        FilledButton(
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
                                            text="Discard",
                                            on_click=clear_view,
                                        ),
                                        ElevatedButton(
                                            text="Save",
                                            on_click=partial(
                                                save,
                                                tags=tags,
                                                ocr=ocr,
                                                nlp=nlp,
                                            ),
                                        ),
                                    ]
                                ),
                            ],
                            expand=True,
                        ),
                    ],
                )
            ],
        )
    )
