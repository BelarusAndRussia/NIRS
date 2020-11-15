import json


data = {
    "log_level": "DEBUG",
    "mode": "w",
    "encoding": "utf-8",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}

with open("local_settings.json", "w") as write_file:
    json.dump(data, write_file, indent=4)