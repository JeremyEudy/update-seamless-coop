#!/usr/bin/env python3

import requests
import configparser
import zipfile


GAME_DIR = "/mnt/windows/Games/Steam/steamapps/common/ELDEN RING/Game"

MOD_URL = "https://api.github.com/repos/LukeYui/EldenRingSeamlessCoopRelease/releases/latest"

old_config = configparser.ConfigParser()
old_config.read(f"{GAME_DIR}/SeamlessCoop/ersc_settings.ini")
old_config_dict = {
    section: {
        key: value for key, value in old_config[section].items()
    } for section in old_config.sections()
}

try:
    github_response = requests.get(MOD_URL)
except Exception as e:
    print(f"Exception: {e}")

latest_release = github_response.json()
for asset in latest_release["assets"]:
    if asset["name"].endswith(".zip"):
        zip_url = asset["browser_download_url"]
        break

if zip_url:
    zip_response = requests.get(zip_url)
    with open(f"{GAME_DIR}/SeamlessCoop.zip", "wb") as f:
        f.write(zip_response.content)

with zipfile.ZipFile(f"{GAME_DIR}/SeamlessCoop.zip", "r") as zip_file:
    zip_file.extractall(GAME_DIR)

new_config = configparser.ConfigParser()
new_config.read(f"{GAME_DIR}/SeamlessCoop/ersc_settings.ini")

if old_config:
    for section in new_config.sections():
        for key in new_config[section].keys():
            if old_config_dict.get(section) and old_config_dict[section].get(key):
                new_config[section][key] = old_config_dict.get(section).get(key)

with open(f"{GAME_DIR}/SeamlessCoop/ersc_settings.ini", "w+") as config_file:
    new_config.write(config_file)
