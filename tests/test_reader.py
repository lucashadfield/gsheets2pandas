from gsheets2pandas.reader import GSheetReader, read_gsheet
from pandas.core.frame import DataFrame
from pandas import Timestamp
import pytest
import json
import os
from unittest.mock import Mock, patch

GSHEET_INFO = os.path.join(os.path.dirname(__file__), 'resources/gsheets_info.json')
GSHEET_DATA = os.path.join(os.path.dirname(__file__), 'resources/gsheets_data.json')


def fetch_spreadsheet_side_effect(spreadsheetId, ranges=None, fields=None):
    mocked_data = Mock()

    with open(GSHEET_INFO) as f:
        sheet_info = json.load(f)

    if fields is None:
        mocked_data.execute.return_value = sheet_info[spreadsheetId]
        return mocked_data


    with open(GSHEET_DATA) as f:
        data = json.load(f)

    if ranges is None:
        mocked_data.execute.return_value = data[spreadsheetId]
    else:
        sheet_id_map = {s['properties']['title']: i for i, s in enumerate(sheet_info[spreadsheetId]['sheets'])}
        data[spreadsheetId]['sheets'] = [data[spreadsheetId]['sheets'][sheet_id_map[ranges]]]

    mocked_data.execute.return_value = data[spreadsheetId]

    return mocked_data


@pytest.fixture(scope='session')
@patch('gsheets2pandas.reader.file')
@patch('gsheets2pandas.reader.discovery')
def mocked_reader(mock_discovery, mock_file):
    mock_file.Storage.return_value.get.return_value.invalid = False

    reader = GSheetReader()
    reader.service.spreadsheets.return_value.get.side_effect = fetch_spreadsheet_side_effect

    return reader


@patch('gsheets2pandas.reader.tools')
@patch('gsheets2pandas.reader.client')
@patch('gsheets2pandas.reader.file')
@patch('gsheets2pandas.reader.discovery')
def test_refresh_credentials(mock_discovery, mock_file, mock_client, mock_tools):
    mock_file.Storage.return_value.get.return_value.invalid = True
    reader = GSheetReader('client_secret_path', 'client_credentials_path')
    reader.service.spreadsheets.return_value.get.side_effect = fetch_spreadsheet_side_effect
    df = read_gsheet('SPREADSHEET_1_SHEET_0_EMPTY')

    assert isinstance(df, DataFrame)
    assert repr(reader) == 'GSheetReader(client_secret_path, client_credentials_path)'


def test_1_sheet_0_empty(mocked_reader):
    df = read_gsheet('SPREADSHEET_1_SHEET_0_EMPTY', sheet='Sheet1', gsheet_reader=mocked_reader)

    assert isinstance(df, DataFrame)
    assert df.shape == (6, 4)


def test_1_sheet_0_empty_no_header(mocked_reader):
    df = read_gsheet('SPREADSHEET_1_SHEET_0_EMPTY', header=False, gsheet_reader=mocked_reader)
    assert isinstance(df, DataFrame)
    assert df.shape == (7, 4)


def test_3_sheet_0_empty(mocked_reader):
    df = read_gsheet('SPREADSHEET_3_SHEET_0_EMPTY', gsheet_reader=mocked_reader)
    assert isinstance(df, tuple)
    assert len(df) == 3


def test_3_sheet_1_empty(mocked_reader):
    df = read_gsheet('SPREADSHEET_3_SHEET_1_EMPTY', gsheet_reader=mocked_reader)
    assert isinstance(df, tuple)
    assert len(df) == 2


def test_3_sheet_2_empty(mocked_reader):
    df = read_gsheet('SPREADSHEET_3_SHEET_2_EMPTY', gsheet_reader=mocked_reader)
    assert isinstance(df, DataFrame)
    assert df.shape == (4, 4)


def test_read_by_sheet_name(mocked_reader):
    df = read_gsheet('SPREADSHEET_3_SHEET_1_EMPTY', 'Sheet1', gsheet_reader=mocked_reader)
    assert isinstance(df, DataFrame)
    assert df.shape == (4, 5)


def test_read_empty_by_sheet_name(mocked_reader):
    df = read_gsheet('SPREADSHEET_3_SHEET_2_EMPTY', 'Sheet2', gsheet_reader=mocked_reader)
    assert isinstance(df, DataFrame)
    assert df.empty


def test_read_by_sheet_index(mocked_reader):
    df = read_gsheet('SPREADSHEET_3_SHEET_1_EMPTY', 1, gsheet_reader=mocked_reader)
    assert isinstance(df, DataFrame)
    assert df.shape == (4, 4)


def test_read_empty_by_sheet_index(mocked_reader):
    df = read_gsheet('SPREADSHEET_3_SHEET_2_EMPTY', 2, gsheet_reader=mocked_reader)
    assert isinstance(df, DataFrame)
    assert df.empty


def test_invalid_sheet_name(mocked_reader):
    with pytest.raises(KeyError):
        read_gsheet('SPREADSHEET_1_SHEET_0_EMPTY', 'Invalid Sheet', gsheet_reader=mocked_reader)


def test_invalid_sheet_index(mocked_reader):
    with pytest.raises(IndexError):
        read_gsheet('SPREADSHEET_1_SHEET_0_EMPTY', 1, gsheet_reader=mocked_reader)


def test_invalid_sheet_argument_type(mocked_reader):
    with pytest.raises(TypeError):
        read_gsheet('SPREADSHEET_1_SHEET_0_EMPTY', 1.2, gsheet_reader=mocked_reader)


def test_types(mocked_reader):
    s = read_gsheet('SPREADSHEET_1_SHEET_0_EMPTY', gsheet_reader=mocked_reader)['types']
    for x, target_type in zip(s, [int, float, bool, str, Timestamp]):
        assert isinstance(x, target_type)


def test_repr(mocked_reader):
    assert repr(mocked_reader) == 'GSheetReader(~/.gsheets2pandas/client_secret.json, ~/.gsheets2pandas/client_credentials.json)'
