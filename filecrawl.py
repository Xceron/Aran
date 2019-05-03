#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
import re
import zipfile
import io
import pickle
import os
import platform
import sys
from bs4 import BeautifulSoup

from filecrawl import filehandling
from filecrawl import credentials
from filecrawl import config_handling
from filecrawl.colors import Color as Col


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
            download_files_from_studip()


def download_files_from_studip():
    """
    :return: downloads all files/folders from Studip
    """
    sl = filehandling.slash()
    dst_folder = config_handling.get_value("path")
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
                           "loginname": config_handling.get_value("username"),
                           "password": credentials.get_credentials(config_handling.get_value("username"))}
                login_start = r.post("https://studip.uni-trier.de/index.php?again=yes", data=payload)
                if "angemeldet" in login_start.text:
                    print(Col.SUCCESS + "Login successful!")
                else:
                    print(Col.ERROR + "Wrong password and/or username")
                    input(Col.WARNING + "Press any key to exit")
                    sys.exit(0)
        except AttributeError:
            # weird cases where AttributeError gets thrown
            download_files_from_studip()
        my_courses = r.get("https://studip.uni-trier.de/dispatch.php/my_courses")
        my_courses_links = get_links_from_site(my_courses.text, "2Fcourse%2Ffiles")
        module_links = []
        for j in range(len(my_courses_links)):  # gathers all links to My Courses
            if my_courses_links[j] == my_courses_links[j - 1]:
                course_id = re.search("auswahl=(.*)&", my_courses_links[j]).group(1)
                course_id = course_id.replace("auswahl=", "")
                course_id = course_id.replace("&amp", "")
                module_links.append("https://studip.uni-trier.de/dispatch.php/course/files?cid=" + course_id)
        for sites in module_links:  # My Courses - files overview site
            site_get = r.get(sites)
            save_cookies(r.cookies, "cookies")
            soup = BeautifulSoup(site_get.text, "html.parser")
            folder_name = filehandling.make_folder_name(soup.find("title")["data-original"])
            if not os.path.exists(dst_folder + sl + folder_name):  # checks if the folder already exists
                os.makedirs(dst_folder + sl + folder_name)  # creates destination folder
            download_folder(site_get, dst_folder + sl + folder_name)


def download_files_from_moodle():
    path = config_handling.get_value("path")
    with requests.Session() as r:
        sl = filehandling.slash()
        login_site = r.get("https://moodle.uni-trier.de/login/index.php")
        if not login_site.ok:
            print(Col.ERROR + "User or moodle seems to be offline.")
            input(Col.WARNING + "Press any key to exit")
            sys.exit()
        else:
            payload = {"username": config_handling.get_value("username"),
                       "password": credentials.get_credentials(config_handling.get_value("username"))
                       }
            # Login
            r.post("https://moodle.uni-trier.de/login/index.php", data=payload)
            navigation_site = r.get("https://moodle.uni-trier.de/my/")
            if "Meine Kurse" in navigation_site.text:
                print(Col.SUCCESS + "Login to moodle successsful!")
            else:
                print(Col.ERROR + "Wrong password and/or username")
                input(Col.WARNING + "Press any key to exit")
                sys.exit()
        # get all courses
        my_course_links = get_links_from_site(navigation_site.text, "course")
        for course_site in my_course_links:
            course_overview = r.get(course_site)
            files_urls = get_links_from_site(course_overview.text, "/resource/")
            course_soup = BeautifulSoup(course_overview.text, "html.parser")
            course_name = course_soup.find("h1").text
            if not os.path.exists(path + sl + course_name):
                os.makedirs(path + sl + course_name)
            # Download files
            for files_ov_url in files_urls:
                files_ov_site = r.get(files_ov_url)
                try:
                    file_link = get_links_from_site(files_ov_site.text, "/pluginfile.php/")[0]
                    response_header = r.head(file_link)
                    content_type = response_header.headers.get("content-type")
                    if "video" in content_type:
                        if config_handling.get_value("download_videos"):
                            if is_new_video(response_header.headers, path + sl + course_name):
                                print(Col.OK + "Found a new video, downloading may take a while")
                                response = r.get(file_link)
                                soup = BeautifulSoup(files_ov_site.text, "html.parser")
                                file_name = soup.find("a", href=re.compile(file_link)).text
                                with open(path + sl + course_name + sl + file_name, "wb") as out_file:
                                    out_file.write(response.content)
                                print(Col.SUCCESS + "Successfully downloaded a video!")
                            else:
                                print(Col.OK + "Found an already downloaded video, skipping this one")
                        else:
                            pass
                    else:
                        response = r.get(file_link)
                        soup = BeautifulSoup(files_ov_site.text, "html.parser")
                        file_name = soup.find("a", href=re.compile(file_link)).text
                        with open(path + sl + course_name + sl + file_name, "wb") as out_file:
                            out_file.write(response.content)
                        print(Col.SUCCESS + "Successfully downloaded a file!")
                except IndexError:
                    pass


