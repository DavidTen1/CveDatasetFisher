from tkinter import *
from FileManager import *
from RepoCloner import *
from tkinter import filedialog, messagebox, ttk
from git import *
import os
import subprocess
import json
master = Tk()

style = ttk.Style()
style.configure('Custom.TEntry', readonlybackground='#FFFFFF')# readonly background stays white

#window size
master.geometry("750x350")
master.title('CveDatasetFisher')



class ComboboxUpdater:
    def __init__(self):
        self.combobox_values = ['Option A', 'Option B', 'Option C']
        self.combobox = None
        self.prevCommitIndex = 0
        self.nextCommitIndex = 0
        self.prevCommitHash = None

    def update_values(self, repoName):
        """updates commit list in commit dropdowm

    Args:
       repoName(string): name of a Git repo

    Returns:
        None
        """
        # New values for the combobox
        new_values = get_value_by_key(reposCommitsList, repoName)
        # Clear existing values and set new values
        self.combobox['values'] = new_values
        self.combobox_values = new_values
        
        # Print the new values globally
        #print("New Combobox Values (Global):", self.combobox_values)


    def update_fileValues(self, commitString):
        """updates file list in file dropdowm

    Args:
       repoName(string): name of a Git repo

    Returns:
        None
        """
        # New values for the combobox
        new_values = showChangedFiles(commitString)
        # Clear existing values and set new values
        self.combobox['values'] = new_values
        self.combobox_values = new_values

    def update_onlineFileValues(self, ownerName, repoName ,commitString):
        """updates file list in file dropdowm for ghapi

    Args:
       ownerName(string): name of a repo owner
       repoName(string): name of a Git repo
       commitString(string):commit title with corresponding hash
    Returns:
        None
        """
        # New values for the combobox
        new_values = getCommitFilesViaUrl(ownerName,repoName,commitString)
        
        # Clear existing values and set new values
        self.combobox['values'] = new_values
        self.combobox_values = new_values

    def get_combobox_values(self):
        """updates file list in file dropdowm for ghapi

    Args:
       self: class instance
    Returns:
        self.combobox_values(list): returns current combobox values
        """
        return self.combobox_values

    def set_previous_commitHash(self, ownerName,repoName,commitString):
        """returns previous commit hash for ghapi

    Args:
       ownerName(string): name of a repo owner
       repoName(string): name of a Git repo
       commitString(string):commit title with corresponding hash
    Returns:
         self.prevCommitHash(string) = previous commit hash for ghapi
        """
        self.prevCommitHash = prepareFileCommitsOutput(ownerName,repoName,commitString)[5]

    def get_previous_commitHash(self):
        """gets previous commit hash

    Args:
       self: class instance
    Returns:
        self.prevCommitHash(string): returns current combobox values
        """
        return self.prevCommitHash

    def set_combobox(self, combobox):
        """sets new combobox

    Args:
       combobox(combobox): new combobox
    Returns:
       None
        """
        self.combobox = combobox

    def setNeighboredCommitsIndexes(self, commitTargetValue):
        """gets indexes of previous and current commits each

    Args:
       self: class instance
       commitTargetValue(string): a commit title with hash and short description
    Returns:
        commitIndexData(list): returns indexes of previous and current commits each
        """
        targetArray = self.combobox_values
        for i in range(len(targetArray)):
            
            if commitTargetValue in targetArray[i]:
               
                self.prevCommitIndex = i + 1
                self.nextCommitIndex = i
                break
          
    def get_commit_indexes(self):
        """gets indexes of previous and current commits each

    Args:
       self: class instance
    Returns:
        commitIndexData(list): returns indexes of previous and current commits each
        """
        commitIndexData =[self.prevCommitIndex,self.nextCommitIndex]
        return commitIndexData 


# the updaters each update the file and the commit comboboxes
combobox_updater = ComboboxUpdater()
combobox_updater2 = ComboboxUpdater()

cveDownloadArr = None
cveDownloadsArrFilePath = os.path.join(cwd, "cveDownloadList.json")
if os.path.exists(cveDownloadsArrFilePath):
    with open(cveDownloadsArrFilePath, 'r') as file:
     cveDownloadArr = json.loads(file.read())
    

def addOfflineItem():
        new_item = {"CVE":cveInput.get(),"Commit":commitCombobox.get(),"Commit":commitCombobox.get(),"Repo":repoCombobox.get(),"Bug":bugTextBox.get("1.0","end"),"Patch":patchTextBox.get("1.0","end")}
        if new_item:  # Ensure the entry is not empty
            fileStat = "w" if os.path.exists(cveDownloadsArrFilePath) else "x"
            current_items = list(cveDownloadListCombobox['values'])
            current_items.append(new_item)
            cveDownloadListCombobox['values'] = current_items
            #self.entry.delete(0, tk.END)  # Clear the entry after adding
            with open(cveDownloadsArrFilePath, fileStat) as file:
             json.dump(cveDownloadListCombobox['values'], file, ensure_ascii=False, indent=4)

