# built-in
from os.path import exists, abspath
from os import mkdir, listdir, remove
from shutil import copy
from webbrowser import open as web_open

# my code
from src.constants import (
    ROUTES,
    SPACY_MODEL_PATH,
    DATA_DIR,
    TEMP_DIR,
    DOCS_DIR,
    TAGS_FILE,
    VEC_DB_DIR,
    COLLECTION_NAME,
    PDF_NAME,
)

# packages
from flet import (
    Page,
    NavigationBar,
    NavigationDestination,
    icons,
    FilePickerResultEvent,
    ControlEvent,
)
from spacy import load
from easyocr import Reader
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from img2pdf import convert


def create_nav_bar(page: Page) -> NavigationBar:
    return NavigationBar(
        destinations=[
            NavigationDestination(icon=icons.SEARCH),
            NavigationDestination(icon=icons.FILE_UPLOAD),
        ],
        selected_index=0,
        on_change=lambda e: page.go(ROUTES[e.control.selected_index]),
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


def create_db() -> None:
    client = QdrantClient(path=VEC_DB_DIR)
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=96, distance=Distance.COSINE),
    )


def ensure_db_exists() -> None:
    if not exists(VEC_DB_DIR):
        create_db()


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


def setup() -> tuple:
    # necessary because my local version will have stuff in it
    # and it would suck to have to clear it every time I update
    # and ship the app. Instead those folders/files are omitted
    # by default an made on 1st app start
    ensure_folders_exist()
    ensure_tags_exist()
    ensure_db_exists()
    return Reader(["en"]), load(SPACY_MODEL_PATH)


def intermediate(res: FilePickerResultEvent, route: str) -> None:
    """
    Needed to refresh page since that only happens on route change.
    Refreshing, to the user, doesn't mean changing pages so behind the
    scenes I change the route then return so the on route change event
    triggers and page is refreshed
    """
    if len(res.page.views) > 1:
        clear_view(res)
    res.page.go("/intermediate")
    res.page.go(route)


def copy_selected_files(res: FilePickerResultEvent) -> None:
    if res.files:
        for file in res.files:
            if file not in listdir(TEMP_DIR):
                copy(file.path, TEMP_DIR)
    intermediate(res, "/edit_upload")


def remove_stops_and_lemmatize(doc):
    return [token.lemma_ for token in doc if not token.is_stop]


def get_embedding(text, nlp):
    doc = nlp(text)
    lemmatized_tokens = remove_stops_and_lemmatize(doc)
    # if all words are stop, list is empty and dims are off
    # whitespace string fixes that
    if not lemmatized_tokens:
        lemmatized_tokens = [" "]
    lemmatized_doc = nlp(" ".join(lemmatized_tokens))
    return lemmatized_doc.vector


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


def clear_view(event: ControlEvent) -> None:
    event.page.views.pop()
    event.page.update()


def clear_folder(folder) -> None:
    """Remove files from a specified folder, usually the TEMP_DIR"""
    for file in listdir(folder):
        remove(f"{folder}/{file}")


def create_pdf(image_paths: list[str]) -> None:
    """Create a pdf out of images specified here, save it to TEMP_DIR"""
    with open(f"{TEMP_DIR}/{PDF_NAME}", "wb") as file:
        file.write(convert(image_paths))


def launch_pdf() -> None:
    """Launch pdf in TEMP_DIR for viewing in browser"""
    abs_path = abspath(f"{TEMP_DIR}/{PDF_NAME}")
    web_open(abs_path)
