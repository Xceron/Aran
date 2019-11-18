#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
from re import search, compile
import os
import platform
import sys
from bs4 import BeautifulSoup

from aran import filehandling
from aran import config_handling
from aran.colors import Color as Col


class GeneralDownloadManager():

    def __init__(self):
        self.session = requests.session()
        self.path = config_handling.get_value("path")
        self.username = config_handling.get_value("username")

    @staticmethod
    def is_new_video(html_header: object, path: str) -> bool:
        """
        :param html_header: header to moodle site
        :param path: download path
        :return: boolean
        """
        filename = search("filename=\"(.*)\"\', 'Last", str(html_header)).group(1)
        for root, dirs, files in os.walk(path):
            for file_names in files:
                if file_names == filename:
                    return False
        return True

    @staticmethod
    def get_links_from_site(html: str, url: str) -> list:
        """
        :param html: html text
        :param url: url with regex
        :return: list with urls
        """
        soup = BeautifulSoup(html, "html.parser")
        site_tags = soup.find_all("a", href=compile(url))
        links = [tags.get("href") for tags in site_tags]
        return links

    @staticmethod
    def get_size_from_head(head: object) -> int:
        return head.headers.get("Content-Length")

    @staticmethod
    def get_name_from_head(head: object) -> str:
        try:
            return search("filename=\"(.*)\"", head.headers.get("Content-Disposition")).group(1)
        except AttributeError:
            return search("filename\*=UTF-8''(.*)", head.headers.get("Content-Disposition")).group(1)  # TODO untersuche header nach Namen, um RegEx anzupassen

    @staticmethod
    def remove_duplicates(entry_list: list) -> list:
        return list(dict.fromkeys(entry_list))

    def is_new_file(self, head: object, foldername: str, parent: str) -> bool:
        dic = filehandling.get_directory_structure(self.path)
        head_file_size = self.get_size_from_head(head)
        if not parent:
            foldername = list(filehandling.find_parent_keys(dic, foldername))[0]
        folder = filehandling.find_key(dic, foldername)
        if folder is not None:
            folder = filehandling.flatten(folder)
            if int(head_file_size) in folder.values():
                return False
            else:
                return True
        else:
            return True


class StudipDownloader(GeneralDownloadManager):

    def __init__(self):
        super().__init__()

    def download_files_from_studip(self) -> None:
        """
        :return: downloads all files/folders from Studip
        """
        dst_folder = self.path
        with self.session as r:
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
                               "loginname": self.username,
                               "password": config_handling.get_credentials(self.username)}
                    login_start = r.post("https://studip.uni-trier.de/index.php?again=yes", data=payload)
                    if "angemeldet" in login_start.text:
                        print(Col.SUCCESS + "Login successful!")
                    else:
                        print(Col.ERROR + "Wrong password and/or username")
                        input(Col.WARNING + "Press any key to exit")
                        sys.exit(0)
            except AttributeError:
                # weird cases where AttributeError gets thrown
                self.download_files_from_studip()
            my_courses = r.get("https://studip.uni-trier.de/dispatch.php/my_courses")
            my_courses_links = super().get_links_from_site(my_courses.text, "2Fcourse%2Ffiles")
            module_links = []
            for j in range(len(my_courses_links)):  # gathers all links to My Courses
                if my_courses_links[j] == my_courses_links[j - 1]:
                    course_id = search("auswahl=(.*)&", my_courses_links[j]).group(1)
                    course_id = course_id.replace("auswahl=", "")
                    course_id = course_id.replace("&amp", "")
                    module_links.append("https://studip.uni-trier.de/dispatch.php/course/files?cid=" + course_id)
            for sites in module_links:  # My Courses - files overview site
                site_get = r.get(sites)
                soup = BeautifulSoup(site_get.text, "html.parser")
                folder_name = filehandling.make_folder_name(soup.find("title")["data-original"])
                if not os.path.exists(os.path.join(dst_folder, folder_name)):  # checks if the folder already exists
                    os.makedirs(os.path.join(dst_folder, folder_name))  # creates destination folder
                self.download_folder(site_get, os.path.join(dst_folder, folder_name))

    def download_folder(self, url: object, path: str) -> None:
        """
        :param url: url to a a site containing files and/or folders
        :param path: path to dir to download
        :return: download file to the directory and rename it accordingly
        """
        
        if len(path) >= 255 and platform == "Windows":  # Windows 255 char path length limitation
            path = u"\\\\?\\{}".format(path)
        with self.session as r:
            folder_urls = super().get_links_from_site(url.text, "https://studip.uni-trier.de/dispatch.php/course/files/index/(.*)")
            folder_urls = super().remove_duplicates(folder_urls)
            for folders in range(len(folder_urls)):
                folder_site = r.get(folder_urls[folders])
                soup = BeautifulSoup(folder_site.text, "html.parser")
                tag = soup.find_all("a", href=folder_urls[folders])
                folder_name = filehandling.make_folder_name(tag[0].text)
                files_url = super().get_links_from_site(folder_site.text,
                                                "https://studip.uni-trier.de/dispatch.php/file/details/+(.*)")
                files_url = super().remove_duplicates(files_url)
                for files in files_url:
                    self.download_file(files, path, folders == 0, folder_name)
                folders += 1

    def download_file(self, files_url: str, path: str, parent: str, folder_name: str) -> None:
        if not parent:
            if not os.path.exists(os.path.join(path, folder_name)):
                os.makedirs(os.path.join(path, folder_name))
            path = os.path.join(path, folder_name)
        with self.session as r:
            overview_page = r.get(files_url, stream=True)
            if "Herunterladen" in overview_page.text:
                file_url = super().get_links_from_site(overview_page.text, "https://studip.uni-trier.de/sendfile.php(.*)")[0]
                fixed_url = file_url.replace("&amp;", "&")
                response_header = r.head(fixed_url)
                if super().is_new_file(response_header, os.path.basename(path), parent):
                    response = r.get(fixed_url)
                    file_name = search("file_name=(.*)", fixed_url)
                    file_name = file_name.group(1)
                    file_name = file_name.replace("+", " ")
                    with open(os.path.join(path, file_name), "wb") as out_file:
                        out_file.write(response.content)
                    print(Col.SUCCESS + "Successfully downloaded the following file: {}".format(file_name))
                else:
                    print(Col.OK + "Already downloaded {}, skipping this one".format(super().get_name_from_head(response_header)))
            else:
                pass