def addOnlineItem():
        new_item = {"CVE":cveInput.get(),"Owner":ownerOnlineInput.get(),"Repo":repoOnlineInput.get(),"Commit":commitOnlineInput.get(),"Bug":bugTextBox.get("1.0","end"),"Patch":patchTextBox.get("1.0","end")}
        if new_item:  # Ensure the entry is not empty
            fileStat = "w" if os.path.exists(cveDownloadsArrFilePath) else "x"
            current_items = list(cveDownloadListCombobox['values'])
            #print('tt', type(current_items))
            current_items.append(new_item)
            cveDownloadListCombobox['values'] = current_items
            #self.entry.delete(0, tk.END)  # Clear the entry after adding
            with open(cveDownloadsArrFilePath, fileStat) as file:
             json.dump(cveDownloadListCombobox['values'], file, ensure_ascii=False, indent=4)

def removeItem():
        selected_item = cveDownloadListCombobox.get()
        fileStat = "w" if os.path.exists(cveDownloadsArrFilePath) else "x"
        if selected_item:  # Ensure an item is selected
            current_items = list(cveDownloadListCombobox['values'])
            if selected_item in current_items:
                current_items.remove(selected_item)
                cveDownloadListCombobox['values'] = current_items
                cveDownloadListCombobox.set('')  # Clear the selection after removing
                with open(cveDownloadsArrFilePath, fileStat) as file:
                 json.dump(cveDownloadListCombobox['values'], file, ensure_ascii=False, indent=4)


def removeItems():
        selected_item = cveDownloadListCombobox.get()
        fileStat = "w" if os.path.exists(cveDownloadsArrFilePath) else "x"
        current_items = list(cveDownloadListCombobox['values'])
        cveDownloadListCombobox['values'] = []
        cveDownloadListCombobox.set('')  # Clear the selection after removing
        with open(cveDownloadsArrFilePath, fileStat) as file:
         json.dump(cveDownloadListCombobox['values'], file, ensure_ascii=False, indent=4)

                 
#combobox_updater.get_combobox_values()[ combobox_updatr.get_commit_indexes()[0]]

def downloadSavedCves():
    prevCommitHash = ''
    for entry in cveDownloadListCombobox['values']:
         #print('cnty',entry, type(entry))
         jsonEntry = entry.replace("'",'"')
         #print('cnty',jsonEntry, type(jsonEntry))
         parsedEntry = json.loads(jsonEntry)
         #print('cnty ', parsedEntry, type(parsedEntry), 'Owner' not in parsedEntry.keys())
         if 'Owner' not in parsedEntry.keys():
          currentRepo = parsedEntry['Repo']
          currentCommit = parsedEntry['Commit']
          repoUpdater.setRepo(currentRepo)
          currentRepoCommitList = get_value_by_key(reposCommitsList, parsedEntry['Repo'])
          prevValIndex = 0
          currentValIndex = 0
          for i in range(len(currentRepoCommitList)):
             if currentCommit in currentRepoCommitList[i] or currentRepoCommitList[i].split(" ", 1)[0] in currentCommit:
                prevValIndex = i + 1
                currentValIndex = i
                prevCommitHash = currentRepoCommitList[prevValIndex].split(" ", 1)[0]
                break

          finalDownloadOffline(parsedEntry['CVE'], prevCommitHash, parsedEntry['Commit'], parsedEntry['Repo'],parsedEntry['Bug'],parsedEntry['Patch'])
          finalDownloadOffline(parsedEntry['CVE'], parsedEntry['Commit'], parsedEntry['Commit'], parsedEntry['Repo'],parsedEntry['Bug'],parsedEntry['Patch'], True)
         
         if 'Owner' in parsedEntry.keys():
            finalDownloadOnline(parsedEntry['CVE'], parsedEntry['Owner'], parsedEntry['Repo'], parsedEntry['Commit'], parsedEntry['Commit'], parsedEntry['Bug'], parsedEntry['Patch'])
            finalDownloadOnline(parsedEntry['CVE'], parsedEntry['Owner'], parsedEntry['Repo'], parsedEntry['Commit'], parsedEntry['Commit'], parsedEntry['Bug'], parsedEntry['Patch'], True)
        


