import requests
from config import access_token as at, version
import logging
import random
import hashlib
import time

logging.basicConfig(level=logging.DEBUG,
                    filename='app.log',
                    filemode='w',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

TIMEOUT = 1000

def _get_user_agent():
    """Generate new UA for header"""
    platform = random.choice(['Macintosh', 'Windows', 'X11'])
    if platform == 'Macintosh':
        os = random.choice(['68K', 'PPC'])
    elif platform == 'Windows':
        os = random.choice(['Win3.11',
                            'WinNT3.51',
                            'WinNT4.0',
                            'Windows NT 5.0',
                            'Windows NT 5.1',
                            'Windows NT 5.2',
                            'Windows NT 6.0',
                            'Windows NT 6.1',
                            'Windows NT 6.2',
                            'Win95',
                            'Win98',
                            'Win 9x 4.90',
                            'WindowsCE'])
    elif platform == 'X11':
        os = random.choice(['Linux i686', 'Linux x86_64'])
    browser = random.choice(['chrome', 'firefox', 'ie'])
    if browser == 'chrome':
        webkit = str(random.randint(500, 599))
        version = str(random.randint(0, 24)) + '.0' + \
            str(random.randint(0, 1500)) + '.' + str(random.randint(0, 999))
        return 'Mozilla/5.0 (' + os + ') AppleWebKit/' + webkit + \
            '.0 (KHTML, live Gecko) Chrome/' + version + ' Safari/' + webkit
    elif browser == 'firefox':
        year = str(random.randint(2000, 2012))
        month = random.randint(1, 12)
        if month < 10:
            month = '0' + str(month)
        else:
            month = str(month)
        day = random.randint(1, 30)
        if day < 10:
            day = '0' + str(day)
        else:
            day = str(day)
        gecko = year + month + day
        version = random.choice(['1.0',
                                 '2.0',
                                 '3.0',
                                 '4.0',
                                 '5.0',
                                 '6.0',
                                 '7.0',
                                 '8.0',
                                 '9.0',
                                 '10.0',
                                 '11.0',
                                 '12.0',
                                 '13.0',
                                 '14.0',
                                 '15.0'])
        return 'Mozilla/5.0 (' + os + '; rv:' + version + \
            ') Gecko/' + gecko + ' Firefox/' + version
    elif browser == 'ie':
        version = str(random.randint(1, 10)) + '.0'
        engine = str(random.randint(1, 5)) + '.0'
        option = random.choice([True, False])
        if option == True:
            token = random.choice(
                ['.NET CLR', 'SV1', 'Tablet PC', 'Win64; IA64', 'Win64; x64', 'WOW64']) + '; '
        elif option == False:
            token = ''
        return 'Mozilla/5.0 (compatible; MSIE ' + version + \
            '; ' + os + '; ' + token + 'Trident/' + engine + ')'

def create_new_session():
    session = requests.session()
    session.headers = {
        'User-Agent': _get_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml,application/pdf;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate'
    }
    google_id = hashlib.md5(
        str(random.randint(0, 16**16)).encode()).hexdigest()[: 16]
    cookie = {
        "domain": ".scholar.google.com",
        "expires": time.time() + 60 * 60,
        "name": "GSP",
        "value": 'ID={}:CF=3'.format(google_id),
        "httpOnly": False}
    session.cookies.set(cookie['name'], cookie['value'])
    session.HTTP_requests = 0
    return session


class VK():
    def __init__(self, access_token, version):
        self.access_token = access_token
        self.v = version

    def getFriends(self, user_id):
        friends = {}
        flag = True
        i = 0
        try:
            friends["result"] = []
            friends["error"] = {}
            while flag:
                url = 'https://api.vk.com/method/friends.get?user_id={user_id}&fields=city,country&count=100&offset={offset}&access_token={access_token}&v={api_version}'
                url_formatted = url.format(user_id=user_id, access_token=self.access_token, api_version=self.v, offset=i)
                res_friends = create_new_session().get(url_formatted)
                keys = list(res_friends.json().keys())
                if "error" in keys:
                    err = str(res_friends.json()["error"]["error_code"]) + ":" + res_friends.json()["error"]["error_msg"]
                    friends["error"][user_id] = err
                    logging.info(f"function: getFriends - handled error: {err}")
                    break
                if len(res_friends.json()["response"]['items']) == 0:
                    flag = False
                for friend in res_friends.json()["response"]['items']:
                    friends["result"].append(friend["id"])
                i += 100
            friends["status"] = "success"
        except:
            friends["status"] = "fail"
            logging.exception("Exception occurred")
        return friends

    def getFriendsOfFriends(self, user_id):
        friends = self.getFriends(user_id)
        fr_deep = {}
        try:
            fr_deep["result"] = {}
            fr_deep["error"] = []
            for user in friends["result"]:
                fr_2 = self.getFriends(user)
                fr_deep["result"][user] = fr_2["result"]
                if fr_2["error"]:
                    fr_deep["error"].append(fr_2["error"])
            fr_deep["status"] = "success"
        except:
            fr_deep["status"] = "fail"
            logging.exception("Exception occurred")
        return fr_deep

    def getGroups(self, user_id):
        groups = {}
        flag = True
        i = 0
        try:
            groups["result"] = []
            groups["error"] = {}
            while flag:
                url = 'https://api.vk.com/method/groups.get?user_id={user_id}&fields=city,country&count=100&offset={offset}&access_token={access_token}&v={api_version}'
                url_formatted = url.format(user_id=user_id, access_token=self.access_token, api_version=self.v, offset=i)
                res_groups = create_new_session().get(url_formatted)
                keys = list(res_groups.json().keys())
                if "error" in keys:
                    err = str(res_groups.json()["error"]["error_code"]) + ":" + res_groups.json()["error"]["error_msg"]
                    groups["error"][user_id] = err
                    logging.info(f"function: getGroups - handled error: {err}")
                    break
                if len(res_groups.json()["response"]['items']) == 0:
                    flag = False
                for group in res_groups.json()["response"]['items']:
                    groups["result"].append(group)
                i += 100
            groups["status"] = "success"
        except:
            groups["status"] = "fail"
        return groups

if __name__ == '__main__':
    vk = VK(at, version)
    users = [244864074, 89767667, 153988262, 135707636, 257875098, 124315477, 210121381, 136389672, 135707636]
    print(vk.getFriends(89767667))