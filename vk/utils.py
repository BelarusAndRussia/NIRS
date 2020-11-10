import logging.handlers

from vk.create_session import create_new_session


root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler("app.log", mode='w', maxBytes=5*1024*1024, encoding="utf-8")
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
root_logger.addHandler(handler)


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