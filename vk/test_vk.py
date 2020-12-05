import pytest
#
from settings import settings
from vk import VK

"""
Модуль тестирования API
USAGE: pytest --settings <setting filename> vk
"""

@pytest.fixture()
def setting(pytestconfig):
    return pytestconfig.getoption("settings")

def test_initmodule(setting):
    settings.load_JSON(setting)
    global vk_module
    vk_module = VK(settings)

def test_getFriends():
    print(vk_module.getFriends(186101748))



