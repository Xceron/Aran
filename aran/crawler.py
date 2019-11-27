#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
from re import search, compile
import os
import sys
from bs4 import BeautifulSoup
from multiprocessing import Process, Queue

from aran import setup_logger
from aran import filehandling
from aran import config_handling
from aran.colors import Color as Col


class GeneralDownloadManager:

    def __init__(self):
        self.logger = setup_logger.logger
        self.session = requests.Session()
        self.path = config_handling.get_value("path")
        self.username = config_handling.get_value("username")
        self.download_queue = Queue()  # Queue consisting lists [file, dir_to_save_file_to_including_file_name]
        # Queue containing as many Strings as there are Processes (without counting the download process)
        # Used only to determine when all processes are done -> Studip has been fully crawled
        self.process_queue = Queue()

    def remove_blacklisted_links(self, link_list: list) -> list:
        """
        takes a list containing links and removes blacklisted links
        :param link_list: list with links
        :return: list with links without blacklisted ones
        """
        self.logger.debug("Removing blacklisted links from link list")
        blacklist = config_handling.get_value("blacklist")
        common = set(link_list).intersection(blacklist)
        if len(common) == 0:
            return link_list
        else:
            for link in common:
                self.logger.info(f"Skipping {link} because you set it into the blacklist")
                self.logger.debug(f"Blacklisted: {link}")
            # Taken from https://stackoverflow.com/questions/18194968/python-remove-duplicates-from-2-lists
            return list(set(link_list).difference(blacklist))

    def get_links_from_site(self, html: str, url: str) -> list:
        """
        :param html: html text
        :param url: url with regex
        :return: list with urls
        """
        self.logger.debug(f"Getting links with regEx {url}")
        soup = BeautifulSoup(html, "html.parser")
        site_tags = soup.find_all("a", href=compile(url))
        links = [tags.get("href") for tags in site_tags]
        self.logger.debug(f"Found these links: {links}")
        return self.remove_blacklisted_links(links)

    def get_size_from_head(self, head: requests.Response) -> int:
        self.logger.debug("Getting file size from a HEAD")
        return head.headers.get("Content-Length")

    def get_name_from_head(self, head: requests.Response) -> str:
        self.logger.debug("Getting a file name from a HEAD")
        try:
            return search("filename=\"(.*)\"", head.headers.get("Content-Disposition")).group(1)
        except AttributeError:
            return search("filename\*=UTF-8''(.*)", head.headers.get("Content-Disposition")).group(1)

    @staticmethod
    def remove_duplicates(entry_list: list) -> list:
        return list(dict.fromkeys(entry_list))

    def should_file_be_downloaded(self, head: requests.Response, destination: str) -> bool:
        max_file_size = config_handling.get_value("maxSizeInMB")
        # max_file_size = 55
        blacklisted_file_extensions = config_handling.get_value("noDownload")
        # blacklisted_file_extensions = []
        # get root folder length
        download_path_length = len(self.path)
        # get the root folder name (self.path/root folder/names/that/get/removed
        parent_path = destination[download_path_length+1:].split(os.sep)[0]
        parent_folder = self.path + os.path.sep + parent_path
        head_file_size = int(self.get_size_from_head(head))
        head_file_name = self.get_name_from_head(head)
        if head_file_size / 1_000_000 > max_file_size:
            self.logger.info(f"Skipped {head_file_name} because it is too large")
            self.logger.debug(f"Too large: {head_file_name}")
            return False
        file_extension = head_file_name.split(".")[-1]
        if file_extension in blacklisted_file_extensions:
            self.logger.info(f"Skipped {head_file_name} because you blacklist .{file_extension}")
            self.logger.debug(f"Ignoring: {head_file_name}")
            return False
        folder_sizes = filehandling.get_file_size_of_dir(parent_folder)
        if int(head_file_size) in folder_sizes:
            self.logger.info(f"Already downloaded {head_file_name}, skipping this one")
            self.logger.debug(f"Duplicate: {head_file_name}")
            return False
        else:
            return True

    def download_files_from_queue(self) -> None:
        while not self.download_queue.empty():
            with self.session as s:
                file, location = self.download_queue.get()
                name = self.get_name_from_head(s.head(file))
                self.logger.info(f"Started downloading {name}")
                with open(location, "wb") as out_file:
                    out_file.write(s.get(file).content)
                    self.logger.info(f"Finished downloading {name}")
        return


