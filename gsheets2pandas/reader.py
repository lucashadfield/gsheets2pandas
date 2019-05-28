from oauth2client import file, client, tools
from apiclient import discovery
from httplib2 import Http
from typing import Optional, Union, List
import os
from pandas.core.frame import DataFrame
from pandas import Timestamp, Timedelta
import io

CLIENT_SECRET_PATH = '~/.gsheets2pandas/client_secret.json'
CLIENT_CREDENTIALS_PATH = '~/.gsheets2pandas/client_credentials.json'
SCOPE = 'https://www.googleapis.com/auth/spreadsheets.readonly'
FIELDS = 'sheets/data/rowData/values(effectiveValue,effectiveFormat)'


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

    def _get_credentials(self) -> client.OAuth2Credentials:
        store = file.Storage(os.path.expanduser(self.client_credentials_path))
        credentials = store.get()

        if credentials is None or credentials.invalid:
            credentials = self._refresh_credentials(store)

        return credentials

    def _refresh_credentials(self, store: file.Storage) -> client.OAuth2Credentials:
        flow = client.flow_from_clientsecrets(os.path.expanduser(self.client_secret_path), scope=SCOPE)
        return tools.run_flow(flow, store, http=Http())

    def _get_service(self) -> discovery.Resource:
        return discovery.build('sheets', 'v4', http=self.credentials.authorize(Http()))

    @staticmethod
    def _timestamp_from_float(f: Union[int, float]) -> Timestamp:
        return Timestamp(1899, 12, 30) + Timedelta(days=f)

    def _extract_cell_value(self, cell: dict) -> Union[int, float, bool, str, Timestamp]:
        try:
            cell_type, cell_value = list(cell['effectiveValue'].items())[0]
        except KeyError:
            cell_value = None
        else:
            if cell_type == 'numberValue':
                try:
                    dt_type = cell['effectiveFormat']['numberFormat']['type']
                    if dt_type == 'DATE_TIME' or dt_type == 'DATE':
                        cell_value = self._timestamp_from_float(cell_value)
                except KeyError:
                    pass

        return cell_value

    def _sheet_data_to_dataframe(self, data: list, header=True) -> DataFrame:
        data_list = [[self._extract_cell_value(cell) for cell in row['values']] for row in data]

        return DataFrame(data_list[1:], columns=data_list[0]) if header else DataFrame(data_list)

    def fetch_spreadsheet(self, spreadsheet_id: str, sheet_name: Optional[str] = None, header: bool = True) -> List[DataFrame]:
        spreadsheet_data = self.service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            ranges=sheet_name,
            fields=FIELDS
        ).execute()

        return [self._sheet_data_to_dataframe(s['data'][0]['rowData'], header) if s['data'][0] else DataFrame()
                for s in spreadsheet_data['sheets']]

    def fetch_spreadsheet_info(self, spreadsheet_id: str) -> dict:
        return self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()


def read_gsheet(spreadsheet_id: str,
                sheet: Optional[Union[str, int]] = None,
                header: bool = True,
                gsheet_reader: Optional[GSheetReader] = None,
                **gsheet_kwargs) -> Union[DataFrame, tuple]:

    if gsheet_reader is None:
        gsheet_reader = GSheetReader(**gsheet_kwargs)

    if sheet is not None:
        sheet_names = [s['properties']['title'] for s in gsheet_reader.fetch_spreadsheet_info(spreadsheet_id)['sheets']]
        if isinstance(sheet, str):
            if sheet not in sheet_names:
                raise KeyError(f"sheet '{sheet}' not found. Available sheets are: {sheet_names}")
        elif isinstance(sheet, int):
            sheet = sheet_names[sheet]
        else:
            raise TypeError(f'sheet needs to of type Optional[Union[str, int]]')

    spreadsheet = gsheet_reader.fetch_spreadsheet(spreadsheet_id, sheet, header)

    if len(spreadsheet) > 1:
        spreadsheet = [s for s in spreadsheet if not s.empty]

    return tuple(spreadsheet) if len(spreadsheet) > 1 else spreadsheet[0]
