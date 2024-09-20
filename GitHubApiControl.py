#Source for the 3 ghapi lines below: https://ghapi.fast.ai/ and https://github.com/fastai/ghapi/blob/master/tutorials/tutorial_actions.ipynb(check)
from ghapi.all import *
from fastcore.all import *
from ghapi.all import GhApi
from FileManager import *
#from RepoCloner import *
#Source for ghauth: https://ghapi.fast.ai/auth.html(check)
#Source for subprocess:https://docs.python.org/3/library/subprocess.html(check)
import subprocess
#Source for os: https://www.freecodecamp.org/news/how-to-check-if-a-file-exists-in-python/(check)
import os
#Source for re:https://docs.python.org/3/library/re.html(check)
import re
# Source for use of requests:  https://github.com/pedrojunqueira/PytalistaYT/blob/master/Python/requests/download_files.py(check)
import requests
#Source regarding git lib:https://www.devdungeon.com/content/working-git-repositories-python(check)
import git
#Source for json dump operation: https://www.geeksforgeeks.org/json-dumps-in-python/(check)
import json
#Sources for os operations:https://www.freecodecamp.org/news/how-to-check-if-a-file-exists-in-python/, https://www.geeksforgeeks.org/python-os-path-join-method/,https://www.geeksforgeeks.org/python-os-makedirs-method/, https://www.w3schools.com/python/ref_os_getcwd.asp(check)
cwd = os.getcwd()
#check existence of a file containing a token and save the latter for REST API auth
Token = ''
file_path = os.path.join(cwd, 'token'  + ".txt")
if os.path.exists(file_path):
 token_file = open(file_path, 'r')
 Token = token_file.read()

api = GhApi(token= Token)
#ghauth = GhDeviceAuth()
#Source for file modding operations:https://www.w3schools.com/python/python_file_handling.asp(check)

#ANNOTATION: Code parts having no page as sources are either generated by ChatGPT or made by the developer

def isDoublequotesCountUneven(string):
    return  string.count('\"') % 2 == 1


def isBackslashLastChar(string):
    return  string[-1] == '\\'


def isLinebreakWrong(string):
    return  isBackslashLastChar(string) and  isDoublequotesCountUneven(string)

#Source leading to the authentication of Github API requests:https://docs.github.com/en/rest/authentication/authenticating-to-the-rest-api?apiVersion=2022-11-28
def prepareFileCommitsOutput(owner,repoName,commitHash):
 """Prepares the download of all CVE-relevant data (commit changes, all pre- and post-patch files) for comparing the pre- and post-patch states to track the patches' applications

    Args:
       owner(string): name of a Git repo owner
       repoName(string): name of a Git repo
       commitHash(string): Commit title containing the hash and the summary of changes
        

    Returns:
        [dyn_download_url_prefix ,dyn_output,dyn_commit_groups,dyn_commit_groups_box, dyn_commit_info, dyn_prev_commit_hash, dyn_commit_url](list): contains file download URL prefix by commit, all LOC changes for all files of a commit, the current and previous commit hash each
 """

 dyn_commit_info =  api.git.get_commit(owner=owner, repo=repoName, commit_sha=commitHash, token=Token);
 dyn_commit_url = dyn_commit_info['html_url']
 dyn_prev_commit_hash = (dyn_commit_info['parents'][0]['html_url']).rsplit('/')[-1]
 # raw.githubusercontent.com URLs contain the actual raw file contents
 dyn_download_url_prefix = 'https://raw.githubusercontent.com/'+ owner+'/'+repoName + '/' + commitHash
 dyn_commit_area_prefix = 'https://github.com/'+ owner +  '/'+ repoName +'/commit/'+ commitHash +'.diff'
 # the command outputs all commit data, albeit unordered
 # the token authenticates the requests so their amount is 5000, otherwise it'd be 50, the more code lines are recognized, the more requests will be needed, if you have none left, their amount will be reseted to 5000 after a certain time
 dyn_command = 'cmd /k  curl -H "Accept: application/vnd.github.diff."  -H "Authorization: token '+ Token + '"  https://api.github.com/repos/'+ owner+'/'+repoName + '/commits/' + commitHash
 dyn_output = str(subprocess.check_output(dyn_command, shell=True)).split('\\n')
