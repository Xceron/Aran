#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
from filecrawl import credentials
import tkinter
from tkinter import filedialog
import os
import getpass

from .colors import Color as Col


def create_json_config():
    """
    :return: saves into the json file
    """
    positive_answers = ["yes", "y", "ye", "ja", "+", "1"]
    negative_answers = ["no", "n", "nein", "-", "0"]
    data = {
        "username": "NAME",
        "path": "",
        "backup_bigger": "x",
        "backup_smaller": "x",
        "moodle": "x",
        "download_videos": "x"
    }

    # username and password

    def check_credentials():
        print(Col.OK + "Enter your Studip username:")
        username = input()
        print(Col.OK + "Enter your Studip password: ")
        password = getpass.getpass()
        data["username"] = username
        credentials.save_credentials(username, password)

    check_credentials()
    while not credentials.validate_password(data["username"], credentials.get_credentials(data["username"])):
        check_credentials()
    # path
    while not (os.path.exists(data["path"])):
        print(Col.OK + "Enter the path where the files should be downloaded. If you need help, type \"help\".")
        path = input()
        if path == "help":
            tkinter.Tk().withdraw()
            path = filedialog.askdirectory()
        data["path"] = path
    # backup version number 1
    while not (type(data["backup_bigger"]) == bool):
        print(Col.OK + "Do you want to backup the old files, if the new file is bigger? \n"
              + Col.OK + "This can happen if the new file gets expanded [y/n]")
        backup_big_input = input()
        if backup_big_input in positive_answers:
            data["backup_bigger"] = True
        elif backup_big_input in negative_answers:
            data["backup_bigger"] = False
    # backup version number 2
    while not (type(data["backup_smaller"]) == bool):
        print(Col.OK + "Do you want to backup the old files, if the new file is smaller? \n"
              + Col.OK + "This can happen if the new file gets compressed [y/n]")
        backup_small_input = input()
        if backup_small_input in positive_answers:
            data["backup_smaller"] = True
        elif backup_small_input in negative_answers:
            data["backup_smaller"] = False
    while not (type(data["moodle"]) == bool):
        print(Col.OK + "Do you want to download files from moodle? [y/n]")
        moodle_input = input()
        if moodle_input in positive_answers:
            data["moodle"] = True
            while not (type(data["download_videos"]) == bool):
                print(Col.OK + "Do you want to download videos? [y/n]")
                video_input = input()
                if video_input in positive_answers:
                    data["download_videos"] = True
                elif video_input in negative_answers:
                    data["download_videos"] = False
        elif moodle_input in negative_answers:
            data["moodle"] = False
            data["download_videos"] = False
    # convert into json data and save it
    data_json = json.dumps(data, indent=4)
    documents_path = os.path.expanduser("~/Documents/Filecrawl_config.json")
    # documents_path = "Filecrawl_config.json"
    with open(documents_path, "w") as file:
        file.write(data_json)


def get_value(key):
    """
    :param key: key of json file
    :return: value of key
    """
    documents_path = os.path.expanduser("~/Documents/Filecrawl_config.json")
    # documents_path = "Filecrawl_config.json"
    with open(documents_path, "r") as file:
        data = json.load(file)
        return data[key]