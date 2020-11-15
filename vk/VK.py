import json
import logging.handlers
import random
import argparse
#
from .utils import get_request

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

root_logger = logging.getLogger()
root_logger.setLevel(level=SETTINGS["log_level"])
handler = logging.handlers.RotatingFileHandler(LOG_FILE, mode=SETTINGS["mode"], encoding=SETTINGS["encoding"])
handler.setFormatter(logging.Formatter(SETTINGS["format"]))
root_logger.addHandler(handler)

with open(TOKENS_FILE, "r") as read_file:
    TOKENS = json.load(read_file)["tokens"]


def vkapi_request(method: str, args: dict):
    """
    Make api requests to vk.com
    Arguments:
        method: str – method VkAPI
        args: dict – parameters for executed api-method.
    Return:
        result: dict – VkAPI response json
    """
    root_logger.debug(f"Execute VKAPI method '{method}' with params {args}")
    data = get_request(f"https://api.vk.com/method/{method}", data=args)
    return data


def getFriends(user_id: int):
    """
    Collect friends of user
    Arguments:
        user_id: int – id of user
    Return:
        result: dict – {result: [users_id], error: {id: text_error, ...}, status: success or fail}
    """
    friends = {}
    flag = True
    i = 0
    try:
        friends["result"] = []
        friends["error"] = {}
        while flag:
            res_friends = vkapi_request("friends.get", {"user_id": user_id,
                                                        "count": 5000,
                                                        "offset": i,
                                                        "access_token": random.choice(TOKENS),
                                                        "v": VERSION})
            keys = list(res_friends.json().keys())
            if "error" in keys:
                err = str(res_friends.json()["error"]["error_code"]) + ":" + \
                      res_friends.json()["error"]["error_msg"]
                friends["error"][user_id] = err
                root_logger.info(f"function: getFriends - handled error: {err}")
                break
            else:
                root_logger.info(f'function: getFriends - result request:'
                                 f' {res_friends.json()["response"]["items"]}')
            if len(res_friends.json()["response"]['items']) == 0:
                flag = False
            for friend in res_friends.json()["response"]['items']:
                friends["result"].append(friend)
            i += 5000
        friends["status"] = "success"
    except IndexError:
        friends["status"] = "fail"
        root_logger.exception("Exception occurred")
    return friends


def getFriendsOfFriends(user_id: int):
    """
    Collect friends of friends of user
    Arguments:
        user_id: int – id of user
    Return:
        result: dict – {result: {id: [friends], ...}, error: {id: text_error, ...}, status: success or fail}
    """
    fr_deep = {}
    friends = getFriends(user_id)
    if len(friends['result']) == 0:
        return friends
    try:
        fr_deep["result"] = {}
        fr_deep["error"] = []
        for user in friends["result"]:
            fr_2 = getFriends(user)
            fr_deep["result"][user] = fr_2["result"]
            if fr_2["error"]:
                fr_deep["error"].append(fr_2["error"])
        fr_deep["status"] = "success"
    except IndexError:
        fr_deep["status"] = "fail"
        root_logger.exception("Exception occurred")
    return fr_deep


def getGroups(user_id: int):
    """
    Collect groups of user
    Arguments:
        user_id: int – id of user
    Return:
        result: dict – {result: [groups_id], error: {id: text_error, ...}, status: success or fail}
    """
    groups = {}
    flag = True
    i = 0
    try:
        groups["result"] = []
        groups["error"] = {}
        while flag:
            res_groups = vkapi_request("groups.get", {"user_id": user_id,
                                                      "count": 1000,
                                                      "offset": i,
                                                      "access_token": random.choice(TOKENS),
                                                      "v": VERSION})
            keys = list(res_groups.json().keys())
            if "error" in keys:
                err = str(res_groups.json()["error"]["error_code"]) + ":" + \
                      res_groups.json()["error"]["error_msg"]
                groups["error"][user_id] = err
                root_logger.info(f"function: getGroups - handled error: {err}")
                break
            else:
                root_logger.info(f'function: getGroups - result request: {res_groups.json()["response"]["items"]}')
            if len(res_groups.json()["response"]['items']) == 0:
                flag = False
            for group in res_groups.json()["response"]['items']:
                groups["result"].append(group)
            i += 1000
        groups["status"] = "success"
    except IndexError:
        groups["status"] = "fail"
        root_logger.exception("Exception occurred")
    return groups
