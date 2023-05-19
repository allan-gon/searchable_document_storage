# my code
from src.constants import TEMP_DIR
from src.helper import clear_folder

# packages
from flet import Page, ElevatedButton, Text, FilePickerFileType


def create_init_upload_page(page: Page) -> None:
    page.controls.clear()
    clear_folder(TEMP_DIR)
    page.controls.append(Text("Only select images from a single file"))
    page.controls.append(
        ElevatedButton(
            text="Upload",
            on_click=lambda _: page.overlay[0].pick_files(
                file_type=FilePickerFileType.IMAGE, allow_multiple=True
            ),
        )
    )
