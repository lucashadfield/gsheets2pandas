from gsheets2pandas.reader import GSheetReader, read_gsheet
from pandas.core.frame import DataFrame
from pandas import Timestamp
import os
import pytest

SPREADSHEET_1_SHEET_0_EMPTY = '1o6zf4aV9yqD-69qN52bPDUTFhAO3inwvkLAkIhXJoIA'
SPREADSHEET_3_SHEET_0_EMPTY = '1e4xhGYcwCg_p9dU8H-ZmAycICARAgNVjBzaZZlllmzY'
SPREADSHEET_3_SHEET_1_EMPTY = '1n4AnD9QES42F3TQBBAW3Z_uMIv0BnXAf18ZU4G_S2_E'
SPREADSHEET_3_SHEET_2_EMPTY = '12kKBmAtE7y0ToCLoYYF0LzfsdRtcYVaAg7GLVWeiZec'


@pytest.fixture(scope='session')
def gsheet_reader():
    return GSheetReader()


def test_gsheetreader_default():
    GSheetReader()


def test_gsheetreader_env():
    os.environ['CLIENT_SECRET_PATH'] = '~/.gsheets2pandas/client_secret.json'
    os.environ['CLIENT_CREDENTIALS_PATH'] = '~/.gsheets2pandas/client_credentials.json'
    GSheetReader()
    del os.environ['CLIENT_SECRET_PATH']
    del os.environ['CLIENT_CREDENTIALS_PATH']


def test_gsheetreader_kwargs():
    GSheetReader('~/.gsheets2pandas/client_secret.json', '~/.gsheets2pandas/client_credentials.json')


def test_1_sheet_0_empty():
    df = read_gsheet(SPREADSHEET_1_SHEET_0_EMPTY, gsheet_reader=None)
    assert isinstance(df, DataFrame)
    assert df.shape == (6, 4)


def test_1_sheet_0_empty_no_header():
    df = read_gsheet(SPREADSHEET_1_SHEET_0_EMPTY, header=False, gsheet_reader=None)
    assert isinstance(df, DataFrame)
    assert df.shape == (7, 4)


def test_3_sheet_0_empty(gsheet_reader):
    df = read_gsheet(SPREADSHEET_3_SHEET_0_EMPTY, gsheet_reader=gsheet_reader)
    assert isinstance(df, tuple)
    assert len(df) == 3


def test_3_sheet_1_empty(gsheet_reader):
    df = read_gsheet(SPREADSHEET_3_SHEET_1_EMPTY, gsheet_reader=gsheet_reader)
    assert isinstance(df, tuple)
    assert len(df) == 2


def test_3_sheet_2_empty(gsheet_reader):
    df = read_gsheet(SPREADSHEET_3_SHEET_2_EMPTY, gsheet_reader=gsheet_reader)
    assert isinstance(df, DataFrame)
    assert df.shape == (4, 3)


def test_read_by_sheet_name(gsheet_reader):
    df = read_gsheet(SPREADSHEET_3_SHEET_1_EMPTY, 'Sheet1', gsheet_reader=gsheet_reader)
    assert isinstance(df, DataFrame)
    assert df.shape == (4, 3)


def test_read_empty_by_sheet_name(gsheet_reader):
    df = read_gsheet(SPREADSHEET_3_SHEET_2_EMPTY, 'Sheet2', gsheet_reader=gsheet_reader)
    assert isinstance(df, DataFrame)
    assert df.empty


def test_read_by_sheet_index(gsheet_reader):
    df = read_gsheet(SPREADSHEET_3_SHEET_1_EMPTY, 1, gsheet_reader=gsheet_reader)
    assert isinstance(df, DataFrame)
    assert df.shape == (4, 3)


def test_read_empty_by_sheet_index(gsheet_reader):
    df = read_gsheet(SPREADSHEET_3_SHEET_2_EMPTY, 2, gsheet_reader=gsheet_reader)
    assert isinstance(df, DataFrame)
    assert df.empty


def test_invalid_sheet_name(gsheet_reader):
    with pytest.raises(KeyError):
        read_gsheet(SPREADSHEET_1_SHEET_0_EMPTY, 'Invalid Sheet', gsheet_reader=gsheet_reader)


def test_invalid_sheet_index(gsheet_reader):
    with pytest.raises(IndexError):
        read_gsheet(SPREADSHEET_1_SHEET_0_EMPTY, 1, gsheet_reader=gsheet_reader)


def test_invalid_sheet_argument_type(gsheet_reader):
    with pytest.raises(TypeError):
        read_gsheet(SPREADSHEET_1_SHEET_0_EMPTY, 1.2, gsheet_reader=gsheet_reader)


def test_types(gsheet_reader):
    s = read_gsheet(SPREADSHEET_1_SHEET_0_EMPTY, gsheet_reader=gsheet_reader)['types']
    for x, target_type in zip(s, [int, float, bool, str, Timestamp]):
        assert isinstance(x, target_type)
