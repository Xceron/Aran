#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from typing import Generator
import json


def make_folder_name(old_name: str) -> str:
    """
    removes certain keywords from folder name and changes it accordingly if the user specified replacements
    :param old_name: not formatted name
    :return: gets rid of useless words for a easier to find folder name in dst_folder
    """
    json_file = open(os.path.join(os.getcwd(), "aran_config.json"))
    json_data = json.load(json_file)["replacements"]
    for key, values in json_data.items():
        if key in old_name:
            return values
    old_name = old_name.strip()
    for sign in ["Vorlesung: ", "Übung: ", "Tutorium: ", " - Dateien", "sonstige: "]:
        old_name = old_name.replace(sign, "")
    return old_name


def get_file_size_of_dir(root_dir: str) -> Generator[int]:
    """
    creates a list that represents the folder structure of root_dir
    :param root_dir: directory where to start from
    :return: yields the file sizes from the directory
    """
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            try:
                yield os.stat(os.path.join(root, file)).st_size
            except FileNotFoundError:
                pass
