import logging
import datetime
from math import floor
#
from vk import VK

log = logging.getLogger(__name__)

TODAY_DATE = datetime.datetime.today()
AGE_GO_TO_SCHOOL = 7
AGE_WENT_FROM_SCHOOL = 17
AGE_WENT_FROM_UNIVERSITY = 22
MIN_NUM_OF_CLASSES = 8

class ANALYSIS:
    """
        ******************************
        Class for analysis
        ******************************
    """
    def __init__(self, settings):
        self.vk_module = VK(settings)

    def _SimpleDetAgeOfVkUser(self, user_id: int):
        """"
            Simple method to determine age of user
            return: age or error or None
        """
        log.info("Starter function for detecting age of vk user")
        info = self.vk_module.getUsers(user_id, ["bdate", "education", "schools", "home_town"])
        #указана дата в профиле
        if "bdate" in info["result"][0]:
            bday = list(reversed(info["result"][0]["bdate"].split('.')))
            bday = [int(i) for i in bday]
            if len(bday) == 3:
                bday = datetime.datetime(*bday)
                age = floor(((TODAY_DATE.year - bday.year) * 12 + (TODAY_DATE.month - bday.month)) / 12)
                if age >= 14 and age <= 70:
                    log.debug(f'user_id: {user_id}-> OK')
                    return age
        if "is_closed" in info["result"][0]:
            if info["result"][0]["is_closed"] == True:
                log.debug(f'user_id: {user_id}-> Profile is private')
                return "Profile is private"
        #указан год выпуска со школы
        if "schools" in info["result"][0]:
            num_of_schools = len(info["result"][0]["schools"])
            if num_of_schools:
                if "year_from" in info["result"][0]["schools"][0] and "year_to" in info["result"][0]["schools"][num_of_schools-1]:
                    age = TODAY_DATE.year - info["result"][0]["schools"][0]["year_from"] + AGE_GO_TO_SCHOOL
                    #исключаем случай, когда указана из нескольких школ только одна последняя
                    if age >= 14 and age <= 70 and\
                       info["result"][0]["schools"][num_of_schools-1]["year_to"] -\
                       info["result"][0]["schools"][0]["year_from"] >= MIN_NUM_OF_CLASSES:
                        log.debug(f'user_id: {user_id}-> OK')
                        return age
                if "year_graduated" in info["result"][0]["schools"][-1]:
                    age = TODAY_DATE.year - info["result"][0]["schools"][-1]["year_graduated"] + AGE_WENT_FROM_SCHOOL
                    log.debug(f'user_id: {user_id}-> OK')
                    return age
        #указан год выпуска из универа (не очень адекватная оценка)
        if "graduation" in info["result"][0]:
            if info["result"][0]["graduation"]:
                age = TODAY_DATE.year - info["result"][0]["graduation"] + 22
                log.debug(f'user_id: {user_id}-> OK')
                return age

    def DetAgeOfVkUser(self, user_id: int):
        """"
            Determine age of user
            return: age
        """
        age_simple = self._SimpleDetAgeOfVkUser(user_id)
        if age_simple is not None and age_simple != "Profile is private":
            return age_simple
        user_info = self.vk_module.getUsers(user_id, ["education", "schools", "home_town"])["result"][0]
        user_general_info = {}
        user_univ = None
        user_schools = None
        user_ht = None
        if "education" in user_info:
            user_univ = user_info["university_name"]
        if "schools" in user_info:
            if len(user_info["schools"]):
                user_schools = user_info["schools"][-1]["name"]
        if "home_town" in user_info:
            user_ht = user_info["home_town"]
        user_general_info["university_name"] = user_univ
        user_general_info["school_name"] = user_schools
        user_general_info["home_town"] = user_ht
        friends = self.vk_module.getFriends(user_id)["result"]
        log.debug(f"Functon getFriends return: {friends}")
        friends_info = []
        for friend in friends:
            friend_info = self.vk_module.getUsers(friend,["bdate", "education", "schools", "home_town"])["result"]
            friend_general_info = {}
            friend_bd = None
            friend_univ = None
            friend_schools = None
            friend_ht = None
            friend_general_info["id"] = friend
            if "bdate" in friend_info:
                friend_bd = friend_info["bdate"]
            if "education" in friend_info:
                friend_univ = friend_info["university_name"]
            if "schools" in friend_info:
                friend_schools = friend_info["schools"][-1]["name"]
            if "home_town" in friend_info:
                friend_ht = friend_info["home_town"]
            friend_general_info["bdate"] = friend_bd
            friend_general_info["university_name"] = friend_univ
            friend_general_info["school_name"] = friend_schools
            friend_general_info["home_town"] = friend_ht
            friends_info.append(friend_general_info)
        log.debug(f"friends_info: {friends_info}")
        log.debug(f"user_general_info: {user_general_info}")
        #указана школа
        if user_general_info["school_name"]:
            classmates = []
            for friend in friends_info:
                if friend["school_name"] == user_general_info["school_name"]:
                    classmates.append(friend["id"])
            if len(classmates):
                friend_ages = []
                for friend in classmates:
                    friend_age = self._SimpleDetAgeOfVkUser(friend)
                    if friend_age is not None and friend_age != "Profile is private":
                        friend_ages.append(friend_age)
                user_age = max(set(friend_ages), key=friend_ages.count)
                if user_age:
                    log.debug(f"Functon DetAgeOfVkUser return: {user_age}")
                    return user_age
        #указан универ
        if user_general_info["university_name"]:
            classmates = []
            for friend in friends_info:
                if friend["university_name"] == user_general_info["university_name"]:
                    classmates.append(friend["id"])
            if len(classmates):
                friend_ages = []
                for friend in classmates:
                    friend_age = self._SimpleDetAgeOfVkUser(friend)
                    if friend_age is not None and friend_age != "Profile is private":
                        friend_ages.append(friend_age)
                user_age = max(set(friend_ages), key=friend_ages.count)
                if user_age:
                    log.debug(f"Functon DetAgeOfVkUser return: {user_age}")
                    return user_age
        # указан родной город и нет школы и универа
        if user_general_info["home_town"]:
            classmates = []
            for friend in friends_info:
                if friend["home_town"] == user_general_info["home_town"] and user_general_info["school_name"]:
                    classmates.append(friend["school_name"])
            if len(classmates):
                user_school = max(set(classmates), key=classmates.count)
                friend_ages = []
                for friend in classmates:
                    if friend["school_name"] == user_school:
                        friend_age = self._SimpleDetAgeOfVkUser(friend["id"])
                        if friend_age is not None and friend_age != "Profile is private":
                            friend_ages.append(friend_age)
                user_age = max(set(friend_ages), key=friend_ages.count)
                if user_age:
                    log.debug(f"Functon DetAgeOfVkUser return: {user_age}")
                    return user_age
        #в крайнем случаем считаем вораст всех друзей
        friend_ages = []
        for friend in friends:
            fr_age = self._SimpleDetAgeOfVkUser(friend)
            if fr_age is not None and fr_age != "Profile is private":
                friend_ages.append(fr_age)
        user_age = max(set(friend_ages), key=friend_ages.count)
        if user_age:
            log.debug(f"Functon DetAgeOfVkUser return: {user_age}")
            return user_age
