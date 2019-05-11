#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import platform
from functools import reduce
from collections.abc import MutableMapping


def slash():
    """
    :return: appropiate slash for Unix/macOS or Windows based systems
    """
    if platform.system() == "Windows":
        return "\\"
    else:
        return "//"


def make_folder_name(old_name):
    """
    :param old_name: unformatted name
    :return: gets rid of useless words for a easier to find folder name in dst_folder
    """
    old_name = old_name.strip()
    for sign in ["Vorlesung", "Übung: ", "Tutorium", " - Dateien", ": "]:
        old_name = old_name.replace(sign, "")
    return old_name


def get_directory_structure(rootdir):
    """
    Creates a nested dictionary that represents the folder structure of rootdir
    """
    return_dict = {}
    rootdir = rootdir.rstrip(os.sep)
    start = rootdir.rfind(os.sep) + 1
    for root, dirs, files in os.walk(rootdir):
        folders = root[start:].split(os.sep)
        subdir = dict.fromkeys(files)
        for name in files:
            subdir[name] = os.stat(os.path.join(root, name)).st_size
        parent = reduce(dict.get, folders[:-1], return_dict)
        parent[folders[-1]] = subdir
    return return_dict


def findkey(dictionary, key):
    try:
        if key in dictionary:
            return dictionary[key]
        for key_di, sub_dictionary in dictionary.items():
            val = findkey(sub_dictionary, key)
            if val:
                return val
    except TypeError:
        return None


def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def find_parent_keys(d, target_key, parent_key=None):
    for k, v in d.items():
        if k == target_key:
            yield parent_key
        if isinstance(v, dict):
            for res in find_parent_keys(v, target_key, k):
                yield res
