# To build

```
flet pack .\main.py --icon icon.ico --hidden-import=dbm.dumb
```
- once this finishes move the model folder (omitted on github) into the dist folder

# To install
<!-- need to update link when new version compiles -->
- download and run this installer: https://tinyurl.com/bdctfstw
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

# Tests
- **NOTE** any points which aren't sequential are yet to be tested

## Basic
- app starts up
- icon appears correctly on exe
- icon appears correctly on running app
- correct file structure is created (mainly the data folder and it's content)
- can navigate between search and upload page via the nav bar
- window is re-sizable

## Search Page
- searching an empty db does nothing
- select/deselect empty tags does nothing
- contains search bar/button
- contains tag dropdown and accompanying select/deselect

- filterable
- selecting/deselecting when dropdown is None does nothing

## Upload Page
- the upload button an text appear
- clicking the button opens os file picker
    - only pdfs are selectable
- on cancel snack bar lets you know
- on proper selection view pops up

## Edit Upload View
- can see pdf preview
- can remove pages
- can select, deselect, create, and delete tags
- selecting tags makes button with the tag as it's text appear
- discard and save collapse teh view returning to upload page
- save in due time shows a green snackbar
- discard shows a red snack bar

# Questions
- ocr is async so what if another file is uploaded and set to be ocr'd in that time?
    - does another instance spawn? is there a problem?
    - does it know the resource is in use so it awaits?
    - if it doesn't await
        - there's a race condition for insertion

<!-- i have a function that setups up the layout for a page in my app. One element in the layout is the save button whose callback does some io then calls an async function that uses a model. The result if the async function is used to insert into a database. To be clear everything is syncronous except for the async function my callback uses. It's this way because teh model may take time to give a result but the user doesn't need to know that and have a slow experience. But since this allows the user to continue using the app, what happens if they click the save button again before teh model is finished or the database is written to? Does it wait for the resources or do i have a race condition? -->

# Problem
- if you upload >1 times in a session, the 1st image of your document will show the 1st image of the 1st upload.
    - This is not a resource or path issue as I tested by inspecting the path and opening teh asset before it's loading into the image class
    - path does contain both \\ & / but switching to either doesn't seem to affect this
- the list view is certainly getting garbage collected

- probably want to use better model, searches aren't great
