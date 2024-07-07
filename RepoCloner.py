import git
import os
import shutil
import subprocess
import re
import requests
from FileManager import *
from GitHubApiControl import *
from tkinter import filedialog, messagebox, ttk
# URL of the Git repository
#repo_url = 'https://github.com/vim/vim.git'
reposCommitsList = []
lAlt = []
cvesList = []
#current working directory, root dir of this file
cwd = os.getcwd()
allfiles = os.listdir(cwd)

#repo = git.Repo('ImageMagick')
#repo.git.checkout('main')
#repo.git.pull()

def restart_program():
    python = sys.executable
    os.execl(python, python, *sys.argv)


    
def restart_click():
    restart_program()

# this class updates the currently selected repos for examination of them as well as of commits
class RepoUpdater:
     def __init__ (self):
          self.repo = None

     def cloneRepo(self,repoURL, repoName):
       """sets new repo

    Args:
       self: class instance
       repoName(string): name of repo

    Returns:
    None
       """
       git.Repo.clone_from(repoURL, repoName)
       self.repo = git.Repo(repoName)
       restart_click()
       
     def setRepo(self,repoName):
      """sets new repo

    Args:
       self: class instance
       repoName(string): name of repo

    Returns:
    None
      """
      self.repo = git.Repo(repoName)
      #print('sr choose', self.repo, type(git.Repo(repoName)) )

     def getRepo(self):
      """returns current repo

    Args:
       self: class instance

    Returns:
    self.repo = current repo
      """
      return self.repo
          
     def pullRepo(self):
      """pulls latest updates from current repo

    Args:
       self: class instance

    Returns:
    None
      """
      self.repo = self.getRepo()
      #print('sr pull', self.repo, type(self.repo) )
      self.repo.git.checkout('main')
      self.repo.git.pull()


repoUpdater = RepoUpdater()

def listCurrentRepoHistory(repoName):
     """Lists commits history of a repo

    Args:
       repoName(string): name of repo

    Returns:
    commitList(list): commit history of repo
    """
     gitRepoHistory = git.Repo(repoName).git.log('--oneline')
     commitList = None
     commitList = gitRepoHistory.split("\n")
     return commitList     

def get_value_by_key(array, search_key): #CGPT
    """Lists commits in a combobox

    Args:
       array(list): Array with kv pairs
       search_key(string): key to search array for

    Returns:
    dictionary[search_key](string): Key-value-dict if a values´'s found via key, None otherwise
    """
    for dictionary in array:
        if search_key in dictionary:
            return dictionary[search_key]
    return None  # Key not found in any dictionary



def updateFilesDropdown(combobox, commitString):
    """Lists files in a combobox

    Args:
       combobox(Combobox): files  list combobox
       commitString(string): Commit title containing the hash and the summary of changes

    Returns:
    None
    """
    combobox.set('')
    combobox["values"]= []
    combobox["values"]=showChangedFiles(commitString)
    l2 = combobox["values"]


# List CHANGED FILES
def showChangedFiles(commitString):
     """Show the areas with commit changes

    Args:
       
       commitString(string): Commit title containing the hash and the summary of changes

    Returns:
     changedFilesData(list): changed files of a commit
    """
     commitHash = commitString.split(" ", 1)[0]
     repo = repoUpdater.getRepo()
     changedFilesData = repo.git.show('--name-only', commitHash,'--oneline' ).split('\n')[1:]
     #print('cc', repo.git.show('--name-only', commitHash,'--oneline' ))
     return changedFilesData


def showCommitFile( commitString, filePath, repoName):
    """Show the areas with commit changes

    Args:
       
       commitString(string): Commit title containing the hash and the summary of changes
       filePath(string): path of file that must exist
       repoName(string): name of a Git repo

    Returns:
     commitArea(string): shows in which areas the changes took place
    """
    repo = repoUpdater.getRepo()
    commitHash = commitString.split(" ", 1)[0]
    repo.git.checkout(commitHash)
    absPath = cwd + "\\" +   repoName + '\\'+ filePath.replace('/','\\')
    with open(absPath, 'r') as file:
       content = file.read()
       return content

