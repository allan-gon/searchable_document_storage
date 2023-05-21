# To build

```
flet pack .\main.py --icon icon.ico --hidden-import=dbm.dumb
```
- once this finishes move the model folder (omitted on github) into the dist folder

# To install
- download and run this installer: https://tinyurl.com/2p8h2k2f
    - **NOTE**: will obviously be detected as virus since it's a python exe. Simply allow it as a threat once it's quarantined and when running the installer click run anyways

# TODO
- speed up startup
    - use larger spacy model

# Dev stuff
- to check if works as binary
```
pyinstaller --hidden-import=dbm.dumb --noconfirm --onefile main.py
```
- btw manually moved model folder into that dir
