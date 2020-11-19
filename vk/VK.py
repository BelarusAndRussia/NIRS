import random
#
import requests
#
from main import VERSION, TOKENS, root_logger
from .utils import get_request
from .exceptions import *


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
    try:
        data = get_request(f"https://api.vk.com/method/{method}", data=args)
    except requests.exceptions.Timeout:
        return {"req_err": "TIMEOUT"}
    except requests.exceptions.ConnectionError:
        return {"req_err": "ConnectionError"}
    except requests.exceptions.HTTPError:
        return {"req_err": "HTTPError"}
    keys = list(data.json().keys())
    if "error" in keys:
        if data.json()["error"]["error_code"] == 30:
            raise VkApiPrifileIsPrivate
        if data.json()["error"]["error_code"] == 6:
            raise VkApiToManyExecute
        if data.json()["error"]["error_code"] == 9:
            raise VkApiTooManySameExecute
        if data.json()["error"]["error_code"] == 18:
            raise VkApiDeletedUser
        if data.json()["error"]["error_code"] == 37:
            raise VkApiBannedUser
        if data.json()["error"]["error_code"] == 29:
            raise VkApiLimitReached
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
    friends["result"] = []
    friends["error"] = []
    while flag:
        try:
            res_friends = vkapi_request("friends.get", {"user_id": user_id,
                                                        "count": 5000,
                                                        "offset": i,
                                                        "access_token": random.choice(TOKENS),
                                                        "v": VERSION})
        except VkApiPrifileIsPrivate:
            err = "30: This profile is private"
            friends["error"].append({user_id: err})
            friends["status"] = "fail"
            root_logger.info(f"function: getFriends - handled error: {err}")
            return friends
        except VkApiToManyExecute:
            err = "6: Too many executes"
            friends["error"].append({user_id: err})
            friends["status"] = "fail"
            root_logger.info(f"function: getFriends - handled error: {err}")
            return friends
        except VkApiTooManySameExecute:
            err = "9: Too many same actions"
            friends["error"].append({user_id: err})
            friends["status"] = "fail"
            root_logger.info(f"function: getFriends - handled error: {err}")
            return friends
        except VkApiDeletedUser:
            err = "18: Deleted user"
            friends["error"].append({user_id: err})
            friends["status"] = "fail"
            root_logger.info(f"function: getFriends - handled error: {err}")
            return friends
        except VkApiBannedUser:
            err = "37: Banned user"
            friends["error"].append({user_id: err})
            friends["status"] = "fail"
            root_logger.info(f"function: getFriends - handled error: {err}")
            return friends
        except VkApiLimitReached:
            err = "29: Limit rate"
            friends["error"].append({user_id: err})
            friends["status"] = "fail"
            root_logger.info(f"function: getFriends - handled error: {err}")
            return friends
        except:
            err = "Unknown error"
            friends["error"].append({user_id: err})
            friends["status"] = "fail"
            root_logger.exception(f"function: getFriends - handled error: {err}")
            return friends
        if type(res_friends) == requests.models.Response:
            keys = list(res_friends.json().keys())
        elif type(res_friends) == dict:
            keys = list(res_friends.keys())
        if "req_err" in keys:
            err = res_friends["req_err"]
            friends["error"].append({user_id: err})
            friends["status"] = "fail"
            root_logger.info(f"function: getFriends - handled error: {err}")
            return friends
        root_logger.info(f'function: getFriends - result request:'
                         f' {res_friends.json()["response"]["items"]}')
        if len(res_friends.json()["response"]['items']) == 0:
            flag = False
        for friend in res_friends.json()["response"]['items']:
            friends["result"].append(friend)
        i += 5000
    friends["status"] = "success"
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
                fr_deep["error"].append(fr_2["error"][0])
        fr_deep["status"] = "success"
    except IndexError:
        fr_deep["status"] = "fail"
        root_logger.exception("function: getFriends - handled unknown error")
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
    groups["result"] = []
    groups["error"] = []
    while flag:
        try:
            res_groups = vkapi_request("groups.get", {"user_id": user_id,
                                                      "count": 1000,
                                                      "offset": i,
                                                      "access_token": random.choice(TOKENS),
                                                      "v": VERSION})
        except VkApiPrifileIsPrivate:
            err = "30: This profile is private"
            groups["error"].append({user_id: err})
            groups["status"] = "fail"
            root_logger.info(f"function: getGroups - handled error: {err}")
            return groups
        except VkApiToManyExecute:
            err = "6: Too many executes"
            groups["error"].append({user_id: err})
            groups["status"] = "fail"
            root_logger.info(f"function: getGroups - handled error: {err}")
            return groups
        except VkApiTooManySameExecute:
            err = "9: Too many same actions"
            groups["error"].append({user_id: err})
            groups["status"] = "fail"
            root_logger.info(f"function: getGroups - handled error: {err}")
            return groups
        except VkApiDeletedUser:
            err = "18: Deleted user"
            groups["error"].append({user_id: err})
            groups["status"] = "fail"
            root_logger.info(f"function: getGroups - handled error: {err}")
            return groups
        except VkApiBannedUser:
            err = "37: Banned user"
            groups["error"].append({user_id: err})
            groups["status"] = "fail"
            root_logger.info(f"function: getGroups - handled error: {err}")
            return groups
        except VkApiLimitReached:
            err = "29: Limit rate"
            groups["error"].append({user_id: err})
            groups["status"] = "fail"
            root_logger.info(f"function: getGroups - handled error: {err}")
            return groups
        except:
            err = "Unknown error"
            groups["error"].append({user_id: err})
            groups["status"] = "fail"
            root_logger.exception(f"function: getGroups - handled error: {err}")
            return groups
        if type(res_groups) == requests.models.Response:
            keys = list(res_groups.json().keys())
        elif type(res_groups) == dict:
            keys = list(res_groups.keys())
        if "req_err" in keys:
            err = res_groups["req_err"]
            groups["error"].append({user_id: err})
            groups["status"] = "fail"
            root_logger.info(f"function: getGroups - handled error: {err}")
            return groups
        root_logger.info(f'function: getGroups - result request: {res_groups.json()["response"]["items"]}')
        if len(res_groups.json()["response"]['items']) == 0:
            flag = False
        for group in res_groups.json()["response"]['items']:
            groups["result"].append(group)
        i += 1000
    groups["status"] = "success"
    return groups
