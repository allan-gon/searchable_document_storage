from flet import (
    Page,
    NavigationBar,
    NavigationDestination,
    icons,
    FilePickerResultEvent,
    ControlEvent,
)
from src.constants import ROUTES, COLLECTION_NAME, VEC_DB_DIR
from tempfile import NamedTemporaryFile
from webbrowser import open as web_open
from os.path import exists, join
from os import mkdir, listdir
from shutil import copy
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
    if not exists("./data/"):
        mkdir("./data")
        mkdir("./data/temp")

    if not exists("./data/temp"):
        mkdir("./data/temp")

    if not exists("./data/docs"):
        mkdir("./data/docs")


def ensure_tags_exist() -> None:
    # create file if missing
    if not exists("./data/tags"):
        with open("./data/tags", "w") as file:
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
    # and ship the app. Instead those folders/files are ommited
    # by default an made on 1st app start
    ensure_folders_exist()
    ensure_tags_exist()
    ensure_db_exists()
    return Reader(["en"]), load("./model/en_core_web_sm-3.5.0")


def intermediate(res: FilePickerResultEvent, route: str) -> None:
    """
    Needed to refresh page since that only happens on route change.
    Refeshing, to the user, doesn't mean changing pages so behing the
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
            if file not in listdir("./data/temp"):
                copy(file.path, "./data/temp")
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
    # if nothing is entered then whitespace minumum for spacy to embed
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


def display_folder(folder: str) -> None:
    # Generate HTML content
    html_content = "<html><head></head><body>"
    for filename in listdir(folder):
        file_path = join(folder, filename)
        html_content += f'<img src="file://{file_path}" alt="{filename}" />'
    html_content += "</body></html>"

    # Create a temporary HTML file
    with NamedTemporaryFile(suffix=".html", delete=False) as temp:
        temp.write(html_content.encode("utf-8"))

    # Open the temporary HTML file in the default browser
    web_open("file://" + temp.name)


def clear_view(event: ControlEvent) -> None:
    event.page.views.pop()
    event.page.update()
