#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import asyncio
import json


def make_folder_name(old_name: str) -> str:
    """
    :param old_name: not formatted name
    :return: gets rid of useless words for a easier to find folder name in dst_folder
    """
    json_file = open(os.path.join(os.getcwd(), "aran_config.json"))
    json_data = json.load(json_file)["synonyms"]
    for key, values in json_data.items():
        if key in old_name:
            return values
    old_name = old_name.strip()
    for sign in ["Vorlesung: ", "Übung: ", "Tutorium: ", " - Dateien", "sonstige: "]:
        old_name = old_name.replace(sign, "")
    return old_name


async def get_file_size_of_dir(root_dir: str) -> list:
    """
    Creates a list that represents the folder structure of root_dir
    """
    return_list = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            try:
                return_list.append(os.stat(os.path.join(root, file)).st_size)
            except FileNotFoundError:
                pass
    return return_list