class StudipDownloader(GeneralDownloadManager):

    def __init__(self):
        super().__init__()

    def login_into_studip(self) -> bool:
        self.logger.info("Login into StudIP")
        with self.session as r:
            homepage = r.get("https://studip.uni-trier.de/index.php?again=yes")
            soup = BeautifulSoup(homepage.text, "html.parser")
            security_token = soup.find("input", {"name": "security_token"})["value"]
            login_ticket = soup.find("input", {"name": "login_ticket"})["value"]
            try:
                if not homepage.ok:
                    self.logger.error("User or Studip seems to be offline.")
                    input(f"{Col.WARNING} Press any key to exit")
                    sys.exit(1)
                else:
                    payload = {"security_ticket": security_token,
                               "login_ticket": login_ticket,
                               "loginname": self.username,
                               "password": config_handling.get_credentials(self.username)}
                    login_start = r.post("https://studip.uni-trier.de/index.php?again=yes", data=payload)
                    if "angemeldet" in login_start.text:
                        self.logger.info("Login successful!")
                        return True
                    else:
                        self.logger.error("Wrong password and/or username")
                        input(Col.WARNING + "Press any key to exit")
                        sys.exit(1)
            except AttributeError:
                # weird cases where AttributeError gets thrown
                self.logger.debug("AttributeError, retrying login")
                self.login_into_studip()

    @staticmethod
    def clean_up_module_url(url: str) -> str:
        """
        removes the redirect from a module link
        :param url: link to a module
        :return: link to module without redirect
        """
        module_id = search("auswahl=(.*)&", url).group(1)
        module_id = module_id.replace("auswahl=", "")
        module_id = module_id.replace("&amp", "")
        return f"https://studip.uni-trier.de/dispatch.php/course/files?cid={module_id}"

    def get_all_modules_from_landing_page(self) -> list:
        output = list()
        self.logger.debug("Getting all module links from the landing page")
        with self.session as s:
            my_courses = s.get("https://studip.uni-trier.de/dispatch.php/my_courses")
            my_courses_links = self.get_links_from_site(my_courses.text, "2Fcourse%2Ffiles")
            no_duplicates_list = list(set(my_courses_links))
            for link in no_duplicates_list:
                output.append(self.clean_up_module_url(link))
            self.logger.debug(f"Found the following modules: {output}")
        return output

    def traverse_through_module(self, url: str):
        """
        gets the content of a module
        :param url:
        :return:
        """
        with self.session as s:
            site = s.get(url)
            soup = BeautifulSoup(site.text, "html.parser")
            folder_name = filehandling.make_folder_name(soup.find("title")["data-original"])
            self.logger.info(f"Getting files for {folder_name}")
            self.logger.debug(f"Traversing: {folder_name}")
            # if not os.path.exists(os.path.join(dst_folder, folder_name)):  # checks if the folder already exists
            #     self.logger.debug(f"Created a new folder: {os.path.join(dst_folder, folder_name)}")
            #     os.makedirs(os.path.join(dst_folder, folder_name))  # creates destination folder
            try:
                self.get_folders_of_site(site.text, "")
            except Exception as e:
                self.logger.debug("Error when traversing a module", e)
                return
            # self.process_queue.get()
            # if self.process_queue.empty():
            #     sys.exit(0)
            return
            # self.get_files_of_site(site.text)

    def generate_folder_name_from_site_structure(self, html: str, destination: str) -> os.path:
        """
        gets the folder structure from the header in the file overview and returns the path where the file should be
        downloaded
        :param html: file overview site url
        :return: path
        """
        soup = BeautifulSoup(html, "html.parser")
        container_tag = soup.find("div", {"class": "caption-container"})
        folder_structure = " ".join(container_tag.text.split())
        folder_structure = folder_structure.replace("Allgemeiner Dateiordner", "")
        folder_name = filehandling.make_folder_name(folder_structure)
        if destination == "":  # root folder
            folder_name = self.path + os.path.sep + folder_name
        else:  # subfolder
            folder_name = destination + os.path.sep + folder_name
        # Replaces // from "/Allgemeiner Dateiordner" with /
        folder_name = folder_name.replace(f"{os.path.sep}{os.path.sep}", os.path.sep)
        # Removes / from the path end if there is one
        if folder_name[-1] == os.path.sep:
            folder_name = folder_name[:-1]
        return folder_name

    def get_folders_of_site(self, html: str, destination: str) -> None:
        """
        gets all folders of a file overview site
        :param html:
        :param destination:
        :return:
        """
        with self.session as s:
            current_dst = self.generate_folder_name_from_site_structure(html, destination)
            self.get_files_of_site(html, current_dst)
            soup = BeautifulSoup(html, "html.parser")
            table_folder_section = soup.find("tbody", {"class", "subfolders"})
            if table_folder_section is None:
                return
            site_tags = table_folder_section.find_all("a",
                                                      href=compile(
                                                          "https://studip.uni-trier.de/dispatch.php/course/files/index/(.*)"))
            folder_urls = [tags.get("href") for tags in site_tags]
            folder_urls = list(set(folder_urls))  # remove duplicates
            if folder_urls is None:
                return
            else:
                for folder_url in folder_urls:
                    folder_url_site = s.get(folder_url)
                    self.logger.debug(f"Folder: {folder_url}")
                    # self.generate_folder_name_from_site_structure(folder_url_site.text, destination)
                    self.get_folders_of_site(folder_url_site.text, current_dst)
                return

    def get_files_of_site(self, html: str, destination: str) -> None:
        """
        adds all files to the download queue
        :param html: HTML of the site to get the files
        :param destination: path to download file to
        :return:
        """
        with self.session as s:
            file_urls = self.get_links_from_site(html, "https://studip.uni-trier.de/sendfile.php(.*)")
            if not os.path.exists(destination):  # checks if the folder already exists
                self.logger.debug(f"Created a new folder: {destination}")
                os.makedirs(destination)  # creates destination folder
            for file_url in file_urls:
                self.logger.debug(f"File: {file_url}")
                file_head = s.head(file_url)
                file_name = self.get_name_from_head(file_head)
                if self.should_file_be_downloaded(file_head, destination):
                    download_path = destination + os.path.sep + file_name
                    self.download_queue.put([file_url, download_path])
            return

    def main(self):
        self.login_into_studip()
        modules = self.get_all_modules_from_landing_page()
        process_list = list()
        for module in modules:
            self.logger.debug("Created a new module_process")
            self.process_queue.put("New thread")
            module_thread = Process(target=self.traverse_through_module, args=(module,), name="module_process")
            process_list.append(module_thread)
        download_process = Process(target=self.download_files_from_queue, name="download_process")
        # process_list.append(download_process)
        self.logger.debug("Created the download_process")
        [process.start() for process in process_list]
        self.logger.debug("Started all processes")
        [process.join() for process in process_list]
        download_process.start()
        download_process.join()
        self.logger.info("Finished all processes")
        return

def main() -> None:
    sd = StudipDownloader()
    sd.main()


if __name__ == '__main__':
    main()