#groups commit changes by file
 #dyn_commit_groups = str(subprocess.check_output(dyn_command, shell=True)).split('@@ -')
 dyn_commit_groups = str(subprocess.check_output(dyn_command, shell=True)).split('--git')
 # this list has commit changes of each file appended as one group-like element, which are orderly saved via the for loop
 dyn_commit_groups_box = []
 for group in dyn_commit_groups:
  dyn_commit_groups_box.append(group.split('\\n')[4:])

 return [dyn_download_url_prefix ,dyn_output,dyn_commit_groups,dyn_commit_groups_box, dyn_commit_info, dyn_prev_commit_hash, dyn_commit_url, dyn_commit_area_prefix]

 #How to get to the commit hashes, here is an example: https://api.github.com/repos/ImageMagick/ImageMagick/git/commits/67b871032183a29d3ca0553db6ce1ae80fddb9aa
def getCommitFilesViaUrl(owner,repoName,commitHash):
    """Lists all files changed during a commit, file names have --- or +++ before them and they get fished out

    Args:
       owner(string): name of a Git repo owner
       repoName(string): name of a Git repo
       commitHash(string): Commit title containing the hash and the summary of changes
        

    Returns:
        commit_files: list of files from a commit
    """
    stdOutput = prepareFileCommitsOutput(owner,repoName,commitHash)[1]
    
    fileMark = '---' or '+++'
    commit_copy = [file for file in stdOutput if fileMark in file]
    commit_files = []
    for file in commit_copy:
        if '---' in file or '+++' in file: 
            file = file.replace('---','') or file.replace('+++','')
            file = file.replace('a/','').replace(' ','') or file.replace('b/','').replace(' ','')
            commit_files.append(file)
      
    return commit_files
    

# looks for a char in a string
def contains_charOnline(array, char):
    for string in array:
        if char in string:
            return True
    return False
#returns a char's index in a string
def index_of_element_with_charOnline(array, char):
    return next((index for index, string in enumerate(array) if char in string), -1)

    

def showFileOnline(owner,repoName,commitHash,filePath):
     """extracts file's entire content from web and returns it

    Args:
       owner(string): name of a Git repo owner
       repoName(string): name of a Git repo
       commitHash(string): Commit title containing the hash and the summary of changes
       filePath(string): dir of file which beforehand must exist

    Returns:
        data(string): file content as string
     """
     file_show_url = prepareFileCommitsOutput(owner,repoName,commitHash)[0] + '/' + filePath
     #file_url = 'https://raw.githubusercontent.com/finxter/FinxterTutorials/main/nlights.txt'
     response = requests.get(file_show_url)
     data = response.text
     return data
#    for line in enumerate(data.split('\n')):
#        print(line)

def showCommitAreaOnline(owner,repoName,commitHash,filePath):
     """extracts file's entire content and returns it

    Args:
       owner(string): name of a Git repo owner
       repoName(string): name of a Git repo
       commitHash(string): Commit title containing the hash and the summary of changes
       filePath(string): dir of file which beforehand must exist

    Returns:
        data(string): file content as string
     """
     commit_area_url = prepareFileCommitsOutput(owner,repoName,commitHash)[7]
     #file_url = 'https://raw.githubusercontent.com/finxter/FinxterTutorials/main/nlights.txt'
     response = requests.get(commit_area_url)
     commit_area_data = response.text.split('diff -')
     commit_file_area_data = ''
     for target_area in commit_area_data:
         if filePath in target_area:
             commit_file_area_data = 'diff -' + target_area

     deletionArray = []
     insertionArray = []
     
     #deleted lines are marked with -, new ones with + and are saved correspondingly
     for line in commit_file_area_data.split('\n'):
          if len(line) == 0 or len(line) == 1:
                continue

          if('@@' in line and '\"' not in line):
              deletionArray.append(line)
              insertionArray.append(line)  
          
          elif (line[0] == '-'):
                deletionArray.append(line)
          elif (line[0] == '+') :
                insertionArray.append(line)
                
     deletionString = ('\n').join(deletionArray)
     insertionString = ('\n').join(insertionArray)
     
     return [commit_file_area_data,deletionString , insertionString]



def downloadURLOnline(owner,repoName,commitHash,filePath):
    """ builds download URL for file by commit

    Args:
       owner(string): name of a Git repo owner
       repoName(string): name of a Git repo
       commitHash(string): Commit title containing the hash and the summary of changes
        

    Returns:
         file_show_url: file download URL by commit
    """
    file_show_url = prepareFileCommitsOutput(owner,repoName,commitHash)[0] + '/' + filePath
    return file_show_url
  

