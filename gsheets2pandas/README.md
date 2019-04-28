# gsheets2pandas - python interface for reading Google Sheets into pandas DataFrames

[![Python 3.6](https://img.shields.io/badge/python-3.6+-blue.svg)](#)


### Setup:

##### Google API setup
This assumes you are running Jupyter locally on port 8888. If not, adjust the steps accordingly. The port 8080 configs are needed regardless.

1. Go to: https://console.developers.google.com/apis
2. Create a new project
3. Find and enable "Google Sheets API"
4. Create Credentials → `OAuth client ID`
5. Add http://localhost:8888 and http://localhost:8080 to list of "Authorised JavaScript origins"
6. Add http://localhost:8888/ and http://localhost:8080/ to list of "Authorised redirect URIs" **Note: trailing / on each URI**
7. Save and download as json. Save to `~/.gsheets2pandas/client_secret.json`. If you save it elsewhere you need to either need to set the `CLIENT_SECRET_PATH` environment variable or pass in `client_secret_path` when using gsheets2pandas

##### gsheets2pandas setup
1. `git clone https://github.com/lucashadfield/gsheets2pandas.git`
2. `pip install gsheets2pandas`



### Notes
The first time you call `gsheets2pandas.read_gsheet(...)` or `gsheets2pandas.GSheetReader()` it will run the client credentials flow that will create the client_credentials.json file needed for authentication. This flow spawns a browser window that directs you to authorise the API app you configured. If the flow fails to spawn a browser (if being used in Jupyter or Jupyter Lab) you can try running the `auth_setup.py` script in the installation directory.

The client_credentials file be saved/loaded from one of the following locations, in order:
1. Path at `client_credentials_path` passed into `gsheets2pandas.read_gsheet(client_credentials_path=...)` or `gsheets2pandas.GSheetReader(client_credentials_path=...)`
2. Location specified by the `CLIENT_CREDENTIALS_PATH` environment variable
3. Default location `~/.gsheets2pandas/client_credentials.json`



### Basic Usage

##### Read a Google Sheet
If there are multiple non-empty sheets in the specified spreadsheet, they will all be returned in a tuple of pandas DataFrames. If there is only 1 valid, sheet, it will be returned as a pandas DataFrame.
```python
import gsheets2pandas
df = gsheets2pandas.read_gsheet(spreadsheet_id='SHEET_ID_HERE')
```

##### Read a specific sheet by name from a Google Sheet
Returns a pandas DataFrame
```python
import gsheets2pandas
df = gsheets2pandas.read_gsheet(spreadsheet_id='SHEET_ID_HERE', sheet='Sheet1')
```

##### Read a specific sheet by index from a Google Sheet
Returns a pandas DataFrame
```python
import gsheets2pandas
df = gsheets2pandas.read_gsheet(spreadsheet_id='SHEET_ID_HERE', sheet=0)
```


### To Do
1. Tests and Coverage
2. More detailed Google API setup instructions

