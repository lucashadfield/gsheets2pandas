from oauth2client import file, client, tools
from apiclient import discovery
from httplib2 import Http
from typing import Optional, Union
import os
import io
import csv
import pandas
from pandas.core.frame import DataFrame

CLIENT_SECRET_PATH = '~/.gsheets2pandas/client_secret.json'
CLIENT_CREDENTIALS_PATH = '~/.gsheets2pandas/client_credentials.json'
SCOPE = 'https://www.googleapis.com/auth/spreadsheets.readonly'


class GSheetReader:
    """
    Returns an authenticated Google Sheets reader based on configured
    client_secret.json and client_credentials.json files

    :param client_secret_path: path to google API client secret. If omitted, then looks in:
                1. CLIENT_SECRET_PATH environment variable
                2. ~/.pandas_read_gsheet/client_secret.json
    :param client_credentials_path: path to google API client credentials. If the file
    doesn't exist, it will be created through client secret flow. This will spawn a browser
    to complete Google Auth. This might fail in Jupyter/JupyterLab - try running the auth_setup.py file.
    If omitted, then looks in:
                1. CLIENT_CREDENTIALS_PATH environment variable
                2. ~/.pandas_read_gsheet/client_credentials.json
    """
    def __init__(self, client_secret_path: Optional[str] = None, client_credentials_path: Optional[str] = None):
        self.client_secret_path = client_secret_path if client_secret_path is not None \
            else os.environ.get('CLIENT_SECRET_PATH', CLIENT_SECRET_PATH)

        self.client_credentials_path = client_credentials_path if client_credentials_path is not None \
            else os.environ.get('CLIENT_CREDENTIALS_PATH', CLIENT_CREDENTIALS_PATH)

        self.credentials = self._get_credentials()
        self.service = self._get_service()

    def __repr__(self):
        return f'{self.__class__.__name__}({self.client_secret_path}, {self.client_credentials_path})'

    def _get_credentials(self):
        store = file.Storage(os.path.expanduser(self.client_credentials_path))
        credentials = store.get()

        if credentials is None or credentials.invalid:
            credentials = self._refresh_credentials(store)

        return credentials

    def _refresh_credentials(self, store):
        flow = client.flow_from_clientsecrets(os.path.expanduser(self.client_secret_path), scope=SCOPE)
        return tools.run_flow(flow, store, http=Http())

    def _get_service(self):
        return discovery.build('sheets', 'v4', http=self.credentials.authorize(Http()))

    def _sheet_data_to_dataframe(self, data, parse_dates=True):
        with io.StringIO() as buf:
            csv.writer(buf).writerows(data)
            buf.seek(0, 0)
            return pandas.read_csv(buf, parse_dates=list(range(len(data[0]))) if parse_dates else False)

    def fetch_spreadsheet_info(self, spreadsheet_id):
        return self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()

    def fetch_spreadsheet_by_sheet_name(self, spreadsheet_id: str, sheet_name: str, parse_dates: bool = True) -> DataFrame:
        sheet_data = self.service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_name).execute()
        if 'values' in sheet_data:
            return self._sheet_data_to_dataframe(sheet_data['values'], parse_dates)
        return DataFrame()


def read_gsheet(spreadsheet_id: str,
                sheet: Optional[Union[str, int]] = None,
                gsheet_reader: Optional[GSheetReader] = None,
                parse_dates: bool = True,
                **gsheet_kwargs) -> Union[DataFrame, tuple]:

    if gsheet_reader is None:
        gsheet_reader = GSheetReader(**gsheet_kwargs)

    sheets_info = gsheet_reader.fetch_spreadsheet_info(spreadsheet_id)['sheets']
    sheet_names = [s['properties']['title'] for s in sheets_info]

    if sheet is None:
        sheets = sheet_names
    elif isinstance(sheet, str):
        if sheet not in sheet_names:
            raise KeyError(f"sheet '{sheet}' not found. Available sheets are: {tuple(sheet_names)}")
        sheets = [sheet]
    elif isinstance(sheet, int):
        sheets = [sheet_names[sheet]]
    else:
        raise TypeError(f'sheet needs to of type Optional[Union[str, int]]')

    if len(sheets) == 1:
        return gsheet_reader.fetch_spreadsheet_by_sheet_name(spreadsheet_id, sheets[0])

    spreadsheets = []
    for sh in sheets:
        spreadsheet = gsheet_reader.fetch_spreadsheet_by_sheet_name(spreadsheet_id, sh, parse_dates)
        if not spreadsheet.empty:
            spreadsheets.append(spreadsheet)

    if len(spreadsheets) > 1:
        return tuple(spreadsheets)
    elif len(spreadsheets) == 1:
        return spreadsheets[0]
