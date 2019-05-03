# -*- coding: utf-8 -*-

import keyring
import requests
from bs4 import BeautifulSoup
from .colors import Color as Col
import sys


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


def validate_password(username, password):
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