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
)
from asyncio import run
from src.search_related import insert_doc


def create_tag(drop: Dropdown, text: str, e: ControlEvent) -> None:
    if text:
        for option in drop.options:
            if option.key == text:
                break
        else:
            drop.options.append(dropdown.Option(text))
            with open("./data/tags", "w") as file:
                file.write("\n".join([option.key for option in drop.options]))
            e.page.update()


def select_tag(event: ControlEvent, btns: Row, drop: Dropdown) -> None:
    if drop.value:
        for btn in btns.controls:
            if drop.value == btn.text:
                break
        else:
            btns.controls.append(ElevatedButton(text=drop.value))
            event.page.update()


def disselect_tag(e: ControlEvent, btns: Row, drop: Dropdown) -> None:
    if drop.value:
        for btn in btns.controls:
            if btn.text == drop.value:
                btns.controls.remove(btn)
                e.page.update()
                break


def delete_tag(e: ControlEvent, drop: Dropdown) -> None:
    if drop.value:
        for option in drop.options:
            if option.key == drop.value:
                drop.options.remove(option)
                with open("./data/tags", "w") as file:
                    file.write("\n".join([option.key for option in drop.options]))
                e.page.update()
                break


def remove_btn(e: ControlEvent, lv: ListView) -> None:
    for row in lv.controls:
        if row.controls[-1] == e.control:
            remove(row.controls[0].src)
            lv.controls.remove(row)
            break
    e.page.update()


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


async def extract_text(folder: str, ocr, nlp) -> str:
    full_text = ""
    for file in listdir(folder):
        content = ocr.readtext(f"{folder}/{file}", detail=0)
        full_text += " " + " ".join(content)
    doc = nlp(full_text)
    text = " ".join([token.lemma_ for token in doc])
    return text


def save(e: ControlEvent, tags: Row, ocr, nlp) -> None:
    folder = move_files()
    tags = ", ".join([control.text for control in tags.controls])
    e.page.go("/begin_upload")
    text = run(extract_text(folder, ocr, nlp))
    insert_doc(folder, tags, text)


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
                    ElevatedButton("Remove", on_click=lambda e: remove_btn(e, lv)),
                ],
            )
        )

    page.controls.append(
        Row(
            expand=True,
            controls=[
                Column(
                    expand=True,
                    controls=[
                        ElevatedButton(
                            text="Upload more files",
                            on_click=lambda _: page.overlay[0].pick_files(
                                file_type=FilePickerFileType.IMAGE, allow_multiple=True
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
                                    on_click=lambda e: select_tag(e, tags, tag_drop),
                                ),
                                OutlinedButton(
                                    text="Disselect",
                                    on_click=lambda e: disselect_tag(e, tags, tag_drop),
                                ),
                                FilledButton(
                                    text="Delete",
                                    on_click=lambda e: delete_tag(e, tag_drop),
                                ),
                            ],
                        ),
                        Row(
                            controls=[
                                tag_input_field,
                                ElevatedButton(
                                    text="Create",
                                    on_click=lambda e: create_tag(
                                        tag_drop, tag_input_field.value, e
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
                                    on_click=lambda _: page.go("/begin_upload"),
                                ),
                                ElevatedButton(
                                    text="Save",
                                    on_click=lambda e: save(e, tags, ocr, nlp),
                                ),
                            ]
                        ),
                    ],
                    expand=True,
                ),
            ],
        )
    )
