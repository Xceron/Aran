import tkinter
from tkinter import filedialog
import os
import warnings

# tkinter.Tk().withdraw()
# path = filedialog.askdirectory()
# print(path)
# path = ""
# while not (os.path.exists(path)):
#     x = input()
#     if x == "y":
#         tkinter.Tk().withdraw()
#         path = filedialog.askdirectory()
#     print(path)


data = {
        "username" : "NAME",
        "path" : "",
        "backup_bigger" : "x",
        "backup_smaller" : "x"
    }
positive_answers = ["yes", "y", "ye", "ja", "+", "1"]
negative_answers = ["no", "n", "nein", "-", "0"]

def testPath():

    while not (os.path.exists(data["path"])):
        import sys

        try:
            sys.stdout = open('/dev/null', 'w')
            data["path"] = filedialog.askdirectory()
        finally:
            sys.stdout.close()
            sys.stdout = sys.__stdout__
        # path = input("Enter the path where the files should be saved. If you need help, type \"help\". ")
        # if path == "help":
        #     # tkinter.Tk().withdraw()
        #     data["path"] = filedialog.askdirectory()


print(data["path"])
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    testPath()

print("test")

if not (type(data["backup_bigger"]) == bool):
    backup_big_input = input("Do you want to save the old files, if the new file is bigger? \n"
                             "This can happen if the new file gets expanded [y/n]")
    if backup_big_input in positive_answers:
        data["backup_bigger"] = True
    elif backup_big_input in negative_answers:
        data["backup_bigger"] = False