# built-in
from functools import partial
from os import listdir, mkdir, remove
from os.path import abspath
from asyncio import run
from shutil import move

# my code
from util.constants import TAGS_FILE, DOCS_DIR, TEMP_DIR, COLLECTION_NAME, VEC_DB_DIR
from util.shared_util import get_embedding, clear_folder

# packages
from flet import (
    Row,
    Text,
    Dropdown,
    dropdown,
    TextField,
    ControlEvent,
    SnackBar,
    ListView,
    Image,
    ElevatedButton,
)
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from easyocr.easyocr import Reader as OcrModel


def clear_view(event: ControlEvent) -> None:
    event.page.views.pop()
    event.page.update()


def discard(event: ControlEvent) -> None:
    clear_folder(abspath(TEMP_DIR))
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


async def extract_text(folder: str, ocr: OcrModel) -> str:
    full_text = ""
    for file in listdir(folder):
        content = ocr.readtext(f"{folder}/{file}", detail=0)
        full_text += " " + " ".join(content)
    return full_text.lower()


def insert(embedding: list[float], folder: str, tags: list[str]) -> None:
    client = QdrantClient(path=VEC_DB_DIR)
    collection_info = client.get_collection(collection_name=COLLECTION_NAME)
    vectors_count = collection_info.vectors_count
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=vectors_count + 1,
                vector=list([float(num) for num in embedding]),
                payload={"folder_name": folder, "tags": tags},
            )
        ],
    )


def save(event: ControlEvent, tags: Row, ocr, nlp) -> None:
    folder = move_files()
    tags = [control.text for control in tags.controls]
    clear_view(event)
    text = run(extract_text(folder, ocr))
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


def remove_btn(event: ControlEvent, lv: ListView) -> None:
    for row in lv.controls:
        if row.controls[-1] == event.control:
            remove(row.controls[0].src)
            lv.controls.remove(row)

            break
    event.page.update()


def populate_listview(lv: ListView) -> None:
    abs_dir = abspath(TEMP_DIR)
    for file in listdir(abs_dir):
        # a row in the list view is 2/3 image and 1/3 button
        lv.controls.append(
            Row(
                expand=True,
                controls=[
                    Image(
                        expand=2,
                        src=f"{abs_dir}/{file}",
                        width=3 * 192,
                        height=3 * 108,
                    ),
                    ElevatedButton(
                        expand=1, text="Remove", on_click=partial(remove_btn, lv=lv)
                    ),
                ],
            )
        )