# searches a combobox for a value containing the input 
def search(event): #GFG
    value = event.widget.get()
      
    if value == '':
        if str(event.widget) == '.commit':
            commitsLb['values'] = combobox_updater.get_combobox_values()
        if str(event.widget) == '.file':
            filesLb['values'] = combobox_updater2.get_combobox_values()
        if str(event.widget) == '.cve':
            cvesLb['values'] = cvesList
        if str(event.widget) == '.repo':
            reposLb['values'] = repoList
    else:
        data = []
        if str(event.widget) == '.commit':
            for item in combobox_updater.get_combobox_values(): 
                if value.lower() in item.lower(): 
                    data.append(item)
            if str(event.widget) == '.commit':
                 commitsLb['values'] = data
        if str(event.widget) == '.file':
             for item in combobox_updater2.get_combobox_values(): 
                if value.lower() in item.lower(): 
                    data.append(item)
                    #print('cc2',data)
                if str(event.widget) == '.file':
                 filesLb['values'] = data
        if str(event.widget) == '.cve':
            for item in cvesList: 
                if value.lower() in item.lower(): 
                    data.append(item)
            if str(event.widget) == '.cve':
                cvesLb['values'] = data
        if str(event.widget) == '.repo':
             for item in repoList: 
                 if value.lower() in item.lower(): 
                     data.append(item)
                     #print('ccc',data)
             if str(event.widget) == '.repo':
                reposLb['values'] = data




def change_prePatchTextBoxContent(content):
    """shows text content in pre patch text box

    Args:
       content(string): content for textbox
    Returns:
        None
    """
    prePatchTextBox.delete('1.0','end')
    prePatchTextBox.insert('1.0', content)  # Insert new content

def change_postPatchTextBoxContent(content):
    """shows text content in post patch text box

    Args:
       content(string): content for textbox
    Returns:
        None
    """
    postPatchTextBox.delete('1.0','end')
    postPatchTextBox.insert('1.0', content)  # Insert new content     



def save_token():
   file_path = os.path.join(cwd, 'token'  + ".txt")
   fileCommand = "w" if os.path.exists(file_path) else "x"
   token_file = open("token.txt", fileCommand)
   token_file.write(tokenOnlineInput.get())
   token_file.close()

            
#6 input entries
fileDirInput = Entry(master)
repoURLInput = Entry(master)
newRepoNameInput = Entry(master)
ownerOnlineInput =Entry(master)
commitOnlineInput  =Entry(master)
repoOnlineInput = Entry(master)
tokenOnlineInput = Entry(master)
cveInput = Entry(master)

#Entries' row-column-positions
fileDirInput.grid(row=0, column=1)
repoURLInput.grid(row=1, column=1)
newRepoNameInput.grid(row=1, column=10)
ownerOnlineInput.grid(row=0, column=6)
repoOnlineInput.grid(row=1, column=6) 
commitOnlineInput.grid(row=2, column=6)
tokenOnlineInput.grid(row=3, column=6)
cveInput.grid(row=2, column=10)
# Labels, standing for input names, along with buttons fulfilling their functions


file_path = os.path.join(cwd, 'token'  + ".txt")
if os.path.exists(file_path):
 token_file = open(file_path, 'r')
 token = token_file.read()
 tokenOnlineInput.delete(0,END)
 tokenOnlineInput.insert(0,token)




Label(master, text="File directory").grid(row=0) # if only the row index is selected, the default column index will be 0, same will be for the other way around
Button(master, text='Open file', command=lambda: browseFiles(fileDirInput ) ).grid(row=0, column=2, sticky=W, pady=4)
Label(master, text="Download repo").grid(row=1) # if only the row index is selected, the default column index will be 0, same will be for the other way around
Label(master, text="Commit name/hash").grid(row=2)  # if only the row index is selected, the default column index will be 0, same will be for the other way around
Button(master, text='Clone repo', command=lambda: repoUpdater.cloneRepo(repoURLInput.get(), newRepoNameInput.get())).grid(row=1, column=11, sticky=W , padx=0,pady=4)
Button(master, text='Save token', command=save_token).grid(row=3, column=7, sticky=W , padx=0,pady=4)

