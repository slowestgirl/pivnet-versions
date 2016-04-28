# PivNet Versions
Run this script to create an xlsx spreadsheet of all dependencies for all PivNet products you have access to. You'll need an API token to run this, which you can find on your "Edit Profile" page on PivNet.

## Instrustionc
Just run `python versions.py` from the directory.

You may need to `pip install` one or more of the following dependencies.

## Dependencies
  - `requests`
  - `getpass`
  - `openpyxl`
  - `time`

# Known Issues
 - If a product has no releases, nothing will show up on the tab. If a product has releases but has no dependencies, nothing will show up on the tab.
 - This takes a long time (on the order of 7 minutes) to run.
