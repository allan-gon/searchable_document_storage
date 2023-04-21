from flet import (
    Page,
    NavigationBar,
    NavigationDestination,
    icons,
    FilePickerResultEvent,
)
from src.constants import ROUTES
from os.path import exists
from os import mkdir, listdir
from shutil import copy


def create_nav_bar(page: Page) -> NavigationBar:
    return NavigationBar(
        destinations=[
            NavigationDestination(icon=icons.SEARCH),
            NavigationDestination(icon=icons.FILE_UPLOAD),
            NavigationDestination(icon=icons.QUESTION_MARK),
        ],
        selected_index=0,
        on_change=lambda e: page.go(ROUTES[e.control.selected_index]),
    )


def ensure_folders_exist() -> None:
    # create folders if they're missing
    if not exists("./data/"):
        mkdir("./data")
        mkdir("./data/temp")
    elif not exists("./data/temp"):
        mkdir("./data/temp")
    # create file if missing
    if not exists("./data/tags"):
        with open("./data/tags", "w") as file:
            file.write()


def intermediate(res: FilePickerResultEvent, route: str) -> None:
    """ """
    res.page.go("/intermediate")
    res.page.go(route)


def copy_selected_files(res: FilePickerResultEvent) -> None:
    if res.files:
        for file in res.files:
            if file not in listdir("./data/temp"):
                copy(file.path, "./data/temp")
    intermediate(res, "/edit_upload")
