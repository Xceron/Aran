#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import os
import getpass
import keyring
import requests
from bs4 import BeautifulSoup
import sys
from typing import Union

from colors import Color as Col


def save_credentials(username: str, password: str) -> None:
    """
    :param username: username used for Studip
    :param password: password used for Studip
    :return: sets username and password in local keyring
    """
    keyring.set_password("StudipCrawl", username, password)


def get_credentials(username: str) -> None:
    """
    :param username: username used for Studip
    :return: password
    """
    return keyring.get_password("StudipCrawl", username)


def validate_password(username: str, password: str) -> None:
    """
    :param username: username used for Studip
    :param password: password used for Studip
    :return: boolean if combination is right
    """
    with requests.Session() as r:
        homepage = r.get("https://studip.uni-trier.de/index.php?again=yes")
        soup = BeautifulSoup(homepage.text, "html.parser")
        security_token = soup.find("input", {"name": "security_token"})["value"]
        login_ticket = soup.find("input", {"name": "login_ticket"})["value"]
        try:
            if not homepage.ok:
                print(Col.ERROR + "User or Studip seems to be offline.")
                input(Col.WARNING + "Press any key to exit")
                sys.exit(0)
            else:
                payload = {"security_ticket": security_token,
                           "login_ticket": login_ticket,
                           "loginname": username,
                           "password": password}
                login_start = r.post("https://studip.uni-trier.de/index.php?again=yes", data=payload)
                if "angemeldet" in login_start.text:
                    return True
                else:
                    print(Col.ERROR + "Wrong username and/or password")
                    return False
        except AttributeError:
            # weird cases where AttributeError gets thrown
            validate_password(username, password)


def create_json_config() -> None:
    """
    :return: saves into the json file
    """
    positive_answers = ["yes", "y", "ye", "ja", "+", "1"]
    negative_answers = ["no", "n", "nein", "-", "0"]
    data = {
        "username": "NAME",
        "path": "",
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
        save_credentials(username, password)

    check_credentials()
    while not validate_password(data["username"], get_credentials(data["username"])):
        check_credentials()
    # path
    while not (os.path.exists(data["path"])):
        print(Col.OK + "Enter the path where the files should be downloaded. If you need help, type \"help\".")
        path: str = input()
        if path == "help":
            try:
                import tkinter
                from tkinter import filedialog
                tkinter.Tk().withdraw()
                path = filedialog.askdirectory()
            except ImportError:
                print(Col.ERROR + "Your Python Version is missing Tkinter, it is not possible to open the GUI. Type "
                                  "the path manually")
        data["path"] = path
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
    json_path = os.path.join(os.getcwd(), "aran_config.json")
    with open(json_path, "w") as file:
        file.write(data_json)


def get_value(key: str) -> Union[bool, str]:
    """
    :param key: key of json file
    :return: value of key
    """
    json_path = os.path.join(os.getcwd(), "aran_config.json")
    if not os.path.exists(json_path):
        print(Col.WARNING + "No config found \n"
              + Col.OK + "Setup begins")
        create_json_config()
        if os.path.exists(json_path):
            print(Col.SUCCESS + f"Successfully created config in {os.getcwd()}.\n"
                  + Col.OK + "Starting the download")
    else:
        with open(json_path, "r") as file:
            data = json.load(file)
            return data[key]
