import inspect
import re
import sys
#
from .BaseAnalysisTask import BaseAnalysisTask
from .VKGetAge import VKGetAge


class Analysis:
    """ Класс для проведения аналитики """

    def __init__(self, settings):
        for name, obj in inspect.getmembers(
                sys.modules[__name__], lambda obj: inspect.isclass(obj) and issubclass(obj, BaseAnalysisTask)
        ):
            if name != BaseAnalysisTask.__name__:
                task = obj(settings)
                setattr(self, self._translate_method(name), task.execute)

    def _translate_method(self, class_method_name):
        replacer = lambda m: f"{('_' if m.start(0) > 0 else '')}{m.group()}"
        return re.sub("[A-Z]{2,}", replacer,
                      re.sub("[A-Z][^A-Z_]+", replacer, class_method_name)).lower()
