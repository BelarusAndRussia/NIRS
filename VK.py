import requests
from config import access_token as at, version


class VK():
    def __init__(self, access_token, version):
        self.access_token = access_token
        self.v = version

    def getFriends(self, user_id):
        friends = []
        flag = True
        i = 0
        while flag:
            url = 'https://api.vk.com/method/friends.get?user_id={user_id}&fields=city,country&count=100&offset={offset}&access_token={access_token}&v={api_version}'
            url_formatted = url.format(user_id=user_id, access_token=self.access_token, api_version=self.v, offset=i)
            res_friends = requests.get(url_formatted)
            keys = list(res_friends.json().keys())
            if "error" in keys:
                err = str(res_friends.json()["error"]["error_code"]) + ":" + res_friends.json()["error"]["error_msg"]
                friends.append(err)
                break
            if len(res_friends.json()["response"]['items']) == 0:
                flag = False
            for friend in res_friends.json()["response"]['items']:
                friends.append(friend["id"])
            i += 100
        return friends

    def getFriendsOfFriends(self, user_id):
        friends = self.getFriends(user_id)
        result = {}
        for user in friends:
            if type(user) == str:
                s = user.split(":")
                result[s[0]] = s[1]
                break
            fr_2 = self.getFriends(user)
            result[user] = fr_2
        return result

    def getGroups(self, user_id):
        groups = []
        flag = True
        i = 0
        while flag:
            url = 'https://api.vk.com/method/groups.get?user_id={user_id}&fields=city,country&count=100&offset={offset}&access_token={access_token}&v={api_version}'
            url_formatted = url.format(user_id=user_id, access_token=self.access_token, api_version=self.v, offset=i)
            res_groups = requests.get(url_formatted)
            if len(res_groups.json()["response"]['items']) == 0:
                flag = False
            for group in res_groups.json()["response"]['items']:
                groups.append(group)
            i += 100
        return groups

if __name__ == '__main__':
    vk = VK(at, version)
    fr = vk.getFriends(492515305)
    print(fr)



