import argparse
import json
import logging.handlers
#
import vk

DEFAULT_LOG_FILE = "app.log"
VERSION = '5.95'

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

with open(TOKENS_FILE, "r") as read_file:
    TOKENS = json.load(read_file)["tokens"]

root_logger = logging.getLogger()
root_logger.setLevel(level=SETTINGS["log_level"])
handler = logging.handlers.RotatingFileHandler(LOG_FILE, mode=SETTINGS["mode"], encoding=SETTINGS["encoding"])
handler.setFormatter(logging.Formatter(SETTINGS["format"]))
root_logger.addHandler(handler)


if __name__ == '__main__':
    users = [244864074, 89767667, 153988262, 135707636, 257875098, 124315477,
             210121381, 136389672, 135707636, 1650874, 2429484]
    print(vk.getFriends(89767667))
