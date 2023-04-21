from flet import app, FilePicker, Page
from src.constants import WIDTH, HEIGHT
from src.helper import create_nav_bar, ensure_folders_exist, copy_selected_files
from src.pages.upload import create_init_upload_page
from src.pages.edit_upload import create_edit_upload_page
from src.pages.search import create_search_page
from src.pages.tbd import tbd


def main(page: Page):
    # make storage folders on 1st start or if folders get deleted
    ensure_folders_exist()

    # Basic app setup
    page.title = "File Storage"
    page.window_width = WIDTH
    page.window_height = HEIGHT
    page.window_resizable = False
    # File picker needed in upload and edit_upload page
    page.overlay.append(FilePicker(on_result=copy_selected_files))

    def route_change(_):
        """Handles navigation"""
        # clear the page
        page.controls.clear()

        # draw page accordingly
        match page.route:
            case "/search":
                create_search_page(page)
            case "/begin_upload":
                create_init_upload_page(page)
            case "/edit_upload":
                create_edit_upload_page(page)
            case "/tbd":
                tbd(page)
        page.update()

    page.on_route_change = route_change
    # nav bar is part of page not controls so it's persistent across pages
    # makes switching pages look better
    page.navigation_bar = create_nav_bar(page)
    page.go("/search")
    page.update()


if __name__ == "__main__":
    app(target=main)