def getCommitLOCsOnline(owner,repoName,commitHash, oneFileOnly = False, targetFileName = ''):
  """ stores all commit LOC changes

    Args:
       owner(string): name of a Git repo owner
       repoName(string): name of a Git repo
       commitHash(string): Commit title containing the hash and the summary of changes
       oneFileOnly(boolean): True if only 1 file get scanned for commit changes, False otherwise
       targetFileName(string): name of only file to be searched, which only happens if oneFileOnly is True

    Returns:
        [commitChangeLocsDict,commitDeletionsLocsDict,commitInsertionsLocsDict](list): Dictionaries, one with insertions, one with deletions, one with both
  """
  
  commit_files =  getCommitFilesViaUrl(owner,repoName,commitHash)
  commit_groups_box = prepareFileCommitsOutput(owner,repoName,commitHash)[3]
  commitChangeLocsDict = {}
  commitDeletionsLocsDict = {}
  commitInsertionsLocsDict = {}
  commitChangesLocsList = []
  groupFileIndex = 0
  fileName = None
  commitChangeLocsPack = []
  #for group in commit_groups_box[1:]:
  for file in commit_files:
      groupFileIndex = groupFileIndex + 1
      group = commit_groups_box[groupFileIndex]
      # indexes of deleted/inserted lines
      #print('group', group) 
      startIndexArr = (re.findall(r'[+-]?\d*\.?\d+', group[0]))
      if(len (startIndexArr) <= 0):
          continue
      #print('sta', startIndexArr, startIndexArr[0][1:])
      deleteLocNumber =   int( startIndexArr[0][1:])
      insertIndex = index_of_element_with_charOnline( startIndexArr , '+')
      insertLocNumber = int(startIndexArr[insertIndex])
      deleteArray = []
      insertArray = []
      # save all deleted LOCs
      for i in range(len(group)):
          deleteNums = re.findall(r'[+-]?\d*\.?\d+', group[i])
          #print('dn', deleteNums)
          #finds non-inserted lines
          if(group[i][0] != '+'):
          ##finds non-deleted lines
           deleteLocNumber = int(deleteNums[0][1:]) if (contains_charOnline(deleteNums, '+') and '@@ ' in group[i]) else deleteLocNumber + 1
          if(group[i][0] == '-'):
           currentString = ( group[i] + 'n' + group[i+1] )if( isLinebreakWrong(group[i]) ) else  group[i]
           deleteArray.append([deleteLocNumber - 1 ,currentString])
          if  isLinebreakWrong(group[i]):
              deleteLocNumber  = deleteLocNumber - 1
           #if isLinebreakWrong(group[i]):
            #   i = i + 1
           #deleteArray.append([deleteLocNumber - 1,group[i]])
              
      # save all inserted LOCs
      for j in range(len(group)):
          insertNums = re.findall(r'[+-]?\d*\.?\d+', group[j])
          #if (j >= 0 and oneFileOnly == False ) and (group[j][0] == '+' or contains_charOnline(insertNums, '+')) or (j >= 0 and oneFileOnly ==  ( targetFileName in commit_files ) and group[j][0] == '+'):
          insertIndex = index_of_element_with_charOnline(insertNums, '+')
          if(group[j][0] != '-'):
           insertLocNumber  = int(insertNums[insertIndex]) if (contains_charOnline(insertNums, '+') and '@@ ' in group[j]) else insertLocNumber + 1
           #print('j',j, 'in', deleteNums, 'dln',insertLocNumber, group[j])
          if(group[j][0] == '+'):
           currentString =  (group[j] + 'n' + group[j+1]) if ( isLinebreakWrong(group[j]) ) else  group[j]
           insertArray.append([insertLocNumber - 1 , currentString])
          if  isLinebreakWrong(group[j]):
              insertLocNumber  = insertLocNumber - 1
           #if isLinebreakWrong(group[j]):
            #   j = j + 1
           #insertArray.append([insertLocNumber - 1 ,group[j]])
           

      commitChangeLocsDict[file] = ([{'deletedLines':deleteArray,'insertedLines':insertArray}])
      commitDeletionsLocsDict[file] = ([deleteArray])
      commitInsertionsLocsDict[file] = ([insertArray])
      
  return [commitChangeLocsDict,commitDeletionsLocsDict,commitInsertionsLocsDict]