def showCommitArea(commitString, filePath, repoName):
    """Show the areas with commit changes

    Args:
       
       commitString(string): Commit title containing the hash and the summary of changes
       filePath(string): path of file that must exist
       repoName(string): name of a Git repo

    Returns:
     commitArea(string): shows in which areas the changes took place
    """
    if isValueString(commitString) and isValueString(filePath):
     commitHash = commitString.split(" ", 1)[0]
     absPath = cwd + "\\" +   repoName + '\\'+ filePath.replace('/','\\')
     # gets current repo
     repo = repoUpdater.getRepo()
     commitArea = repo.git.show(commitHash,'--',absPath).split('\n')
     deletionArray = []
     insertionArray = []
     
     for line in commitArea:
          if len(line) == 0 or len(line) == 1:
                continue
          #add deleted lines to deletion array, inserted ones to the insertion array
          if (line[0] == '+' and  line[1] == ' ') == False:
                deletionArray.append(line)
          if (line[0] == '-' and  line[1] == ' ') == False:
                insertionArray.append(line)      
                

     insertionString = ('\n').join(insertionArray)
     deletionString = ('\n').join(deletionArray)
     return [commitArea,deletionString , insertionString]
    else:
     print('Every arg must be a string and must have existing info!')


#shows only the modified lines
#print(repo.git.show('-U0', '67b871032183a29d3ca0553db6ce1ae80fddb9aa'))



def checkoutCommit(commitInfo):
     repo = repoUpdater.getRepo()
     repo.git.checkout(commitInfo.split(" ", 1)[0])
     

def showOnlyChangedLines(commitString,filePath, repoName):
     """Show only the inserted/deleted lines along with LOC indexes

    Args:
       
       commitString(string): Commit title containing the hash and the summary of changes
       filePath(string): path of file that must exist
       repoName(string): name of a Git repo

    Returns:
     commitInfo(list): group of LOC changes per file
     """
     commitHash = commitString.split(" ", 1)[0]
     absPath = cwd + "\\" +   repoName + '\\'+ filePath.replace('/','\\')
     #current repo
     repo = repoUpdater.getRepo()
     # list of elements with LOCs per file
     commitInfo = repo.git.show('-U0', commitHash, absPath).split('@@ -')[1:]
     return commitInfo

