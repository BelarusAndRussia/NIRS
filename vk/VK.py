import json
import logging.handlers
import random

from .create_session import create_new_session


root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler("app.log", mode='w', maxBytes=5*1024*1024, encoding="utf-8")
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
root_logger.addHandler(handler)

VERSION = '5.95'
with open("tokens/vk_tokens.json", "r") as read_file:
    TOKENS = json.load(read_file)['tokens']


class VK:
    def getFriends(self, user_id):
        friends = {}
        flag = True
        i = 0
        try:
            friends["result"] = []
            friends["error"] = {}
            while flag:
                url = f'https://api.vk.com/method/friends.get?user_id={user_id}&fields=city,country&count=5000&' \
                      f'offset={i}&access_token={random.choice(TOKENS)}&v={VERSION}'
                res_friends = create_new_session().get(url)
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
                    friends["result"].append(friend["id"])
                i += 5000
            friends["status"] = "success"
        except IndexError:
            friends["status"] = "fail"
            root_logger.exception("Exception occurred")
        return friends

    def getFriendsOfFriends(self, user_id):
        fr_deep = {}
        friends = self.getFriends(user_id)
        if len(friends['result']) == 0:
            return friends
        try:
            fr_deep["result"] = {}
            fr_deep["error"] = []
            for user in friends["result"]:
                fr_2 = self.getFriends(user)
                fr_deep["result"][user] = fr_2["result"]
                if fr_2["error"]:
                    fr_deep["error"].append(fr_2["error"])
            fr_deep["status"] = "success"
        except IndexError:
            fr_deep["status"] = "fail"
            root_logger.exception("Exception occurred")
        return fr_deep

    def getGroups(self, user_id):
        groups = {}
        flag = True
        i = 0
        try:
            groups["result"] = []
            groups["error"] = {}
            while flag:
                url = f'https://api.vk.com/method/groups.get?user_id={user_id}&fields=city,country&' \
                      f'count=1000&offset={i}&access_token={random.choice(TOKENS)}&v={VERSION}'
                res_groups = create_new_session().get(url)
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
