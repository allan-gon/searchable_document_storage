# built-ins
from functools import partial
from os.path import exists
from os import mkdir

# my code
from util.constants import (
    ROUTES,
    DATA_DIR,
    TEMP_DIR,
    DOCS_DIR,
    TAGS_FILE,
    VEC_DB_DIR,
    SPACY_MODEL_PATH,
    COLLECTION_NAME,
    DIMENSION,
)
from src.pages.edit_upload import create_edit_upload_page

# packages
from flet import (
    ControlEvent,
    Page,
    NavigationBar,
    NavigationDestination,
    icons,
    FilePickerResultEvent,
    SnackBar,
    Text,
)
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from fitz import open as open_pdf
from easyocr.easyocr import Reader as OcrModel
from easyocr import Reader
from spacy.lang.en import English as SpacyModel
from spacy import load


def switch_routes(event: ControlEvent) -> None:
    event.page.go(ROUTES[event.control.selected_index])


def create_nav_bar(page: Page) -> NavigationBar:
    return NavigationBar(
        destinations=[
            NavigationDestination(icon=icons.SEARCH),
            NavigationDestination(icon=icons.FILE_UPLOAD),
        ],
        selected_index=0,
        on_change=partial(switch_routes),
    )


def create_db() -> None:
    client = QdrantClient(path=VEC_DB_DIR)
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=DIMENSION, distance=Distance.COSINE),
    )


def ensure_folders_exist() -> None:
    # create folders if they're missing
    if not exists(DATA_DIR):
        mkdir(DATA_DIR)

    if not exists(TEMP_DIR):
        mkdir(TEMP_DIR)

    if not exists(DOCS_DIR):
        mkdir(DOCS_DIR)


def ensure_tags_exist() -> None:
    # create file if missing
    if not exists(TAGS_FILE):
        with open(TAGS_FILE, "w"):
            pass


def ensure_db_exists() -> None:
    if not exists(VEC_DB_DIR):
        create_db()


def setup() -> tuple:
    ensure_folders_exist()
    ensure_tags_exist()
    ensure_db_exists()
    return Reader(["en"]), load(SPACY_MODEL_PATH)


def copy_selected_files(
    res: FilePickerResultEvent, ocr: SpacyModel, nlp: OcrModel
) -> None:
    if res.files:
        # convert into image and save them to temp folder
        with open_pdf(res.files[0].path) as pdf:
            for page_num in range(pdf.page_count):
                page = pdf.load_page(page_num)
                pix = page.get_pixmap()
                pix.save(f"{TEMP_DIR}/{page_num}.png")
        # after pdf to image go to edit_upload page
        create_edit_upload_page(res.page, ocr, nlp)

    else:
        # this red may be too harsh
        res.page.show_snack_bar(
            SnackBar(
                content=Text(value="No pdf selected"), open=True, bgcolor="#FF3030"
            )
        )
