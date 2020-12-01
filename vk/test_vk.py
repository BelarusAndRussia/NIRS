from settings import settings
from vk import VK
from main import init_app

init_app()
vk_module = VK(settings)

# def test_getFriends():
#     assert vk_module.getFriends(186101748)['result'] != None
#     assert vk_module.getFriends(245046095)['result'] == None