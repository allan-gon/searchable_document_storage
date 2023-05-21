from flet import ControlEvent, FilePickerFileType


def upload_dialog(event: ControlEvent) -> None:
    event.page.overlay[0].pick_files(
        file_type=FilePickerFileType.CUSTOM, allowed_extensions=["pdf"]
    )
