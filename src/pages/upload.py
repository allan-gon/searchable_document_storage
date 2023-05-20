# built-ins
from functools import partial

# my code
from src.constants import TEMP_DIR
from src.helper import clear_folder, upload_dialog

# packages
from flet import Page, ElevatedButton, Text, FilePickerFileType, ControlEvent


def create_init_upload_page(page: Page) -> None:
    page.controls.clear()
    clear_folder(TEMP_DIR)
    page.controls.append(Text("Only select images from a single file"))
    page.controls.append(
        ElevatedButton(
            text="Upload",
            on_click=partial(upload_dialog),
        )
    )
