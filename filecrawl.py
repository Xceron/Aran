# coding: utf8
import filehandling
import requests
import re
import zipfile
import io
import pickle
import os
from bs4 import BeautifulSoup
import config_handling
import credentials


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
                print("User or Studip seems to be offline.")
                input("Press any key to exit")
                exit()
            else:
                payload = {"security_ticket": security_token,
                           "login_ticket": login_ticket,
                           "loginname": username,
                           "password": password}
                login_start = r.post("https://studip.uni-trier.de/index.php?again=yes", data=payload)
                if "angemeldet" in login_start.text:
                    return True
                else:
                    print("Wrong username and/or password")
                    return False
        except AttributeError:
            # weird cases where AttributeError gets thrown
            get_files()


def get_files():
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
                print("User or Studip seems to be offline.")
                input("Press any key to exit")
                exit()
            else:
                payload = {"security_ticket": security_token,
                           "login_ticket": login_ticket,
                           "loginname": config_handling.get_value("username"),
                           "password": credentials.get_credentials(config_handling.get_value("username"))}
                login_start = r.post("https://studip.uni-trier.de/index.php?again=yes", data=payload)
                if "angemeldet" in login_start.text:
                    print("Login successful!")
                else:
                    print("Wrong password and/or username")
                    input("Press any key to exit")
                    exit()
        except AttributeError:
            # weird cases where AttributeError gets thrown
            get_files()
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
            cookies_path = os.path.expanduser("~/Documents/cookies")
            save_cookies(r.cookies, cookies_path)
            soup = BeautifulSoup(site_get.text, "html.parser")
            folder_name = filehandling.make_folder_name(soup.find("title")["data-original"])
            if not os.path.exists(dst_folder + sl + folder_name):  # checks if the folder already exists
                os.makedirs(dst_folder + sl + folder_name)  # creates destination folder
            download_folder(site_get, dst_folder + sl + folder_name)


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
    sl = filehandling.slash()
    cookies_path = os.path.expanduser("~/Documents/cookies")
    cookies = load_cookies(cookies_path)
    folder_url = get_links_from_site(url.text, "https://studip.uni-trier.de/dispatch.php/file/download_folder/+(.*)")
    for folders in folder_url:
        response = requests.get(folders, stream=True, cookies=cookies)
        z = zipfile.ZipFile(io.BytesIO(response.content))
        z.extractall(path)
        with open(path + sl + "PLACEHOLDER_TO_DELETE", "wb") as out_file:
            out_file.write(response.content)
        print("Successfully downloaded a folder!")
    files_url = get_links_from_site(url.text, "https://studip.uni-trier.de/dispatch.php/file/details/+(.*)")
    for files in files_url:
        overview_page = requests.get("https://studip.uni-trier.de/dispatch.php/file/details/" + files, stream=True,
                                     cookies=cookies)
        if "Herunterladen" in overview_page.text:
            file_url = get_links_from_site(overview_page.text, "https://studip.uni-trier.de/sendfile.php(.*)")[0]
            try:
                fixed_url = file_url.group(1).replace("&amp;", "&")
                response = requests.get("https://studip.uni-trier.de/sendfile.php" + fixed_url, cookies=cookies)
                file_name = re.search("file_name=(.*)", fixed_url)
                file_name = file_name.group(1)
                file_name = file_name.replace("+", " ")
                with open(path + sl + file_name, "wb") as out_file:
                    out_file.write(response.content)
                print("Successfully downloaded a file!")
            except AttributeError:
                download_folder(url, path)
        else:
            pass


def main():
    documents_path = os.path.expanduser("~/Documents/Filecrawl_config.json")
    if not os.path.exists(documents_path):
        print("No config found \n"
              "Setup begins")
        config_handling.create_json_config()
        if os.path.exists(documents_path):
            print("Successfully created config in the \"Documents\" folder.\n"
                  "Starting the download")
        else:
            main()
    get_files()
    filehandling.cleanup(config_handling.get_value("path"))
    input("Press any key to exit")
    exit()


if __name__ == "__main__":
    main()
