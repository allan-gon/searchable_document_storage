# Notes for others
- this will no run properly because the model and data folders are missing.
- this is expected as they are git ignored because too big
- if you somehow figure out what is in those folders and get it run the startup is slow because models get loaded

# Notes for self
```
actual: pyinstaller -w --icon=icon.ico --hidden-import=dbm.dumb --add-data "model;model" --noconfirm main.py
debug: pyinstaller --icon=icon.ico --hidden-import=dbm.dumb --add-data "model;model" --noconfirm main.py
```
- if create tag then delete, drop down till have value
- maybe pack just the app
- copy over the model, data gets made auto

```
flet pack .\main.py --icon icon.ico --hidden-import=dbm.dumb
cp -r ./model ./dist
```
- i think it fails to make the view because the dir thing again but because all one binary abs dir is wrong
- the flet thing makes icon work but teh edit_upload view isn't made