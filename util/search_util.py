# built-ins
from webbrowser import open as web_open
from functools import partial
from os.path import abspath
from os import listdir

# my code
from util.constants import DOCS_DIR, TEMP_DIR, PDF_NAME, VEC_DB_DIR, COLLECTION_NAME
from util.shared_util import clear_folder, get_embedding

# packages
from flet import (
    TextField,
    Row,
    ListView,
    Image,
    ElevatedButton,
    ControlEvent,
    ImageFit,
    ImageRepeat,
    border_radius,
    Text,
)
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Filter,
    FieldCondition,
    MatchValue,
)
from img2pdf import convert


def find_docs(tags: list[str], query: str, nlp) -> list[str]:
    # if nothing is entered then whitespace minimum for spacy to embed
    client = QdrantClient(path=VEC_DB_DIR)
    embed = get_embedding(query, nlp)
    if tags:
        search_result = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=embed,
            limit=10,
            query_filter=Filter(
                should=[
                    FieldCondition(key="tags", match=MatchValue(value=tag))
                    for tag in tags
                ]
            ),
        )
    else:
        search_result = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=embed,
            limit=10,
        )
    return [result.payload["folder_name"] for result in search_result]


def create_pdf(image_paths: list[str]) -> None:
    """Create a pdf out of images specified here, save it to TEMP_DIR"""
    with open(f"{TEMP_DIR}/{PDF_NAME}", "wb") as file:
        file.write(convert(image_paths))


def launch_pdf() -> None:
    """Launch pdf in TEMP_DIR for viewing in browser"""
    abs_path = abspath(f"{TEMP_DIR}/{PDF_NAME}")
    web_open(abs_path)


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
