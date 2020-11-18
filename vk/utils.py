
#
from vk.create_session import create_new_session
from main import root_logger


def get_request(URL: str, data: dict):
    """
    Make request
    Arguments:
        URL:str - URL request
        data:dict - parameters for executed request
    Return:
        result: json
    """
    root_logger.debug(f"Execute request '{URL}' with params {data}")
    full_url = f"{URL}?"
    for arg in data.keys():
        full_url += f"{arg}={data[arg]}&"
    full_url = full_url[:-1]
    result = create_new_session().get(full_url)
    return result
