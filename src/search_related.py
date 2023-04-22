from whoosh.fields import Schema, TEXT, ID, KEYWORD
from whoosh.qparser import QueryParser, AndGroup
from whoosh.query import Or
from whoosh.index import create_in, open_dir
from whoosh.writing import BufferedWriter
from src.constants import INDEX_DIR
import os.path


def create_index() -> None:
    schema = Schema(
        folder_name=ID(stored=True, unique=True),
        tags=KEYWORD(stored=True, commas=True, scorable=True),
        text_content=TEXT(stored=True),
    )

    create_in(INDEX_DIR, schema)


def ensure_index_exists() -> None:
    if not os.path.exists(INDEX_DIR):
        os.mkdir(INDEX_DIR)
        create_index()


def insert_doc(folder_name: str, tags: str, doc_text: str) -> None:
    ix = open_dir(INDEX_DIR)

    with BufferedWriter(index=ix, period=0) as writer:
        writer.add_document(
            **{
                "folder_name": folder_name,
                "tags": tags,
                "text_content": doc_text,
            }
        )
        writer.commit()


def find_doc(tags: list[str] = None, doc_text: str = None) -> list[str]:
    ix = open_dir(INDEX_DIR)
    tag_query, text_query = None, None

    if not tags and not doc_text:
        return []

    if tags:
        tag_query = Or(
            [QueryParser("tags", ix.schema, group=AndGroup).parse(tag) for tag in tags]
        )

    if doc_text:
        text_query = QueryParser("text_content", ix.schema, group=AndGroup).parse(
            doc_text
        )

    with ix.searcher() as searcher:
        if doc_text and tags:
            results = searcher.search(text_query, filter=tag_query)
        elif doc_text:
            results = searcher.search(text_query)
        else:
            results = searcher.search(tag_query)

        folder_names = [res["folder_name"] for res in results]
    return folder_names
