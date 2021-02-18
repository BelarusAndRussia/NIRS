import pandas as pd
import logging
import datetime
from math import floor
import matplotlib.pyplot as plt
#
from .BaseAnalysisTask import BaseAnalysisTask

log = logging.getLogger(__name__)

class LearningRegression(BaseAnalysisTask):
    """ Обучение регрессии """

    def __init__(self, settings):
        self.TODAY_DATE = datetime.datetime.today()
        super().__init__(settings)

    def init_data_frame(self, filename):
        table = pd.read_json(filename)
        table = table[table['date_from_school'].notna()]
        determinated_age = []
        for date in table["bday"]:
            bday = tuple(map(int, date.split('.')[::-1]))
            bday = datetime.datetime(*bday)
            age = floor(((self.TODAY_DATE.year - bday.year) * 12 + (self.TODAY_DATE.month - bday.month)) / 12)
            determinated_age.append(age)
        table["det_age"] = determinated_age
        log.debug(f"Таблица успешно создана")
        return table

    def show_graphic(self, table):
        table.plot(x="det_age", y="date_from_school")
        plt.show()

    def execute(self, filename):
        table = self.init_data_frame(filename)
        self.show_graphic(table)
