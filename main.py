import argparse
import datetime
import json
import logging.handlers
import time
#
import os
import sys
#
from math import floor

MAIN_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(MAIN_DIR, 'irequests/'))
sys.path.insert(0, os.path.join(MAIN_DIR, 'settings/'))
sys.path.insert(0, os.path.join(MAIN_DIR, 'vk/'))
sys.path.insert(0, os.path.join(MAIN_DIR, 'inst/'))
sys.path.insert(0, os.path.join(MAIN_DIR, 'analysis/'))
#
from settings import settings
from vk import VK
from analysis import Analysis
from scrapping import Scrapper

__VERSION__ = '0.1.1'

def cli_args_parser_init():
    """
    Осуществляет инициализацию парсера аргументов коммандной строки
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--settings",
        action="store",
        dest="SETTING_FILE_NAME",
        help="File with settigs",
        type=str)
    parser.add_argument(
        "-l",
        "--log",
        action="store",
        dest="LOG_FILE_NAME",
        help="File with logs",
        type=str)
    return parser


def log_init():
    root_logger = logging.getLogger()
    root_logger.setLevel(level=settings.log_level)
    handler = logging.handlers.RotatingFileHandler(
        settings.log_file, 
        maxBytes=settings.log_max_bytes_in_file, 
        encoding=settings.encoding)
    handler.setFormatter(logging.Formatter(settings.log_format))
    root_logger.addHandler(handler)


def init_app():
    # parse cli arguments
    parser = cli_args_parser_init()
    cli_args = parser.parse_args()
    # init settings
    if cli_args.SETTING_FILE_NAME:
        settings.load_JSON(cli_args.SETTING_FILE_NAME)
    # init log
    if cli_args.LOG_FILE_NAME:
        settings.log_file = cli_args.LOG_FILE_NAME  
    log_init()


if __name__ == '__main__':
    init_app()
    #
    #vk_module = VK(settings)
    analysis = Analysis(settings)
    print(analysis.vk_get_age(186101748))

    # fsb_members = vk_module.get_group_members(-56274312)["result"]
    # fsb_members_friends = []
    # for member in fsb_members:
    #     buff_friends = []
    #     mem_friends = vk_module.get_friends(member)["result"]
    #     if mem_friends:
    #         for mem_fr in mem_friends:
    #             if mem_fr in fsb_members:
    #                 buff_friends.append(mem_fr)
    #     fsb_members_friends.append({member: buff_friends})
    # with open("fsb_friends.json", "w") as wf:
    #     json.dump(fsb_members_friends, wf)



