# built-ins
from functools import partial

# my code
from util.constants import TEMP_DIR
from util.upload_util import upload_dialog
from util.shared_util import clear_folder

# packages
from flet import Page, ElevatedButton, Text


def create_init_upload_page(page: Page) -> None:
    page.controls.clear()
    clear_folder(TEMP_DIR)
    page.controls.append(Text("Select "))
    page.controls.append(
        ElevatedButton(
            text="Upload",
            on_click=partial(upload_dialog),
        )
    )
