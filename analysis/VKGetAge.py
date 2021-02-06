import json
import logging
import datetime
from math import floor
#
from .BaseAnalysisTask import BaseAnalysisTask
from.exeptions import *

log = logging.getLogger(__name__)

class VKGetAge(BaseAnalysisTask):
    """ Определение возраста пользователя ВК """

    def __init__(self, settings):
        self.TODAY_DATE = datetime.datetime.today()
        self.AGE_GO_TO_SCHOOL = 7
        self.AGE_WENT_FROM_SCHOOL = 17
        self.AGE_WENT_FROM_UNIVERSITY = 22
        self.MIN_NUM_OF_CLASSES = 8
        self.LEFT_SIDE_OF_AGE = 14
        self.RIGHT_SIDE_OF_AGE = 70
        super().__init__(settings)

    def validate(self, user_id):
        try:
            info = self.vk_module.get_users([user_id])
        except:
            raise AnalysisTaskArgumentsError(f"Профиль пользователя не действителен!")
        if type(info) is not dict or info.get("deactivated"):
            raise AnalysisTaskArgumentsError(f"Профиль пользователя заблокирован!")
        if (type(info) is not dict or
                info.get("is_closed") and not info.get("can_access_closed")):
            raise AnalysisTaskArgumentsError(f"Профиль пользователя скрыт!")

    def _create_search_params_from_userinfo(self, info, age_from=14, age_to=70):
        """ Get json with search params from user info """
        uid = info.get("id")
        domain = info.get("domain")
        if domain and uid and not domain.endswith(str(uid)):
            name = domain
        else:
            name = info.get("name")
            if not name:
                name = info.get("first_name") + " " + info.get("last_name")
        search_params = {
            "q": name,
            "has_photo": 1 if info.get("photo_id") or \
                              info.get("photo_max") and info.get(
                "photo_max") != "https://vk.com/images/camera_100.png?ava=1" else 0,
            "count": 1000,
        }
        if info.get("bdate"):
            bdate = info.get("bdate").split(".")
            if len(bdate) < 3:
                search_params.update({"birth_day": bdate[0],
                                      "birth_month": bdate[1], })
            if len(bdate) == 3:
                search_params["birth_year"] = bdate[2]
        if info.get("city"):
            search_params["city"] = info.get("city").get("id")
        if info.get("country"):
            search_params["country"] = info.get("country").get("id")
        if info.get("home_town"):
            search_params["hometown"] = info.get("home_town")
        if info.get("sex"):
            search_params["sex"] = info.get("sex")
        search_params["age_from"] = age_from
        search_params["age_to"] = age_to
        return search_params

    def _get_age_by_info(self, info):
        """ Get age by info of user """
        uid = info.get("id")
        if not uid:
            return None
        if info.get("bdate") and len(info.get("bdate").split(".")) == 3:
            today = self.TODAY_DATE.today()
            bdate = datetime.strptime(info.get("bdate"), '%d.%m.%Y')
            age = today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))
            log.debug(f"Определен возраст пользователя ВК (uid={uid}). Приблизительный возраст={age}")
            return age
        search_json = self._create_search_params_from_userinfo(info, "$age_from", "$age_to")
        search_json = json.dumps(search_json, ensure_ascii=False) \
            .replace('"$age_from"', "age_from") \
            .replace('"$age_to"', "age_to")
        code = """
        var uid = """ + str(uid) + """;""" + """
        int age_from = 14;
        int age_to = 80;
        var search_json = """ + search_json + """;
        var tmp_search_json = search_json;
        if( API.users.search(tmp_search_json).items@.id.indexOf(uid) == -1 )
        {
            return 0;
        }
        while( age_from != age_to )
        {
            tmp_search_json = search_json;
            int pivot = age_from + age_to;
            if( pivot % 2 == 0 )
            {
                pivot = pivot / 2;
            }
            else
            {
                pivot = (pivot - 1) / 2;
            }
            tmp_search_json.age_from = age_from;
            tmp_search_json.age_to = pivot;
            if( API.users.search(tmp_search_json).items@.id.indexOf(uid) != -1 )
            {
                if( age_to - age_from == 1 )
                {
                    age_to = age_from;
                }
                else
                {
                    age_to = pivot;
                }
            }
            else
            {
                if( age_to - age_from == 1 )
                {
                    age_from = age_to;
                }
                else
                {
                    age_from = pivot;
                }
            }
        }
        return age_from;
        """
        age = self.vk_module._vkapi_request("execute", {"code": code})
        log.debug(f"Определен возраст пользователя ВК (uid={uid}). Приблизительный возраст={age}")
        if age is None:
            return None
        elif age == 0:
            return None
        return int(age)

    def _simple_det_age_of_vk_user(self, user_id: int):
        """"
            Simple method to determine age of user
            return: age or error or None
        """
        info = self.vk_module.get_users([user_id], ["bdate", "education", "schools", "home_town"])
        #указана дата в профиле
        if "bdate" in info["result"][0]:
            bday = tuple(map(int, info["result"][0]["bdate"].split('.')[::-1]))
            if len(bday) == 3:
                bday = datetime.datetime(*bday)
                age = floor(((self.TODAY_DATE.year - bday.year) * 12 + (self.TODAY_DATE.month - bday.month)) / 12)
                if self.LEFT_SIDE_OF_AGE <= age and age <= self.RIGHT_SIDE_OF_AGE:
                    log.debug(f"Определен возраст пользователя ВК (uid={user_id}). Приблизительный возраст={age}")
                    return age
        #указан год выпуска со школы
        if info["result"][0].get("schools"):
            num_of_schools = len(info["result"][0]["schools"])
            if num_of_schools:
                if info["result"][0]["schools"][0].get("year_from") and info["result"][0]["schools"][-1].get("year_to"):
                    age = self.TODAY_DATE.year - info["result"][0]["schools"][0]["year_from"] + self.AGE_GO_TO_SCHOOL
                    #исключаем случай, когда указана из нескольких школ только одна последняя
                    if self.LEFT_SIDE_OF_AGE <= age and age <= self.RIGHT_SIDE_OF_AGE and\
                       info["result"][0]["schools"][-1]["year_to"] -\
                       info["result"][0]["schools"][0]["year_from"] >= self.MIN_NUM_OF_CLASSES:
                        log.debug(f"Определен возраст пользователя ВК (uid={user_id}). Приблизительный возраст={age}")
                        return age
                if info["result"][0]["schools"][-1].get("year_graduated"):
                    age = self.TODAY_DATE.year - info["result"][0]["schools"][-1]["year_graduated"] + self.AGE_WENT_FROM_SCHOOL
                    log.debug(f"Определен возраст пользователя ВК (uid={user_id}). Приблизительный возраст={age}")
                    return age
        #указан год выпуска из универа (не очень адекватная оценка)
        if info["result"][0].get("graduation"):
            age = self.TODAY_DATE.year - info["result"][0]["graduation"] + self.AGE_WENT_FROM_UNIVERSITY
            log.debug(f"Определен возраст пользователя ВК (uid={user_id}). Приблизительный возраст={age}")
            return age
        return self._get_age_by_info(info)

    def _process_info(self, info):
        if info is None:
            return None
        return {
            "id": info.get("id"),
            "bdate": info.get("bdate"),
            "university_name": info.get("university_name"),
            "school_name": info.get("schools", [{"name": None}])[-1]["name"] if len(info.get("schools", [{"name": None}]))
                           else None,
            "home_town": info.get("home_town")
        }

    def det_age_of_vk_user(self, user_id: int):
        """"
            Determine age of user
            return: age
        """
        age_simple = self._simple_det_age_of_vk_user(user_id)
        if age_simple is not None:
            return age_simple
        user_info = self.vk_module.get_users([user_id], ["education", "schools", "home_town"])["result"][0]
        user_general_info = self._process_info(user_info)
        friends = self.vk_module.get_friends(user_id)["result"]
        log.debug(f"Функция get_friends вернула: {friends}")
        friends_info = []
        frs_info = self.vk_module.get_users(friends, ["bdate", "education", "schools", "home_town"])["result"]
        for friend in frs_info:
            friend_general_info = self._process_info(friend)
            friends_info.append(friend_general_info)
        log.debug(f"friends_info: {friends_info}")
        log.debug(f"user_general_info: {user_general_info}")
        #указана школа
        if user_general_info["school_name"]:
            classmates = list(map(self._simple_det_age_of_vk_user, [i["id"] for i in filter(
                lambda info: info["school_name"] is not None and
                             info["school_name"] == user_general_info["school_name"], friends_info)]))
            if classmates:
                user_age = max(set(classmates) - {None}, key=classmates.count)
                log.debug(f"Определен возраст пользователя ВК (uid={user_id}). Приблизительный возраст={user_age}")
                return user_age
        #указан универ
        if user_general_info["university_name"]:
            classmates = list(map(self._simple_det_age_of_vk_user, [i["id"] for i in filter(
                         lambda info: info["university_name"] is not None and
                                      info["university_name"] == user_general_info["university_name"], friends_info)]))
            if classmates:
                user_age = max(set(classmates) - {None}, key=classmates.count)
                log.debug(f"Определен возраст пользователя ВК (uid={user_id}). Приблизительный возраст={user_age}")
                return user_age
        # указан родной город и нет школы и универа
        if user_general_info["home_town"]:
            classmates = []
            for friend in friends_info:
                if friend["home_town"] == user_general_info["home_town"] and user_general_info["school_name"]:
                    classmates.append(friend["school_name"])
            if classmates:
                user_school = max(set(classmates), key=classmates.count)
                friend_ages = list(map(self._simple_det_age_of_vk_user, [i["id"] for i in filter(
                    lambda info: info["school_name"] == user_school, classmates)]))
                if friend_ages:
                    user_age = max(set(classmates) - {None}, key=classmates.count)
                    log.debug(f"Определен возраст пользователя ВК  (uid={user_id}). Приблизительный возраст={user_age}")
                    return user_age
        #в крайнем случаем считаем вораст всех друзей
        friend_ages = []
        for friend in friends:
            fr_age = self._simple_det_age_of_vk_user(friend)
            if fr_age is not None:
                friend_ages.append(fr_age)
        user_age = max(set(friend_ages), key=friend_ages.count)
        if user_age:
            log.debug(f"Определен возраст пользователя ВК (uid={user_id}). Приблизительный возраст={user_age}")
            return user_age

    def execute(self, user_id):
        self.validate(user_id)
        return self.det_age_of_vk_user(user_id)
