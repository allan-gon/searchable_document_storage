# if I dont enforce these dimensions, the edit_upload page columns
# are poorly sized. maybe even unusable
WIDTH = 1920
HEIGHT = 1080

# used for navigation
ROUTES = ["/search", "/begin_upload", "/edit_upload"]
# all relative to root folder
SPACY_MODEL_PATH = "./model/en_core_web_sm-3.5.0"
DATA_DIR = "./data"
TEMP_DIR = f"{DATA_DIR}/temp"
DOCS_DIR = f"{DATA_DIR}/docs"
TAGS_FILE = f"{DATA_DIR}/tags"
VEC_DB_DIR = f"{DATA_DIR}/db"
PDF_NAME = "selected_doc.pdf"
COLLECTION_NAME = "docs"
