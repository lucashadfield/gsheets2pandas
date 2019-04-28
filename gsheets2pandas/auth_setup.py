from gsheets2pandas import GSheetReader, CLIENT_SECRET_PATH, CLIENT_CREDENTIALS_PATH
import os
import argparse

parser = argparse.ArgumentParser('Setup auth for GSheetReader')
parser.add_argument('client_secret_path', type=str, help='Full path to client_secret.json file',
                    nargs='?', default=os.environ.get('CLIENT_SECRET_PATH', CLIENT_SECRET_PATH))
parser.add_argument('client_credentials_path', type=str, help='Full path to client_credentials.json file',
                    nargs='?', default=os.environ.get('CLIENT_SECRET_PATH', CLIENT_CREDENTIALS_PATH))

GSheetReader(**vars(parser.parse_args()))