def is_new_video(html_header, path):
    """
    :param html_header: header to moodle site
    :param path: download path
    :return: boolean
    """
    filename = re.search("filename=\"(.*)\"\', 'Last", str(html_header)).group(1)
    for root, dirs, files in os.walk(path):
        for file_names in files:
            if file_names == filename:
                return False
    return True

def save_cookies(requests_cookiejar, filename):
    """
    :param requests_cookiejar: CookieJar object
    :param filename: filename of the cookie
    :return: saves the cookie in the same directory as this .py
    """
    with open(filename, "wb") as f:
        pickle.dump(requests_cookiejar, f)


def load_cookies(filename):
    """
    :param filename: filename used in save_cookies
    :return: cookieJar object used for saving the session
    """
    with open(filename, "rb") as f:
        return pickle.load(f)


def get_links_from_site(html, url):
    """
    :param html: html text
    :param url: url with regex
    :return: list with urls
    """
    soup = BeautifulSoup(html, "html.parser")
    site_tags = soup.find_all("a", href=re.compile(url))
    links = [tags.get("href") for tags in site_tags]
    return links


def download_folder(url, path):
    """
    :param url: url to a a site containing files and/or folders
    :param path: path to dir to download
    :return: download file to the directory and rename it accordingly
    """
    if len(path) >= 255 and platform == "Windows":  # Windows 255 char path length limitation
        path = u"\\\\?\\{}".format(path)
    sl = filehandling.slash()
    cookies = load_cookies("cookies")
    folder_url = get_links_from_site(url.text, "https://studip.uni-trier.de/dispatch.php/file/download_folder/+(.*)")
    for folders in folder_url:
        response = requests.get(folders, stream=True, cookies=cookies)
        z = zipfile.ZipFile(io.BytesIO(response.content))
        try:
            z.extractall(r"{}".format(path))
        except FileNotFoundError:
            # This exception gets called when the downloaded zip contains a whitespace as the last character before
            # the suffix, e.g. "zip_folder .zip" and the operating system is Windows. Windows removes the last
            # whitespace automatically resulting in an error when calling extractall(). This is a workaround.
            with open(path + sl + "TEMPORARY_ZIP_TO_DELETE.zip", "wb") as out_file:
                out_file.write(response.content)
            with zipfile.ZipFile(path + sl + "TEMPORARY_ZIP_TO_DELETE.zip") as zipfolder:
                for name in zipfolder.filelist:
                    if name.is_dir():
                        if not os.path.exists(path + sl + name.filename.replace(" /", "\\")):
                            os.makedirs(path + sl + name.filename.replace(" /", "\\"))
                    with zipfolder.open(name.filename) as zip_file_in_folder:
                        zip_bytes = zip_file_in_folder.read()
                        if zip_bytes != b'':  # only files (b'' are folders which were already created before)
                            with open(path + sl + name.filename.replace(" /", "\\"), "wb") as out_file:
                                out_file.write(zip_bytes)
            os.remove(path + sl + "TEMPORARY_ZIP_TO_DELETE.zip")
        print(Col.SUCCESS + "Successfully downloaded a folder!")
    files_url = get_links_from_site(url.text, "https://studip.uni-trier.de/dispatch.php/file/details/+(.*)")
    for files in files_url:
        overview_page = requests.get(files, stream=True, cookies=cookies)
        if "Herunterladen" in overview_page.text:
            file_url = get_links_from_site(overview_page.text, "https://studip.uni-trier.de/sendfile.php(.*)")[0]
            try:
                fixed_url = file_url.replace("&amp;", "&")
                response = requests.get(fixed_url, cookies=cookies)
                file_name = re.search("file_name=(.*)", fixed_url)
                file_name = file_name.group(1)
                file_name = file_name.replace("+", " ")
                with open(path + sl + file_name, "wb") as out_file:
                    out_file.write(response.content)
                print(Col.SUCCESS + "Successfully downloaded a file!")
            except AttributeError:
                download_folder(url, path)
        else:
            pass


def main():
    documents_path = os.path.expanduser("~/Documents/Filecrawl_config.json")
    # documents_path = "Filecrawl_config.json"
    if not os.path.exists(documents_path):
        print(Col.WARNING + "No config found \n"
              + Col.OK + "Setup begins")
        config_handling.create_json_config()
        if os.path.exists(documents_path):
            print(Col.SUCCESS + "Successfully created config in the User folder.\n"
                  + Col.OK + "Starting the download")
        else:
            main()
    try:
        download_files_from_studip()
        if config_handling.get_value("moodle"):
            download_files_from_moodle()
        filehandling.cleanup(config_handling.get_value("path"))
    except requests.ConnectionError:
        print(Col.ERROR + "No internet connection found.")
    print(Col.WARNING + "Press any key to exit")
    input()
    sys.exit(0)


if __name__ == "__main__":
    main()