class MoodleDownloader(GeneralDownloadManager):

    def __init__(self):
        super().__init__()
        self.download_videos = config_handling.get_value("download_videos")

    def download_files_from_moodle(self) -> None:
        with self.session as r:
            login_site = r.get("https://moodle.uni-trier.de/login/index.php")
            if not login_site.ok:
                print(Col.ERROR + "User or moodle seems to be offline.")
                input(Col.WARNING + "Press any key to exit")
                sys.exit()
            else:
                payload = {"username": self.username,
                           "password": config_handling.get_credentials(self.username)
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
            my_course_links = super().get_links_from_site(navigation_site.text, "course")
            for course_site in my_course_links:
                course_overview = r.get(course_site)
                files_urls = super().get_links_from_site(course_overview.text, "/resource/")
                course_soup = BeautifulSoup(course_overview.text, "html.parser")
                course_name = course_soup.find("h1").text
                if not os.path.exists(os.path.join(self.path, course_name)):
                    os.makedirs(os.path.join(self.path, course_name))
                # Download files
                for files_ov_url in files_urls:
                    files_ov_site = r.get(files_ov_url)
                    try:
                        file_link = super().get_links_from_site(files_ov_site.text, "/pluginfile.php/")[0]
                        response_header = r.head(file_link)
                        content_type = response_header.headers.get("content-type")
                        soup = BeautifulSoup(files_ov_site.text, "html.parser")
                        file_name = soup.find("a", href=compile(file_link)).text
                        if "video" in content_type:
                            if self.download_videos:
                                if super().is_new_video(response_header.headers, os.path.join(self.path, course_name)):
                                    print(Col.OK + "Found a new video, downloading may take a while")
                                    response = r.get(file_link)
                                    with open(os.path.join(self.path, course_name, file_name), "wb") as out_file:
                                        out_file.write(response.content)
                                    print(Col.SUCCESS + "Successfully downloaded a video!")
                                else:
                                    print(Col.OK + "Found an already downloaded video, skipping this one")
                            else:
                                pass
                        else:
                            if super().is_new_file(response_header, course_name, False):
                                response = r.get(file_link)
                                with open(os.path.join(self.path, course_name, file_name), "wb") as out_file:
                                    out_file.write(response.content)
                                print(Col.SUCCESS + "Successfully downloaded the following file: {}".format(file_name))
                            else:
                                print(Col.OK + "Already downloaded {}, skipping this one".format(file_name))
                    except IndexError:
                        pass


def main() -> None:
    sd = StudipDownloader()
    sd.download_files_from_studip()
    if config_handling.get_value("moodle"):
        md = MoodleDownloader()
        md.download_files_from_moodle()


if __name__ == '__main__':
    main()
