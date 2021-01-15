import argparse
import logging.handlers
#
import os
import sys
#
MAIN_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(MAIN_DIR, 'irequests/'))
sys.path.insert(0, os.path.join(MAIN_DIR, 'settings/'))
sys.path.insert(0, os.path.join(MAIN_DIR, 'vk/'))
#
from settings import settings
from vk import VK

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
    vk_module = VK(settings)
    print(vk_module.getWhoLikes('photo', 1, 456264771, max_likes=1000))