import random
import time
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
        self._USED_TOKENS = []
        if settings.tokens_file_vk:
            self.load_tokens(settings.tokens_file_vk)
        self.check_tokens()

    def load_tokens(self, fname):
        self._TOKENS = list(map(str.strip, open(
            fname, "r", encoding=self.settings.encoding).readlines()))

    def check_tokens(self):
        for token in self._TOKENS:
            req_data = {
                "access_token": token,
                "v": self.API_VERSION,
                "user_id": 186101748 #open account
            }
            data = request(f"https://api.vk.com/method/users.get", req_data, format_JSON=True)
            if "req_err" in data:
                self._TOKENS.remove(token)

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
        if len(self._TOKENS):
            token = random.choice(self._TOKENS)
            self._TOKENS.remove(token)
            self._USED_TOKENS.append(token)
        else:
            time.sleep(0.4)
            self._TOKENS = self._USED_TOKENS
            self._USED_TOKENS = []
            token = random.choice(self._TOKENS)
        req_data = {
            "access_token": token,
            "v": self.API_VERSION
        }
        if args:
            req_data.update(args)
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
            max_friends: int - num of returned friends
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

    def getInstOfUser(self, user_id: int):
        """
        Collect instagram login of user
        Arguments:
            user_id: int – id of user
        Return:
            result: dict – {result: [{[user_id]: "instagram login"}], error: {id: text_error}, status: success or fail}
        """
        inst_log = {}
        link = self.getUsers(user_id, ["connections", "status", "site"])
        if "instagram" in link['result'][0]:
            inst_log[user_id] = link['result'][0]["instagram"]
        if "status" in link['result'][0]:
            s = link['result'][0]['status'].lower()
            pattern = re.compile('inst')
            if s != '':
                if pattern.match(s) != None:
                    buff = link['result'][0]['status'].split(":")[1]
                    buff = buff.strip()
                    inst_log[user_id] = buff
        if "site" in link['result'][0]:
            pattern = re.compile('https://www.instagram.com/')
            if link['result'][0]['site'] != '':
                if pattern.match(link['result'][0]['site']) != None:
                    inst_log[user_id] = link['result'][0]['site'].split("/")[3]
        return self.result("success", [inst_log], None)

    def getInstOfUserFriends(self, user_id: int):
        """
        Collect instagram logins of user friends
        Arguments:
            user_id: int – id of user
        Return:
            result: dict – {result: [{[user_id]: "instagram login", ...}], error: {id: text_error, ...},
            status: success or fail}
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
                s = link['result'][0]['status'].lower()
                pattern = re.compile('inst')
                if s != '':
                    if pattern.match(s) != None:
                        buff = link['result'][0]['status'].split(":")[1]
                        buff = buff.strip()
                        inst_logs[user] = buff
                        continue
            if "site" in link['result'][0]:
                pattern = re.compile('https://www.instagram.com/')
                if link['result'][0]['site'] != '':
                    if pattern.match(link['result'][0]['site']) != None:
                        inst_logs[user] = link['result'][0]['site'].split("/")[3]
        return self.result("success", [inst_logs], None)

    def getGroups(self, user_id: int, max_groups: int=5000):
        """
        Collect groups of user
        Arguments:
            user_id: int – id of user
            max_groups: int - num of returned groups
        Return:
            result: dict – {result: [groups_id], error: {id: text_error, ...}, status: success or fail}
        """
        groups = []
        groups_per_iteration = 1000
        for offset_groups in range(0, max_groups, groups_per_iteration):
            try:
                res_groups = self._vkapi_request(
                    "groups.get",
                    {
                        "user_id": user_id,
                        "count": groups_per_iteration,
                        "offset": offset_groups,
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
            except VkApiLimitedListOfGroups:
                return self.result("fail", None, [{user_id: "260: Limited list of groups"}])
            except:
                return self.result("fail", None, [{user_id: "Unknown error"}])
            if "req_err" in res_groups:
                return self.result("fail", None, [{user_id: res_groups}])
            log.debug(f'user_id: {user_id}; offset: {offset_groups}; ppi: {groups_per_iteration} -> OK')
            if len(res_groups["response"]['items']) == 0:
                break
            groups += res_groups["response"]["items"]
        return self.result("success", groups, None)

    def getUserPhotos(self, user_id: int, extended: int=0, max_photos: int=200):
        """
        Collect photos of user
        Arguments:
            user_id: int – id of user
            extended: bool - extended information
            max_photos: int - num of returned photos
        Return:
            result: dict – {result: [{user id, photos info, ...}], error: {id: text_error, ...}, status: success or fail}
        """
        photos = []
        photos_per_iteration = 1
        for offset_photos in range(0, max_photos, photos_per_iteration):
            try:
                res_photos = self._vkapi_request(
                    "photos.getAll",
                    {
                        "owner_id": user_id,
                        "count": photos_per_iteration,
                        "offset": offset_photos,
                        "extended": extended,
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
            except VkApiInaccessibleContent:
                return self.result("fail", None, [{user_id: "19: Inaccessible content"}])
            except:
                return self.result("fail", None, [{user_id: "Unknown error"}])
            if "req_err" in res_photos:
                return self.result("fail", None, [{user_id: res_photos}])
            log.debug(f'user_id: {user_id}; offset: {offset_photos}; ppi: {photos_per_iteration} -> OK')
            if len(res_photos["response"]['items']) == 0:
                break
            photos += res_photos["response"]["items"]
        return self.result("success", photos, None)

    def getGroupPhotos(self, group_id: int, extended: int=0, max_photos: int=200):
        """
        Collect photos of group
        Arguments:
            user_id: int – id of group
            extended: bool - extended information
            max_photos: int - num of returned photos
        Return:
            result: dict – {result: [{group id, photos info, ...}], error: {id: text_error, ...}, status: success or fail}
        """
        photos = []
        photos_per_iteration = 1
        for offset_photos in range(0, max_photos, photos_per_iteration):
            try:
                res_photos = self._vkapi_request(
                    "photos.getAll",
                    {
                        "owner_id": -group_id,
                        "count": photos_per_iteration,
                        "offset": offset_photos,
                        "extended": extended,
                    })
            except VkApiProfileIsPrivate:
                return self.result("fail", None, [{group_id: "30: This profile is private"}])
            except VkApiToManyExecute:
                return self.result("fail", None, [{group_id: "6: Too many executes"}])
            except VkApiTooManySameExecute:
                return self.result("fail", None, [{group_id: "9: Too many same actions"}])
            except VkApiDeletedUser:
                return self.result("fail", None, [{group_id: "18: Deleted user"}])
            except VkApiBannedUser:
                return self.result("fail", None, [{group_id: "37: Banned user"}])
            except VkApiLimitReached:
                return self.result("fail", None, [{group_id: "29: Limit rate"}])
            except VkApiInaccessibleContent:
                return self.result("fail", None, [{group_id: "19: Inaccessible content"}])
            except:
                return self.result("fail", None, [{group_id: "Unknown error"}])
            if "req_err" in res_photos:
                return self.result("fail", None, [{group_id: res_photos}])
            log.debug(f'group_id: {group_id}; offset: {offset_photos}; ppi: {photos_per_iteration} -> OK')
            if len(res_photos["response"]['items']) == 0:
                break
            photos += res_photos["response"]["items"]
        return self.result("success", photos, None)

    def getUserWall(self, user_id: int, extended: int=0, max_notes: int=100):
        """
        Collect wall notes of user
        Arguments:
            user_id: int – id of user
            extended: bool - extended information
            max_photos: int - num of returned wall notes
        Return:
            result: dict – {result: [{user id, wall notes info, ...}], error: {id: text_error, ...}, status: success or fail}
        """
        notes = []
        notes_per_iteration = 1
        for offset_notes in range(0, max_notes, notes_per_iteration):
            try:
                res_notes = self._vkapi_request(
                    "wall.get",
                    {
                        "owner_id": user_id,
                        "count": notes_per_iteration,
                        "offset": offset_notes,
                        "extended": extended,
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
            except VkApiInaccessibleContent:
                return self.result("fail", None, [{user_id: "19: Inaccessible content"}])
            except:
                return self.result("fail", None, [{user_id: "Unknown error"}])
            if "req_err" in res_notes:
                return self.result("fail", None, [{user_id: res_notes}])
            log.debug(f'user_id: {user_id}; offset: {offset_notes}; ppi: {notes_per_iteration} -> OK')
            if len(res_notes["response"]['items']) == 0:
                break
            notes += res_notes["response"]["items"]
        return self.result("success", notes, None)

    def getGroupWall(self, group_id: int, extended: int=0, max_notes: int = 100):
        """
        Collect wall notes of group
        Arguments:
            user_id: int – id of user
            extended: bool - extended information
            max_photos: int - num of returned wall notes
        Return:
            result: dict – {result: [{group id, wall notes info, ...}], error: {id: text_error, ...}, status: success or fail}
        """
        notes = []
        notes_per_iteration = 1
        for offset_notes in range(0, max_notes, notes_per_iteration):
            try:
                res_notes = self._vkapi_request(
                    "wall.get",
                    {
                        "owner_id": -group_id,
                        "count": notes_per_iteration,
                        "offset": offset_notes,
                        "extended": extended,
                    })
            except VkApiProfileIsPrivate:
                return self.result("fail", None, [{group_id: "30: This profile is private"}])
            except VkApiToManyExecute:
                return self.result("fail", None, [{group_id: "6: Too many executes"}])
            except VkApiTooManySameExecute:
                return self.result("fail", None, [{group_id: "9: Too many same actions"}])
            except VkApiDeletedUser:
                return self.result("fail", None, [{group_id: "18: Deleted user"}])
            except VkApiBannedUser:
                return self.result("fail", None, [{group_id: "37: Banned user"}])
            except VkApiLimitReached:
                return self.result("fail", None, [{group_id: "29: Limit rate"}])
            except VkApiInaccessibleContent:
                return self.result("fail", None, [{group_id: "19: Inaccessible content"}])
            except:
                return self.result("fail", None, [{group_id: "Unknown error"}])
            if "req_err" in res_notes:
                return self.result("fail", None, [{group_id: res_notes}])
            log.debug(f'group_id: {group_id}; offset: {offset_notes}; ppi: {notes_per_iteration} -> OK')
            if len(res_notes["response"]['items']) == 0:
                break
            notes += res_notes["response"]["items"]
        return self.result("success", notes, None)
