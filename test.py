import requests

def get_request(URL: str, data: dict):
    """
    Make request
    Arguments:
        URL:str - URL request
        data:dict - parameters for executed request
    """
    #root_logger.debug(f"Execute request '{URL}' with params {data}")
    full_url = f"{URL}?"
    for arg in data.keys():
        full_url += f"{arg}={data[arg]}&"
    full_url = full_url[:-1]
    result = requests.get(full_url)
    return result

print(get_request(f"https://api.vk.com/method/friends.get",
                  {"user_id": 89767667,
                   "access_token": "44180b226550eec7ba7ae1dd56d860eb6d4ebefd8b8f9fb160fb0008aa5333e3e7686ca701c56231b93fa",
                   "v": "5.95"}).json())
