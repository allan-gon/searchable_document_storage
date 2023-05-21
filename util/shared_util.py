# built-ins
from os import listdir, remove

# packages
from flet import ControlEvent, Row, Dropdown, ElevatedButton


def select_tag(event: ControlEvent, btns: Row, drop: Dropdown) -> None:
    # when deleted, value must be changed
    if drop.value:
        for btn in btns.controls:
            if drop.value == btn.text:
                break
        else:
            btns.controls.append(ElevatedButton(text=drop.value))
            event.page.update()


def deselect_tag(event: ControlEvent, btns: Row, drop: Dropdown) -> None:
    if drop.value:
        for btn in btns.controls:
            if btn.text == drop.value:
                btns.controls.remove(btn)
                event.page.update()
                break


def clear_folder(folder) -> None:
    """Remove files from a specified folder, usually the TEMP_DIR"""
    for file in listdir(folder):
        remove(f"{folder}/{file}")


def remove_stops_and_lemmatize(doc):
    return [token.lemma_ for token in doc if not token.is_stop]


def get_embedding(text, nlp):
    doc = nlp(text)
    lemmatized_tokens = remove_stops_and_lemmatize(doc)
    lemmatized_doc = nlp(" ".join(lemmatized_tokens))
    return lemmatized_doc.vector
