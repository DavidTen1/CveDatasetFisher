
#Sources for the tkinter import and filedialog: https://www.geeksforgeeks.org/file-explorer-in-python-using-tkinter/
from tkinter import *
from tkinter import filedialog
from GitHubApiControl import *
#Source for os: https://www.freecodecamp.org/news/how-to-check-if-a-file-exists-in-python/(check)
import os
#Source for use of shutil: https://docs.python.org/3/library/shutil.html(check)
import shutil
#Source for use of subprocess: https://docs.python.org/3/library/subprocess.html(check)
import subprocess
#Source for re:https://docs.python.org/3/library/re.html(check)
import re
# Source for use of requests:  https://github.com/pedrojunqueira/PytalistaYT/blob/master/Python/requests/download_files.py(check)
import requests
import json

#Source for file explorer code:https://www.geeksforgeeks.org/file-explorer-in-python-using-tkinter/(check)
#Source for file handling operations:https://www.w3schools.com/python/python_file_handling.asp(check)
#ANNOTATION: Code parts having no page as sources are either generated by ChatGPT or made by the developer


#current working directory
cwd = os.getcwd()

if not os.path.isdir(cwd + '\\' + 'CVEs'):
    os.mkdir(cwd + '\\' + 'CVEs')

# Function for opening the 
# file explorer window
def browseFiles(input): #GFG
    """Browse a file and get its directory.

    Args:
        input (string): file directory in text box.

    Returns:
        None.
    """
    eFilename = filedialog.askopenfilename(initialdir = "/",
                                          title = "Select a File",
                                          filetypes = (("Text files",
                                                        "*.txt*"),
                                                       ("all files",
                                                        "*.*")))
 
#    print("File Opened: "+ eFilename)
    input.insert( 0 , eFilename)


def isURLOnline(value):# Source leading to this code: https://github.com/pedrojunqueira/PytalistaYT/blob/master/Python/requests/download_files.py(check)
    """Check if the URL exists and return code 200 if so.

    Args:
        value(string): A number representing the first addend in the addition.

    Returns:
        requests.get(value).status_code == 200: returns whether or not the HTTP code is 200(the page exists).
    """
    return requests.get(value).status_code == 200

def doesFileExist(value):
    """Check if the file exists and return the bool value.

    Args:
        value(string): target file's directory

    Returns:
       os.path.isfile(value): True, if file exsits, False otherwise.
    """
    #Source for os.path.isfile(value): https://www.freecodecamp.org/news/how-to-check-if-a-file-exists-in-python/(check)
    return os.path.isfile(value)




def makeOrIdCVE_Folder(cveID):
    """Creates a CVE root folder if it doesn't exist.

    Args:
        cveID(string): an ID number for a CVE, which is included in the CVE's root folder

    Returns:
        None
    """
    cvePath = cwd + "\\" + 'CVEs' + "\\" + cveID # Source for os.isdir and os.mkdir:https://www.geeksforgeeks.org/python-os-path-isdir-method/(check)
    if not os.path.isdir(cvePath):
     os.mkdir(cvePath)       
    

def makeOrTakePre_Folder(cveID):
    """Creates a pre-patch folder to store versions  of a commit's files before their patches.

    Args:
        cveID(string): an ID number for a CVE, which is included in the CVE's root folder

    Returns:
        preFolderDir: Pre-patch folder' directory
    """
    preFolderDir = cwd + "\\" + 'CVEs' + "\\"  +  cveID + "\\" + "pre-patch-files"
    if not os.path.isdir(preFolderDir):
     os.mkdir(preFolderDir)

    if os.path.isdir(preFolderDir):
     return preFolderDir

def makeOrTakePost_Folder(cveID):
    """Creates a post-patch folder to store versions  of a commit's files after their patches.

    Args:
        cveID(string): an ID number for a CVE, which is included in the CVE's root folder

    Returns:
        postFolderDir: Post-patch folder's directory
    """
    postFolderDir =  cwd + "\\" + 'CVEs' + "\\" + cveID + "\\" + "post-patch-files"
    if not os.path.isdir(postFolderDir):
     os.mkdir(postFolderDir)

    if os.path.isdir(postFolderDir):
     return postFolderDir

def copyFileToDir(fileDir, targetDir):
    """Copies file in a targeted directory via a lib named shutil which must exist before though

    Args:
        fileDir(string): Directory of file which must exist beforehand though in order  to be copied
        targetDir(string): Directory   which must exist beforehand though in order  to receive the copied file
    Returns:
        None
    """
    #Source for shutil.copy: https://docs.python.org/3/library/shutil.html#shutil.copy
    shutil.copy(fileDir, targetDir)


def buildJSONData(cveID,bugDescInput,patchDescInput, changedLinesData):
    """Copies file in a targeted directory via a lib named shutil which must exist before though

    Args:
        cveID(string): an ID number for a CVE, which is included in the CVE's root folder
        bugDescInput(string): describes bugs
        patchDescInput(string): describes patches
        changedLinesData(object): LOC changes and commit data

    Returns:
        cveJSONData: registers all inserted, modified or deleted lines in given codes, along with CVE ID and descriptions of bugs as well as of patches.
    """
    cveJSONData = {
     'CVE-ID': cveID,
     'Bug description': bugDescInput,
     'Patch description': patchDescInput,
     'File changes': changedLinesData
     }
    return cveJSONData

def createOrModCveJSON(cveID, data):
    """Creates file with all commit info (LOC changes by file)

    Args:
        cveID(string): an ID number for a CVE, which is included in the CVE's root folder
        data(object): LOC changes and commit data

    Returns:
        None
    """
    directory = cwd + "\\" + 'CVEs' + "\\" + cveID
    try:
        if not os.path.exists(directory):
         os.makedirs(directory)

        file_path = os.path.join(directory, cveID + ".json")
        fileStat = "w" if os.path.exists(file_path) else "x"
        with open(file_path, fileStat) as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        #if not os.path.exists(directory):
        #    os.makedirs(directory)
        
        #file_path = os.path.join(directory, cveID + ".json")
        #if not os.path.exists(file_path):
        # with open(file_path, "x") as file:
        #    json.dump(data, file, ensure_ascii=False, indent=4)
        #if  os.path.exists(file_path):
        # with open(file_path, "w") as file:
        #    json.dump(data, file, ensure_ascii=False, indent=4)    
    except Exception as e:
        print(f"Error: {e}")



#Source: ChatGPT
def contains_char(array, char):
    for string in array:
        if char in string:
            return True
    return False

#Source: ChatGPT
def index_of_element_with_char(array, char):
    return next((index for index, string in enumerate(array) if char in string), -1)