Label(master, text="Choose repo").grid(row=0, column = 9)
Label(master, text="Name new repo").grid(row=1, column = 9)
Label(master, text="CVE ID").grid(row=2, column = 9)
Button(master, text='Download CVE package', command=lambda: [finalDownloadOffline(cveInput.get() , combobox_updater.get_combobox_values()[ combobox_updater.get_commit_indexes()[0]],commitCombobox.get(), repoCombobox.get(),bugTextBox.get("1.0", "end") ,patchTextBox.get("1.0", "end"))    ,   finalDownloadOffline(cveInput.get() , commitCombobox.get(), commitCombobox.get(), repoCombobox.get(),bugTextBox.get("1.0", "end") ,patchTextBox.get("1.0", "end"), True)   ]).grid(row=2, column=11, sticky=W , padx=0,pady=4)
Button(master, text='Download CVE package(online)', command=lambda: [finalDownloadOnline(cveInput.get() , ownerOnlineInput.get(), repoOnlineInput.get(), commitOnlineInput.get(),  commitOnlineInput.get(),bugTextBox.get("1.0", "end") ,patchTextBox.get("1.0", "end"))  ,   finalDownloadOnline(cveInput.get() , ownerOnlineInput.get(), repoOnlineInput.get(), commitOnlineInput.get(), commitOnlineInput.get(),bugTextBox.get("1.0", "end") ,patchTextBox.get("1.0", "end"), True)   ]   ).grid(row=2, column=12, sticky=W , padx=0,pady=4)
Button(master, text='Save CVE entry', command= addOfflineItem).grid(row=3, column=2, sticky=W , padx=0,pady=4)
Button(master, text='Save CVE entry(online)', command= addOnlineItem).grid(row=3, column=3, sticky=W , padx=0,pady=4)
Button(master, text='Clear download entry',command=  removeItem).grid(row=3, column=10, sticky=W , padx=0,pady=4)
Button(master, text='Clear download list',  command=  removeItems ).grid(row=3, column=11, sticky=W , padx=0,pady=4)
Button(master, text='Download CVEs(auto)', command= downloadSavedCves ).grid(row=3, column=12, sticky=W , padx=0,pady=4)

# Buttons above the 2 windows
Label(master, text='Owner name(online)' ).grid(row=0, column=5)
Label(master, text='Repo name(online)' ).grid(row=1, column=5)
Label(master, text='Commit hash(online)').grid(row=2, column=5)
Label(master, text='Github token(online)').grid(row=3, column=5)
Label(master, text='CVE auto-download list').grid(row=3, column=0)

# Buttons under the 2 windows.
Button(master, text='Show  pre-patch and post-patch  files completely', command=lambda:  [ change_prePatchTextBoxContent( showCommitFile( combobox_updater.get_combobox_values()[ combobox_updater.get_commit_indexes()[0]]    , fileCombobox.get(), repoCombobox.get()) ),change_postPatchTextBoxContent( showCommitFile( combobox_updater.get_combobox_values()[ combobox_updater.get_commit_indexes()[1]] , fileCombobox.get(), repoCombobox.get()) )] ).grid(row=15, column=5, sticky=W+E, padx=0,pady=4)
Button(master, text='Show pre-patch and post-patch  files\' changed areas', command=lambda: [ change_prePatchTextBoxContent( showCommitArea( commitCombobox.get() , fileCombobox.get(),  repoCombobox.get())[1] ) , change_postPatchTextBoxContent(   showCommitArea(commitCombobox.get()  , fileCombobox.get(), repoCombobox.get())[2]   )]  ).grid(row=16, column=5, sticky=W+E , padx=0,pady=4 )
Button(master, text='Show  pre-patch and post-patch  files\' changed lines', command=lambda: [ change_prePatchTextBoxContent(getCommitLOCsOffline( combobox_updater.get_combobox_values()[ combobox_updater.get_commit_indexes()[1]] , repoCombobox.get(), True, fileCombobox.get() )[1]) ,  change_postPatchTextBoxContent(getCommitLOCsOffline( combobox_updater.get_combobox_values()[ combobox_updater.get_commit_indexes()[1]] , repoCombobox.get(), True, fileCombobox.get())[2])] ).grid(row=17, column=5, sticky=W+E , padx=0,pady=4)
Button(master, text='Show  pre-patch and post-patch  files completely(online)', command=lambda:  [change_prePatchTextBoxContent(showFileOnline(ownerOnlineInput.get(),repoOnlineInput.get(), combobox_updater2.get_previous_commitHash(),fileCombobox.get())) , change_postPatchTextBoxContent(showFileOnline(ownerOnlineInput.get(),repoOnlineInput.get(),commitOnlineInput.get(),fileCombobox.get() )) ] ).grid(row=15, column=6, sticky=W+E, padx=0,pady=4)
Button(master, text='Show pre-patch and post-patch  files\' changed areas(online)', command=lambda: [ change_prePatchTextBoxContent( showCommitAreaOnline( ownerOnlineInput.get() , repoOnlineInput.get(),  commitOnlineInput.get(), fileCombobox.get()  )[1]  ) , change_postPatchTextBoxContent( showCommitAreaOnline( ownerOnlineInput.get() , repoOnlineInput.get(),  commitOnlineInput.get(), fileCombobox.get())[2]  )]  ).grid(row=16, column=6, sticky=W+E , padx=0,pady=4 )
Button(master, text='Show  pre-patch and post-patch  files\' changed lines(online)', command=lambda: [ change_prePatchTextBoxContent(getCommitLOCsOnline( ownerOnlineInput.get() ,repoOnlineInput.get(),commitOnlineInput.get(), True,  fileCombobox.get())[1])  ,  change_postPatchTextBoxContent(getCommitLOCsOnline( ownerOnlineInput.get() ,repoOnlineInput.get(),commitOnlineInput.get(), True,  fileCombobox.get())[2])] ).grid(row=17, column=6, sticky=W+E , padx=0,pady=4)

