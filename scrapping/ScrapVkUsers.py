import datetime
import json
import logging
from math import floor
#
from scrapping.BaseScrapper import BaseScrapper
from settings import settings

log = logging.getLogger(__name__)


class ScrapVkUsers(BaseScrapper):
    """ Класс для сбора пользователей ВК """

    def __init__(self, settings):
        self.TODAY_DATE = datetime.datetime.today()
        self.AGE_GO_TO_SCHOOL = 7
        self.AGE_WENT_FROM_SCHOOL = 17
        self.MIN_NUM_OF_CLASSES = 8
        self.LEFT_SIDE_OF_AGE = 14
        self.RIGHT_SIDE_OF_AGE = 70
        super().__init__(settings)

    def _iterator(self, left_side, right_side):
        for id in range(left_side, right_side):
            ans = self.vk_module.get_users([id], ["bdate", "schools"])
            if not ans.get("error"):
                yield (id, ans["result"][0])

    def _filter(self, data):
        for id, info in data:
            if info.get("bdate") and info.get("schools"):
                yield (id, info)

    def _selector(self, data):
        for id, info in data:
            try:
                bday = tuple(map(int, info["bdate"].split('.')[::-1]))
                if len(bday) == 3:
                    bday = datetime.datetime(*bday)
                    age = floor(((self.TODAY_DATE.year - bday.year) * 12 + (self.TODAY_DATE.month - bday.month)) / 12)
                    if self.LEFT_SIDE_OF_AGE <= age and age <= self.RIGHT_SIDE_OF_AGE:
                        log.debug(f"Возраст пользователя {id} равен {age}")
                        yield (id, age)
                    else:
                        yield (id, None)
                # указан год выпуска со школы
                elif info["schools"]:
                    if info["schools"][0].get("year_from") and info["schools"][-1].get("year_to"):
                        age = self.TODAY_DATE.year - info["schools"][0]["year_from"] + self.AGE_GO_TO_SCHOOL
                        # исключаем случай, когда указана из нескольких школ только одна последняя
                        if self.LEFT_SIDE_OF_AGE <= age and age <= self.RIGHT_SIDE_OF_AGE and \
                                info["schools"][-1]["year_to"] - \
                                info["schools"][0]["year_from"] >= self.MIN_NUM_OF_CLASSES:
                            log.debug(f"Возраст пользователя {id} равен {age}")
                            yield (id, age)
                        else:
                            yield (id, None)
                    if info["schools"][-1].get("year_graduated"):
                        age = self.TODAY_DATE.year - info["schools"][-1][
                            "year_graduated"] + self.AGE_WENT_FROM_SCHOOL
                        log.debug(f"Возраст пользователя {id} равен {age}")
                        yield (id, age)
                else:
                    yield (id, None)
            except:
                yield (id, None)

    def execute(self, left_side, right_side):
        return self._selector(self._filter(self._iterator(left_side, right_side)))
