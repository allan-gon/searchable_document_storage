from flet import Page, ElevatedButton, Text, FilePickerFileType
from os import listdir, remove


def create_init_upload_page(page: Page) -> None:
    page.controls.clear()
    for file in listdir("./data/temp"):
        remove(f"./data/temp/{file}")
    page.controls.append(Text("Only select images from a single file"))
    page.controls.append(
        ElevatedButton(
            text="Upload",
            on_click=lambda _: page.overlay[0].pick_files(
                file_type=FilePickerFileType.IMAGE, allow_multiple=True
            ),
        )
    )