def getCommitLOCsOffline(commitString, repoName, oneFileOnly = False, targetFileName = ''):
  """Download all files from a selected commit

    Args:
       
       commitString(string): Commit title containing the hash and the summary of changes
       repoName(string): name of a Git repo
       oneFileOnly(boolean): True if only 1 file get scanned for commit changes, False otherwise
       targetFileName(string): name of only file to be searched, which only happens if oneFileOnly is True

    Returns:
     [commitChangeLocsDict,commitDeletionsLocsDict,commitInsertionsLocsDict](list): Dictionaries, one with insertions, one with deletions, one with both
  """
  commit_files = showChangedFiles(commitString)
  commitChangeLocsDict = {}
  commitDeletionsLocsDict = {}
  commitInsertionsLocsDict = {}
  commitChangesLocsList = []
  fileName = None
  commitChangeLocsPack = []
  for file in commit_files:
      arrayGroup = showOnlyChangedLines(commitString,file, repoName)
      group = ''.join(arrayGroup).split('\n')
      # indexes of deleted/inserted lines
      startIndexArr = (re.findall(r'[+-]?\d*\.?\d+', group[0]))
      deleteLocNumber = int(startIndexArr[0])
      insertIndex = index_of_element_with_char( startIndexArr , '+')
      insertLocNumber = int(startIndexArr[insertIndex])
      deleteArray = []
      insertArray = []
      # save all deleted LOCs
      for i in range(len(group)):
          deleteNums = re.findall(r'[+-]?\d*\.?\d+', group[i])
          if (i >= 0 and oneFileOnly == False ) and (group[i][0] == '-' or contains_char(deleteNums, '+')) or (i >= 0 and oneFileOnly ==  ( targetFileName in commit_files ) and group[i][0] == '-'):
              deleteLocNumber = int(deleteNums[0]) if contains_char(deleteNums, '+') else  deleteLocNumber + 1
              if(group[i][0] == '-'):
               deleteArray.append([deleteLocNumber - 1,group[i]])
              
      # save all inserted LOCs
      for j in range(len(group)):
          insertNums = re.findall(r'[+-]?\d*\.?\d+', group[j])
          if (j >= 0 and oneFileOnly == False ) and (group[j][0] == '+' or contains_char(insertNums, '+')) or (j >= 0 and oneFileOnly ==  ( targetFileName in commit_files ) and group[j][0] == '+'):
               insertIndex = index_of_element_with_char(insertNums, '+')                                
               insertLocNumber  = int(insertNums[insertIndex]) if contains_char(insertNums, '+') else insertLocNumber + 1
               if(group[j][0] == '+'):
                insertArray.append([insertLocNumber - 1 ,group[j]])

      commitChangeLocsDict[file] = ([{'deletedLines':deleteArray,'insertedLines':insertArray}])
      commitDeletionsLocsDict[file] = ([deleteArray])
      commitInsertionsLocsDict[file] = ([insertArray])

  return [commitChangeLocsDict,commitDeletionsLocsDict,commitInsertionsLocsDict]





def finalDownloadOffline(cveID, commitString, fileArrCommitString, repoName , bugDescInput, patchDescInput, usePostFolder = False):
    """Download all files from a selected commit

    Args:
        cveID(string): an ID number for a CVE, which is included in the CVE's root folder
        commitString(string): Commit title containing the hash and the summary of changes
        fileArrCommitHash(string): Commit title containing the hash and the summary of changes, is the current one that gives away the correct list of commit files, no list for the previous one's files
        repoName: name of repo
        bugDescInput(string): describes bugs
        patchDescInput(string): describes patches
        uaePostFolder(boolean): download the files in post-patches folder if true, pre-patch folder otherwise

    Returns:
       None
    """
    if re.match(r'\d+-\d+', cveID):
     makeOrIdCVE_Folder(cveID)
     makeOrTakePre_Folder(cveID)
     makeOrTakePost_Folder(cveID)
    
     cveFolderDir = makeOrIdCVE_Folder(cveID)
     preFolderDir = makeOrTakePre_Folder(cveID)
     postFolderDir = makeOrTakePost_Folder(cveID)
     # commit hash, be it previous or current, helps catch die LOC changes
     commitHash = commitString.split(" ", 1)[0]  # if usePostFolder == True else combobox_updater.get_combobox_values()[ combobox_updater.get_commit_indexes()[0]]
    # this commit hash is the current one that gives away the correct list of commit files, no list for the previous one's files
     fileArrCommitHash =  fileArrCommitString.split(" ", 1)[0]
     fileArray = showChangedFiles(fileArrCommitHash )

    # current repo
     repo = repoUpdater.getRepo()
   
     targetDir = postFolderDir if usePostFolder == True else preFolderDir

     repo.git.checkout(commitHash)
    
    #save all LOC changes in a JSON
     if(usePostFolder == True):
      commitLineChangesData = getCommitLOCsOffline(commitHash, repoName)[0]
      commitJsonData = buildJSONData(cveID,bugDescInput,patchDescInput,commitLineChangesData)
      createOrModCveJSON(cveID, commitJsonData)
    # for loop has commit files download in the respected folder(pre-/post-patch) dependent on version
     for file in fileArray:
          copyFileToDir(repoName + '\\' + file.replace('/','\\')  , targetDir)

          
    else:
         print('CVE ID not valid, only digits with a hyphen between them accepted')

    

   
