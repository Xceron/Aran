from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import os, sys, zipfile, shutil, time, platform

def slash():
    if platform.system() == "Windows":
        return "\\"
    else:
        return "//"

def obtainFiles():
    if platform.system() == "Windows":
        browser = webdriver.Firefox(options=options, executable_path=geckoDriverPath)
    else:
        browser = webdriver.Firefox(options=options)
    browser.get("https://studip.uni-trier.de/dispatch.php/start")

    # Login

    userNameField = browser.find_element_by_id("loginname")
    userNameField.send_keys(username)
    passwordField = browser.find_element_by_id("password")
    passwordField.send_keys(password)
    loginField = browser.find_element_by_name("Login")
    loginField.click()
    moduleLinks = []
    folders = []
    browser.get("https://studip.uni-trier.de/dispatch.php/my_courses")

    for modules in browser.find_elements_by_tag_name("a"):
        moduleLinks.append(modules.get_attribute("href")) #get all modules

    for i in range(len(moduleLinks)-1):
        try:
            if "%2Fcourse%2Ffiles" in moduleLinks[i]:
                folders.append(moduleLinks[i])
        except TypeError:
            pass

    moduleLinks = []
    for j in range(len(folders)):
        if folders[j] == folders[j-1]:
            moduleLinks.append(folders[j])

    for link in moduleLinks:
            browser.get(link)
            checkBox = browser.find_element_by_id("all_files_checkbox")
            checkBox.click()
            download = browser.find_element_by_name("download")
            download.click()
            newName = browser.find_element_by_id("current_page_title").text
            for zipFolder in os.listdir(downloadFolder):
                if zipFolder == "Allgemeiner_Dateiordner.zip":
                    name = newName
                    name = name.replace(":","")
                    name = name.replace("Vorlesung", "")
                    name = name.replace("Übung", "")
                    name = name.replace("Dateien", "")
                    name = name.replace(" -", "")
                    os.rename(downloadFolder + slash() + zipFolder, downloadFolder + slash() + name[1:-1]+".zip")
                else:
                    name = zipFolder
                    name = name.replace(":","")
                    name = name.replace("Vorlesung", "")
                    name = name.replace("Übung", "")
                    name = name.replace("Dateien", "")
                    name = name.replace(" -", "")
                    name = name.replace("_", "")
                    os.rename(downloadFolder + slash() + zipFolder, downloadFolder + slash() + name)

    browser.quit()

## Comparision temp <-> final folder ##
def extractionToTarget():
    for zips in os.listdir(downloadFolder): #creating folder with matching names in targetFolder
        if not os.path.exists(targetFolder + slash() + zips[0:-4]):
            os.makedirs(targetFolder + slash() + zips[:-4])

    for zips in os.listdir(downloadFolder): #list all folders (.zip) in downloadFolder
        archive = zipfile.ZipFile(os.path.realpath(downloadFolder+slash()+zips)) #create a zipfile.ZipFile object for every zip to work with
        for folder in os.listdir(targetFolder): #get all folders in the target destination
            if zips[:-4] == folder: #name matching from folder and corresponding zip
                for info in archive.infolist(): #retrieving name and size
                    zipFileName = info.filename
                    if zipFileName != "archive_filelist.csv":
                        archive.extract(zipFileName, targetFolder + slash() + folder)
                    elif not "Allgemeiner Dateiordner" in zipFileName and zipFileName != "archive_filelist.csv":
                        archive.extract(zipFileName, targetFolder + slash() + folder + slash() +"Allgemeiner Dateiordner")


def checkDuplicates(tempPath, rootPath):
    """
    :param tempPath: path to file to check in temporary folder
    :param rootPath:  path to file to check in final folder
    deletes smaller file and moves the bigger one to the final folder
    """
    if os.path.exists(rootPath): #duplicate files
        if os.path.isfile(rootPath): #handling files
            if os.path.getsize(tempPath) > os.path.getsize(rootPath):
                print("Found newer version of file, moving: " + os.path.basename(rootPath))
                os.remove(rootPath)
                os.rename(tempPath, rootPath)
            else: #existing file >= file in zipped dir
                print("Deleting zipped file: " + os.path.basename(tempPath))
                os.remove(tempPath)
        else: #zipped file is new
            print("Moving new file: " + os.path.basename(rootPath))
            os.rename(tempPath, rootPath)

def checkFolder(tempPath, rootPath):
    """
    :param tempPath: path to folder to check in temporary folder
    :param rootPath:  path to folder to check in final folder
    recursively checks folders and calls checkDuplicate()
    """
    if os.path.isdir(rootPath):
        for subcontent in os.listdir(rootPath):
            if os.path.isdir(rootPath + slash() + subcontent):
                checkFolder(tempPath + slash() + subcontent, rootPath + slash() + subcontent)
            else:
                checkDuplicates(tempPath + slash() + subcontent, rootPath + slash() + subcontent)


def fileMatching():
    for subfolders in os.listdir(targetFolder):
        try:
            if os.path.exists(targetFolder + slash() + subfolders + slash() + "Allgemeiner Dateiordner"):
                for subfiles in os.listdir(targetFolder + slash() + subfolders + slash() +"Allgemeiner Dateiordner"):
                    if os.path.exists(targetFolder + slash() + subfolders + slash() + subfiles): #duplicate files
                        if os.path.isfile(targetFolder + slash() + subfolders + slash() + subfiles):
                            checkDuplicates(targetFolder + slash() + subfolders + slash() + "Allgemeiner Dateiordner" + slash() + subfiles,targetFolder + slash() + subfolders + slash() + subfiles)
                    elif os.path.isdir(targetFolder + slash() + subfolders + slash() + subfiles):
                        checkFolder(targetFolder + slash() + subfolders + slash() + "Allgemeiner Dateiordner" + slash() + subfiles, targetFolder + slash() + subfolders + slash() + subfiles)
                    else:
                        os.rename(targetFolder + slash() + subfolders + slash() + "Allgemeiner Dateiordner" + slash() + subfiles, targetFolder + slash() + subfolders + slash() + subfiles)
                        print("Created new file: " + subfiles)
                        pass
                shutil.rmtree(targetFolder + slash() + subfolders + slash() + "Allgemeiner Dateiordner")
        except FileNotFoundError:
            pass

    time.sleep(10)
    for temp in os.listdir(downloadFolder):
        os.rename(downloadFolder + slash() + temp)

if __name__ == "__main__":
    ### SETUP ###
    # Only change this part of the file!
    downloadFolder = r"Path\To\Folder" #path to a temporary folder, storing the zips for a limited time
    targetFolder = r"Path\To\Folder" #path to your downloaded files
    if platform.system() == "Windows":
        geckoDriverPath = r"Path\To\Folder" #path to geckodriver ON WINDOWS SYSTEMS ONLY
    username = "USERNAME" #your user name for studip
    password = "PASSWORD" #your password for studip

    # Setup Webdriver
    options = Options()
    options.set_preference("browser.download.folderList",2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir","/data")
    options.set_preference("browser.download.dir", downloadFolder)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/zip")
    options.headless = True

    for temp in os.listdir(downloadFolder):
        os.remove(downloadFolder + slash() + temp)
    obtainFiles()
    extractionToTarget()
    fileMatching()
    sys.exit()
