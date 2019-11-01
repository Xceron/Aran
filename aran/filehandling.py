#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from collections import Iterable
from functools import reduce
from collections.abc import MutableMapping


def make_folder_name(old_name: str) -> str:
    """
    :param old_name: unformatted name
    :return: gets rid of useless words for a easier to find folder name in dst_folder
    """
    old_name = old_name.strip()
    for sign in ["Vorlesung", "Übung: ", "Tutorium", " - Dateien", ": "]:
        old_name = old_name.replace(sign, "")
    return old_name


def get_directory_structure(rootdir: str) -> dict:
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


def find_key(dictionary: dict, key: object) -> object:
    try:
        if key in dictionary:
            return dictionary[key]
        for key_di, sub_dictionary in dictionary.items():
            val = find_key(sub_dictionary, key)
            if val:
                return val
    except TypeError:
        return None


def flatten(d: dict, parent_key: object = '', sep: object = '_') -> dict:
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def find_parent_keys(d: dict, target_key: object, parent_key: object = None) -> Iterable:
    for k, v in d.items():
        if k == target_key:
            yield parent_key
        if isinstance(v, dict):
            for res in find_parent_keys(v, target_key, k):
                yield res
