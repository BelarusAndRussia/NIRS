import pytest
#
from settings import settings
from vk import VK

MY_ID = 186101748
DUROV_ID = 1

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

def test_getUsers():
    f_name = vk_module.getUsers(DUROV_ID)['result'][0]['first_name']
    l_name = vk_module.getUsers(DUROV_ID)['result'][0]['last_name']
    assert f_name == 'Павел'
    assert l_name == 'Дуров'

def test_getFriends():
    my_friend = vk_module.getFriends(MY_ID)['result']
    durov_friend = vk_module.getFriends(DUROV_ID)['result']
    assert len(my_friend) != 0
    assert len(durov_friend) == 0

def test_getFollowers():
    followers = vk_module.getFollowers(1, max_followers=100)['result']
    assert len(followers) == 100

def test_getGroups():
    groups = vk_module.getGroups(MY_ID, max_groups=10)['result']
    assert len(groups) == 10

def test_getPhotos():
    photos = vk_module.getPhotos(DUROV_ID, max_photos=10)['result']
    assert len(photos) == 10

def test_getWall():
    notes_durov = vk_module.getWall(DUROV_ID, max_notes=10)['result']
    assert len(notes_durov) == 10

def test_getVideos():
    videos = vk_module.getVideos(DUROV_ID)['result']
    assert len(videos) == 4

def test_getWhoLikes():
    item_id = 456264771
    whoLikes = vk_module.getWhoLikes('photo', DUROV_ID, item_id, max_likes=1000)['result']
    assert len(whoLikes) == 1000

def test_getComments():
    item_id = 456264771
    comments_durov = vk_module.getComments(DUROV_ID, item_id)['result']
    barca_id = -22746750
    item_id = 11427508
    comments_barca = vk_module.getComments(barca_id, item_id, max_comments=100)['result']
    assert comments_durov == None
    assert len(comments_barca) == 100






