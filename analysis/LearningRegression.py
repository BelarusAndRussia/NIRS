import pandas as pd
import numpy as np
import logging
import datetime
from math import floor
import matplotlib.pyplot as plt
from scipy.stats.stats import pearsonr
from sklearn.linear_model import LinearRegression
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
        plt.scatter(table["det_age"], table["date_from_school"], s=2)
        plt.show()
        return pearsonr(table["det_age"], table["date_from_school"])

    def redression(self, x, y):
        reg = LinearRegression().fit(x, y)
        return reg.predict(np.array([2015]).reshape (-1, 1))

    def prob_values(self, table):
        diff = []
        y_school = table["date_from_school"]
        y_bd = table["bday"]
        res = zip(y_school, y_bd)
        for a in res:
            diff.append(a[0] - int(a[1].split(".")[-1]))
        res = sorted(diff)
        return res

    def execute(self, filename):
        table = self.init_data_frame(filename)
        #self.show_graphic(table)
        #x = np.array(table["date_from_school"]).reshape(-1, 1)
        #y = np.array(table["det_age"]).reshape(-1, 1)
        #predict_age = self.redression(x, y)
        return(self.prob_values(table))