def makeOrIdCVEFolderOnline(cveID):
    """Creates a CVE root folder if it doesn't exist.

    Args:
        cveID(string): an ID number for a CVE, which is included in the CVE's root folder

    Returns:
        None
    """
    cvePath = cwd + "\\" + 'CVEs' + "\\" + cveID
    if not os.path.isdir(cvePath):
     os.mkdir(cvePath)

def makeOrTakePreFolderOnline(cveID):
    """Creates a pre-patch folder to store versions  of a commit's files before their patches.

    Args:
        cveID(string): an ID number for a CVE, which is included in the CVE's root folder

    Returns:
        preFolderDir: Pre-patch folder' directory
    """
    preFolderDir = cwd + "\\" + 'CVEs'  + "\\"  +  cveID + "\\" + "pre-patch-files"
    if not os.path.isdir(preFolderDir):
     os.mkdir(preFolderDir)

    if os.path.isdir(preFolderDir):
     return preFolderDir

def makeOrTakePostFolderOnline(cveID):
    """Creates a pre-patch folder to store versions  of a commit's files after their patches.

    Args:
        cveID(string): an ID number for a CVE, which is included in the CVE's root folder

    Returns:
        postFolderDir: Post-patch folder's directory
    """
    postFolderDir =  cwd +  "\\" + 'CVEs' +  "\\" +  cveID + "\\" + "post-patch-files"
    if not os.path.isdir(postFolderDir):
     os.mkdir(postFolderDir)

    if os.path.isdir(postFolderDir):
     return postFolderDir




def buildJSONDataOnline(cveID,bugDescInput,patchDescInput, changedLinesData):
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


def createOrModCveJSONOnline(cveID, data):
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



        
                          
def finalDownloadOnline(cveID, ownerName,repoName,commitString, fileArrCommitString, bugDescInput,patchDescInput, usePostFolder = False):
   """Download all files from a selected commit

    Args:
        cveID(string): an ID number for a CVE, which is included in the CVE's root folder
        owner(string): name of a Git repo owner
        repoName(string): name of a Git repo
        commitString(string): Commit title containing the hash and the summary of changes
        fileArrCommitHash(string): Commit title containing the hash and the summary of changes, is the current one that gives away the correct list of commit files, no list for the previous one's files
        bugDescInput(string): describes bugs
        patchDescInput(string): describes patches
        uaePostFolder(boolean): download the files in post-patches folder if true, pre-patch folder otherwise

    Returns:
       None
   """
   if re.match(r'\d+-\d+', cveID):
    makeOrIdCVEFolderOnline(cveID)
    makeOrTakePreFolderOnline(cveID)
    makeOrTakePostFolderOnline(cveID)
    
    prevCommitString = prepareFileCommitsOutput(ownerName, repoName, commitString)[5]
    # commit hash, be it previous or current, helps catch die LOC changes
    commitHash = commitString.split(" ", 1)[0] if usePostFolder == True else prevCommitString.split(" ", 1)[0]
    # this commit hash is the current one that gives away the correct list of commit files, no list for the previous one's files
    #hash at start of commit title,lies before 1st space and gets fetched
    fileArrCommitHash =  fileArrCommitString.split(" ", 1)[0]
    cveFolderDir = makeOrIdCVEFolderOnline(cveID)
    preFolderDir = makeOrTakePreFolderOnline(cveID)
    postFolderDir = makeOrTakePostFolderOnline(cveID)
    targetDir = postFolderDir if usePostFolder == True else preFolderDir
    fileArray = getCommitFilesViaUrl(ownerName,repoName, fileArrCommitHash)
    # for loop has commit files download in the respected folder(pre-/post-patch) dependent on version
    
    #save all LOC changes in a JSON
    if(usePostFolder):
      commitLineChangesData = getCommitLOCsOnline(ownerName,repoName, fileArrCommitHash)[0]
      commitJsonData = buildJSONDataOnline(cveID,bugDescInput,patchDescInput,commitLineChangesData)
      createOrModCveJSONOnline(cveID, commitJsonData)
    for file in fileArray:
         fileURL = downloadURLOnline(ownerName,repoName,commitHash,file)
         fileName = fileURL.rsplit('/')[-1]
         req = requests.get(fileURL, allow_redirects=True)
         open( targetDir + '\\' + fileName, 'wb').write(req.content)
        
   else:
        print('CVE ID not valid, only digits with a hyphen between them accepted')


