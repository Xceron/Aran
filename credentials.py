# coding: utf8
import keyring


def save_credentials(username, password):
    """
    :param username: username used for Studip
    :param password: password used for Studip
    :return: sets username and password in local keyring
    """
    keyring.set_password("StudipCrawl", username, password)


def get_credentials(username):
    """
    :param username: username used for Studip
    :return: password
    """
    return keyring.get_password("StudipCrawl", username)
