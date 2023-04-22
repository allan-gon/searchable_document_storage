# if I dont enforce these dimensions, the edit_upload page columns
# are poorly sized. maybe even unusable
WIDTH = 1920
HEIGHT = 1080

# used for navigation
ROUTES = ["/search", "/begin_upload", "/tbd", "/edit_upload"]

# folder with db
INDEX_DIR = "./data/indexdir"
# pyinstaller --onefile --add-data "my_project/models/en_core_web_sm-3.5.0;models" my_script.py