Button(master, text="Fetch info online", command=lambda: [combobox_updater2.update_onlineFileValues(ownerOnlineInput.get() , repoOnlineInput.get(),commitOnlineInput.get()), combobox_updater2.set_previous_commitHash(ownerOnlineInput.get() , repoOnlineInput.get(),commitOnlineInput.get())    ] ).grid(row=1, column=2, sticky=W+E, padx=0,pady=4)
Button(master, text='Pull repo', command=lambda: repoUpdater.pullRepo() ).grid(row=1, column=3, sticky=W , padx=0,pady=4)

commitCombobox = ttk.Combobox(master, value=combobox_updater.get_combobox_values(), name='commit')
combobox_updater.set_combobox(commitCombobox)
fileCombobox= ttk.Combobox(master, value=combobox_updater2.get_combobox_values(), name='file')
combobox_updater2.set_combobox(fileCombobox)
cveDownloadListCombobox = ttk.Combobox(master, value=cveDownloadArr, name='cveDownloads')
repoCombobox = ttk.Combobox(master, value=repoList, name='repo')

#ONLY COMPARE CHANGES FROM SAME COMMIT

#2 different text boxes showing either whole file changes, areas of modifications or merely changed lines
prePatchTextBox= Text(master, height= 10,width= 40)
prePatchTextBox.grid(row=14, column=5)# textbox's row-column position
prePatchTextBox.insert('1.0','Blabla')
#prePatchTextBox.config(state= DISABLED) #read-only so you can't lose the content

postPatchTextBox = Text(master, height= 10,width= 40)
postPatchTextBox.grid(row=14, column=6)# textbox's row-column position
postPatchTextBox.insert('1.0','Blabla')
#postPatchTextBox.config(state= DISABLED)#read-only so you can't lose the content

bugTextBox= Text(master, height= 10,width= 40)
bugTextBox.grid(row=18, column=5)# textbox's row-column position
patchTextBox= Text(master, height= 10,width= 40)
patchTextBox.grid(row=18, column=6)# textbox's row-column position

#combo.bind("<<ComboboxSelected>>", selection_changed)

fileCombobox.grid(row=0, column=1)
filesLb = fileCombobox
filesLb.bind('<KeyRelease>',search)

commitCombobox.grid(row=2, column=1)
commitsLb = commitCombobox
commitsLb.bind('<KeyRelease>',search)

cveDownloadListCombobox.grid(row=3, column=1)
cvesLb = cveDownloadListCombobox
cvesLb.bind('<KeyRelease>',search)

repoCombobox.grid(row=0, column = 10)
reposLb = repoCombobox
reposLb.bind('<KeyRelease>',search)

Button(master, text='Choose repo', command=lambda: [combobox_updater.update_values(repoCombobox.get()), repoUpdater.setRepo(repoCombobox.get()) , repoUpdater.getRepo()   ] ).grid(row=0, column=11, sticky=W, pady=4)
Button(master, text='Select commit', command=lambda: [combobox_updater2.update_fileValues(commitCombobox.get()) ,  combobox_updater.setNeighboredCommitsIndexes(commitCombobox.get()), combobox_updater.get_commit_indexes()  ] ).grid(row=2, column=2, sticky=W , padx=0,pady=4)


#Quit button
Label(master, text='Pre-patch version').grid(row=12, column=5)
Label(master, text='Post-patch version').grid(row=12, column=6)
Label(master, text='Bug description').grid(row=19, column=5)
Label(master, text='Patch description').grid(row=19, column=6)
Button(master, text='Quit program', command=master.destroy).grid(row=20, column=5, sticky=W+E, pady=4, columnspan=2)
mainloop()
