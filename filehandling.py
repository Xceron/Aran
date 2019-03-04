# coding: utf8
import os
import shutil
import platform
import config_handling
import datetime


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
    for sign in ["Vorlesung", "Übung", "Tutorium", " - Dateien", ": "]:
        old_name = old_name.replace(sign, "")
    return old_name


def cleanup(path):
    """
    :return: deletes duplicates and removes useless files
    """
    sl = slash()
    for folder in os.listdir(path):
        if folder == ".DS_Store":
            os.remove(path + sl + folder)
        else:
            for subfolder in os.listdir(path + sl + folder):
                path_sb = path + sl + folder + sl
                if subfolder == ".DS_Store":
                    os.remove(path_sb + ".DS_STORE")
                if subfolder == "PLACEHOLDER_TO_DELETE":
                    os.remove(path_sb + "PLACEHOLDER_TO_DELETE")
                if subfolder == "archive_filelist.csv":
                    os.remove(path_sb + "archive_filelist.csv")
                if subfolder == "Allgemeiner Dateiordner":
                    for files in os.listdir(path_sb + sl + "Allgemeiner Dateiordner"):
                        path_ad = path_sb + "Allgemeiner Dateiordner" + sl + files
                        if os.path.isdir(path_ad):
                            check_folder(path_ad, path_sb + files)
                        elif os.path.isfile(path_ad):
                            check_duplicates(path_ad, path_sb + files)
                        else:
                            pass
                    shutil.rmtree(path_sb + "Allgemeiner Dateiordner")
    os.remove(os.path.expanduser("~/Documents/cookies"))


def get_today():
    """
    :return: current date
    """
    return datetime.datetime.now().strftime("%Y-%m-%d")


def check_duplicates(src_path, dst_path):
    """
    :param src_path: path to file to check in temporary folder
    :param dst_path:  path to file to check in final folder
    :return: deletes smaller file and moves the bigger one to the final folder
    """
    sl = slash()
    if os.path.exists(dst_path):  # duplicate files
        if os.path.isfile(dst_path):  # handling files
            if os.path.getsize(src_path) > os.path.getsize(dst_path):
                if config_handling.get_value("backup_bigger"):  # Backup of old file if new file is bigger
                    print("Found newer version of file. Backed up and moved: " + os.path.basename(dst_path))
                    folder_name = os.path.dirname(dst_path).replace("\\ ", " ")
                    if not os.path.exists(folder_name + sl + "Backups"):
                        os.makedirs(folder_name + sl + "Backups")
                    filename_with_date = os.path.basename(dst_path) + get_today()
                    os.rename(dst_path, folder_name + sl + "Backups" + sl + filename_with_date)
                    os.rename(src_path, dst_path)
                else:
                    print("Found newer version of file, moving: " + os.path.basename(dst_path))
                    os.remove(dst_path)
                    os.rename(src_path, dst_path)
            elif os.path.getsize(src_path) < os.path.getsize(dst_path):  # existing file > file in downloaded dir
                if config_handling.get_value("backup_smaller"):
                    print("Downloaded file is smaller. Backed up and moved: " + os.path.basename(dst_path))
                    folder_name_smaller = os.path.dirname(dst_path).replace("\\ ", " ")
                    if not os.path.exists(folder_name_smaller + sl + "Backups"):
                        os.makedirs(folder_name_smaller + sl + "Backups")
                    filename_with_date = os.path.basename(dst_path) + get_today()
                    os.rename(dst_path, folder_name_smaller + sl + "Backups" + sl + filename_with_date)
                    os.rename(src_path, dst_path)
                else:
                    print("Deleting downloaded file: " + os.path.basename(src_path))
                    os.remove(src_path)
            else:
                print("Deleting downloaded file: " + os.path.basename(src_path))
                os.remove(src_path)
    else:  # downloaded file is new
        print("Moving new file: " + os.path.basename(dst_path))
        os.rename(src_path, dst_path)


def check_folder(src_path, dst_path):
    """
    :param src_path: path to folder to check in temporary folder
    :param dst_path:  path to folder to check in final folder
    :return: recursively checks folders and calls check_duplicate()
    """
    sl = slash()
    if os.path.exists(dst_path):
        if os.path.isdir(dst_path):
            for subcontent in os.listdir(src_path):
                if os.path.isdir(dst_path + sl + subcontent):
                    check_folder(src_path + sl + subcontent, dst_path + sl + subcontent)
                else:
                    check_duplicates(src_path + sl + subcontent, dst_path + sl + subcontent)
    else:
        os.makedirs(dst_path)
        check_folder(src_path, dst_path)
