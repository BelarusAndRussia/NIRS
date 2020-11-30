import random
#
import logging
import json
import re
#
from irequests import request
from .exceptions import *
from settings import Settings

log = logging.getLogger(__name__)


class VK:
    """ Модуль работы с VK """

    def __init__(self, settings):
        if type(settings) is not Settings:
            raise VkInvalidSettings
        self.API_VERSION = 5.101
        self.settings = settings
        self._TOKENS = []
        if settings.tokens_file_vk:
            self.load_tokens(settings.tokens_file_vk)


    def load_tokens(self, fname):
        self._TOKENS = list(map(str.strip, open(
            fname, "r", encoding=self.settings.encoding).readlines()))


    def _vkapi_request(self, method: str, args: dict):
        """
        Make api requests to vk.com
        Arguments:
            method: str – method VkAPI
            args: dict – parameters for executed api-method.
        Return:
            result: dict – VkAPI response json
        """
        log.debug(f"Execute VKAPI method '{method}' with params {args}")
        req_data = {
            "access_token": random.choice(self._TOKENS),
            "v": self.API_VERSION
        }
        if args: req_data.update(args)
        data = request(f"https://api.vk.com/method/{method}", req_data, format_JSON=True)
        if "req_err" in data:
            log.error(f"VKApi request error! {data}")
        elif "error" in data:
            if data["error"]["error_code"] == 30:
                raise VkApiProfileIsPrivate
            elif data["error"]["error_code"] == 6:
                raise VkApiToManyExecute
            elif data["error"]["error_code"] == 9:
                raise VkApiTooManySameExecute
            elif data["error"]["error_code"] == 18:
                raise VkApiDeletedUser
            elif data["error"]["error_code"] == 37:
                raise VkApiBannedUser
            elif data["error"]["error_code"] == 29:
                raise VkApiLimitReached
            elif data["error"]["error_code"] == 5:
                raise VkInvalidToken
            else:
                raise BaseVkError
        return data


    def result(self, status, data, errors):
        if errors:
            log.error(json.dumps(errors))
        return {
            "status": status,
            "error": errors,
            "result": data,
        }


    def getFriends(self, user_id: int, max_friends: int=10000):
        """
        Collect friends of user
        Arguments:
            user_id: int – id of user
        Return:
            result: dict – {result: [users_id], error: {id: text_error, ...}, status: success or fail}
        """
        friends = []
        profiles_per_iteration = 5000
        for offset_profiles in range(0, max_friends, profiles_per_iteration):
            try:
                res_friends = self._vkapi_request(
                    "friends.get", 
                    {
                        "user_id": user_id,
                        "count": profiles_per_iteration,
                        "offset": offset_profiles,
                 })
            except VkApiProfileIsPrivate:
                return self.result("fail", None, [{user_id: "30: This profile is private"}])
            except VkApiToManyExecute:
                return self.result("fail", None, [{user_id: "6: Too many executes"}])
            except VkApiTooManySameExecute:
                return self.result("fail", None, [{user_id: "9: Too many same actions"}])
            except VkApiDeletedUser:
                return self.result("fail", None, [{user_id: "18: Deleted user"}])
            except VkApiBannedUser:
                return self.result("fail", None, [{user_id: "37: Banned user"}])
            except VkApiLimitReached:
                return self.result("fail", None, [{user_id: "29: Limit rate"}])
            except:
                return self.result("fail", None, [{user_id: "Unknown error"}])
            if "req_err" in res_friends:
                return self.result("fail", None, [{user_id: res_friends}])
            log.debug(f'user_id: {user_id}; offset: {offset_profiles}; ppi: {profiles_per_iteration} -> OK')
            if len(res_friends["response"]['items']) == 0:
                break
            friends += res_friends["response"]["items"]
        return self.result("success", friends, None)

    def getFriendsOfFriends(self, user_id: int):
        """
        Collect friends of friends of user
        Arguments:
            user_id: int – id of user
        Return:
            result: dict – {result: {id: [friends], ...}, error: {id: text_error, ...}, status: success or fail}
        """
        fr_deep = {}
        friends = self.getFriends(user_id)
        if friends['result'] == None:
            return friends
        try:
            fr_deep["result"] = {}
            fr_deep["error"] = []
            for user in friends["result"]:
                fr_2 = self.getFriends(user)
                fr_deep["result"][user] = fr_2["result"]
                if fr_2["error"] != None:
                    fr_deep["error"].append(fr_2["error"][0])
            fr_deep["status"] = "success"
        except IndexError:
            fr_deep["status"] = "fail"
            log.exception("function: getFriends - handled unknown error")
        return fr_deep


    def getUsers(self, user_id: int, fields: list):
        """
        Collect information of user
        Arguments:
            user_id: int – id of user
            fields: list - interested fields
        Return:
            result: dict – {result: [{"field": info, ...}], error: {id: text_error, ...}, status: success or fail}
        """
        fields_ = ""
        for _ in fields:
            fields_ += (_ + ",")
        fieldsForReq = fields_[:-1]
        try:
            res_info = self._vkapi_request(
                "users.get",
                {
                    "user_id": user_id,
                    "fields": fieldsForReq,
             })
        except VkApiProfileIsPrivate:
            return self.result("fail", None, [{user_id: "30: This profile is private"}])
        except VkApiToManyExecute:
            return self.result("fail", None, [{user_id: "6: Too many executes"}])
        except VkApiTooManySameExecute:
            return self.result("fail", None, [{user_id: "9: Too many same actions"}])
        except VkApiDeletedUser:
            return self.result("fail", None, [{user_id: "18: Deleted user"}])
        except VkApiBannedUser:
            return self.result("fail", None, [{user_id: "37: Banned user"}])
        except VkApiLimitReached:
            return self.result("fail", None, [{user_id: "29: Limit rate"}])
        except:
            return self.result("fail", None, [{user_id: "Unknown error"}])
        if "req_err" in res_info:
            return self.result("fail", None, [{user_id: res_info}])
        log.debug(f'user_id: {user_id}; fields: {fields} -> OK')
        return self.result("success", res_info["response"], None)


    def getInstOfFriends(self, user_id: int):
        """
        Collect instagram logins of user
        Arguments:
            user_id: int – id of user
        Return:
            result: dict – {result: [{[user_id]: "instagram login", ...}], error: {id: text_error, ...}, status: success or fail}
        """
        users = self.getFriends(user_id)
        if users['result'] == None:
            return users
        users = users['result']
        inst_logs = {}
        for user in users:
            link = self.getUsers(user, ["connections", "status", "site"])
            if "instagram" in link['result'][0]:
                inst_logs[user] = link['result'][0]["instagram"]
                continue
            if "status" in link['result'][0]:
                pattern = re.compile('inst')
                if link['result'][0]['status'] != '':
                    if pattern.match(link['result'][0]['status']) != None:
                        buff = link['result'][0]['status'].split(" ")
                        if len(buff) >= 2:
                            if len(buff[1]) >= 3:
                                inst_logs[user] = buff[1]
                                continue
                            else:
                                inst_logs[user] = buff[2]
                                continue
            if "site" in link['result'][0]:
                pattern = re.compile('https://www.instagram.com/')
                if link['result'][0]['site'] != '':
                    if pattern.match(link['result'][0]['site']) != None:
                        inst_logs[user] = link['result'][0]['site'].split("/")[3]
        return self.result("success", [inst_logs], None)

