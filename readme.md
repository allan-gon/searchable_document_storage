# To build

```
flet pack .\main.py --icon icon.ico --hidden-import=dbm.dumb
```
- once this finishes move the model folder (omitted on github) into the dist folder

# To install
- download and run this installer: https://tinyurl.com/2p8h2k2f
    - **NOTE**: will obviously be detected as virus since it's a python exe. Simply allow it as a threat once it's quarantined and when running the installer click run anyways

# TODO
- when uploading view misbehaves. possibly related to 1st image or to an empty folder
- speed up startup
    - use larger spacy model
- figure out where function out to go im throwing eveything that is used in more than one file or can be general into helper and it's starting to get crowded

# Dev stuff
- to check if works as binary
```
pyinstaller --hidden-import=dbm.dumb --noconfirm --onefile main.py
```
- btw manually moved model folder into that dir

# Changes
- migrate to pdf only support
- only allow pdf upload
    - behind the scenes need images
        - ocr them
    - show preview, still allow removing of pages?
    - save the possibly modified pdf and launch that, no need for storing images
- discard shows up in the snackbar

- upload more should dissapear
- still need a preview
- still need ability to remove
- saving means creating a pdf of the left over images
