import json
import filecrawl
import credentials
import tkinter
from tkinter import filedialog
import os


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
        "backup_smaller": "x"
    }

    # username and password

    def check_credentials():
        username = input("Enter your Studip username: ")
        password = input("Enter your Studip password: ")
        data["username"] = username
        credentials.save_credentials(username, password)

    check_credentials()
    while not filecrawl.validate_password(data["username"], credentials.get_credentials(data["username"])):
        check_credentials()
    # path
    while not (os.path.exists(data["path"])):
        path = input("Enter the path where the files should be saved. If you need help, type \"help\". ")
        if path == "help":
            tkinter.Tk().withdraw()
            data["path"] = filedialog.askdirectory()
    # backup version number 1
    while not (type(data["backup_bigger"]) == bool):
        backup_big_input = input("Do you want to save the old files, if the new file is bigger? \n"
                                 "This can happen if the new file gets expanded [y/n]")
        if backup_big_input in positive_answers:
            data["backup_bigger"] = True
        elif backup_big_input in negative_answers:
            data["backup_bigger"] = False
    # backup version number 2
    while not (type(data["backup_smaller"]) == bool):
        backup_small_input = input("Do you want to save the old files, if the new file is smaller? \n"
                                   "This can happen if the new file gets compressed [y/n]")
        if backup_small_input in positive_answers:
            data["backup_smaller"] = True
        elif backup_small_input in negative_answers:
            data["backup_smaller"] = False
    # convert into json data and save it
    data_json = json.dumps(data, indent=4)
    documents_path = os.path.expanduser("~/Documents/Filecrawl_config.json")
    with open(documents_path, "w") as file:
        file.write(data_json)


def get_value(key):
    """
    :param key: key of json file
    :return: value of key
    """
    documents_path = os.path.expanduser("~/Documents/Filecrawl_config.json")
    with open(documents_path, "r") as file:
        data = json.load(file)
        return data[key]