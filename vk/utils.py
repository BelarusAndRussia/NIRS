import logging.handlers
import argparse
import json
#
from vk.create_session import create_new_session

DEFAULT_LOG_FILE = "app.log"

# Command line parser
parser = argparse.ArgumentParser()
parser.add_argument(
    "-s",
    "--settings",
    action="store",
    dest="SETTING_FILE_NAME",
    help="File with settigs",
    type=str)
parser.add_argument(
    "-t",
    "--tokens",
    action="store",
    dest="TOKENS_FILE_NAME",
    help="File with tokens",
    type=str)
parser.add_argument(
    "-l",
    "--log",
    action="store",
    dest="LOG_FILE_NAME",
    help="File with logs",
    type=str)

command_args = parser.parse_args()
if (command_args.SETTING_FILE_NAME is None) or (command_args.TOKENS_FILE_NAME is None):
    print(f"USAGE: python main.py -s <setting file name> -t <tokens file name> -l [<log file name>]")
    exit()
SETTING_FILE = command_args.SETTING_FILE_NAME
TOKENS_FILE = command_args.TOKENS_FILE_NAME
LOG_FILE = DEFAULT_LOG_FILE if command_args.LOG_FILE_NAME is None else command_args.LOG_FILE_NAME

with open(SETTING_FILE, "r") as read_file:
    SETTINGS = json.load(read_file)

root_logger = logging.getLogger()
root_logger.setLevel(level=SETTINGS["log_level"])
handler = logging.handlers.RotatingFileHandler(LOG_FILE, mode=SETTINGS["mode"], encoding=SETTINGS["encoding"])
handler.setFormatter(logging.Formatter(SETTINGS["format"]))
root_logger.addHandler(handler)


def get_request(URL: str, data: dict):
    """
    Make request
    Arguments:
        URL:str - URL request
        data:dict - parameters for executed request
    Return:
        result: json
    """
    root_logger.debug(f"Execute request '{URL}' with params {data}")
    full_url = f"{URL}?"
    for arg in data.keys():
        full_url += f"{arg}={data[arg]}&"
    full_url = full_url[:-1]
    result = create_new_session().get(full_url)
    return result