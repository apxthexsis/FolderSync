import os
import shutil
import time
import hashlib
import sys
import types

def CompareExistingFile(z, synced, originalPath, Logfile):
    shash = hash_check(z)
    destination = z.replace(synced, originalPath)
    ohash = hash_check(destination)
    if shash != ohash:
        os.replace(z, destination)
        log("Replaced {} {}".format(z, destination), Logfile)

def PathFolderCreation(synced, file, pathsteplen, CommonList, Logfile):
    SyncedFolder = os.path.join(synced, file[pathsteplen::])
    CommonList.append(SyncedFolder)
    if not os.path.exists(SyncedFolder):
        os.mkdir(SyncedFolder)
        log("Created directory {} in {}".format(SyncedFolder, synced), Logfile)
def PathFileCopy(synced, pathsteplen, CommonList, f, Logfile):
    SyncedFile = os.path.join(synced, f[pathsteplen::])
    CommonList.append(SyncedFile)
    shutil.copy(f, SyncedFile)
    log("Copied {} to {}".format(f, SyncedFile), Logfile)

def hash_check(filename):
    buffer_size = 65536
    sha1 = hashlib.sha1()
    with open(filename, 'rb') as f:
        while True:
            data = f.read(buffer_size)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()


def log(str,file):
    file.write("{}\n".format(str))
    print(str)


def check_original_folder(originalPath, Folderpath, Filepath):
    for (root, folder_names, file_names) in os.walk(originalPath):
        for f in folder_names:
            Folderpath.append(os.path.join(root, f))
        for i in file_names:
            Filepath.append(os.path.join(root, i))


def systemParseCommandLineArgument(option):
    consts = types.SimpleNamespace()
    consts.OriginalFolder = 1
    consts.SyncedFolder = 2
    consts.LogFilePlace = 3
    consts.Delay = 4
    try:
        match option:
            case consts.OriginalFolder | consts.SyncedFolder | consts.LogFilePlace:
                return sys.argv[option]
            case consts.Delay:
                return float(sys.argv[option])
    except:
        print("First value: - Original path, \n Second value: - Sync files to path: \n Third value: - Log file path, \n Fourth value - Time between operations in seconds ")

def validatecommandlinearguments():
    if len(sys.argv) != 5:
        print("Invalid amount of arguments passed should be 4!!")
        return False
    return True


def copyfunction(Folderpath, synced, pathsteplen, CommonList, Filepath, Logfile):
    for file in Folderpath:
        PathFolderCreation(synced, file, pathsteplen, CommonList, Logfile)
    for f in Filepath:
        PathFileCopy(synced, pathsteplen, CommonList, f, Logfile)


def CheckSecondFolder(synced, CommonList, secondfilepaths, secondfolderpaths):
    for (root_synced, second_folder_names, second_file_names) in os.walk(synced, topdown=False):
        for v in second_file_names:
            if v not in CommonList:
                secondfilepaths.append(os.path.join(root_synced, v))
        for x in second_folder_names:
            if x not in CommonList:
                delete = os.path.join(root_synced, x)
                secondfolderpaths.append(delete)


def SyncFolder(secondfilepaths, CommonList, Logfile, synced, originalPath, secondfolderpaths):
    for z in secondfilepaths:
        if z not in CommonList:
            os.remove("".join(z))
            log("Removed file {}".format(z), Logfile)
        if z in CommonList:
            CompareExistingFile(z, synced, originalPath, Logfile)
    for b in secondfolderpaths:
        if b not in CommonList:
            os.rmdir("".join(b))
            log("Removed directory {}".format("".join(b)), Logfile)


def FolderSync(originalPath, synced, pathsteplen, Logfile):
    Filepath = []
    Folderpath = []
    CommonList = []
    secondfolderpaths = []
    secondfilepaths = []

    check_original_folder(originalPath, Folderpath, Filepath)
    copyfunction(Folderpath, synced, pathsteplen, CommonList, Filepath, Logfile)
    CheckSecondFolder(synced, CommonList, secondfilepaths, secondfolderpaths)
    secondfilepaths.sort(key=len, reverse=True)
    secondfolderpaths.sort(key=len, reverse=True)
    SyncFolder(secondfilepaths, CommonList, Logfile, synced, originalPath, secondfolderpaths)


def main():
    if not validatecommandlinearguments():
        return -1
    varorigin = systemParseCommandLineArgument(1)
    varsynced = systemParseCommandLineArgument(2)
    if varorigin[-1] != "\\":
        varorigin = varorigin + "\\"
    if varsynced[-1] != "\\":
        varsynced = varsynced + "\\"
    originalPath = varorigin.replace(os.sep, '/')
    synced = varsynced.replace(os.sep, '/')
    pathsteplen = len(originalPath)
    Logfile = open(systemParseCommandLineArgument(3), "a")
    if not os.path.exists(synced):
        os.mkdir(synced)

    while True:
        FolderSync(originalPath, synced, pathsteplen, Logfile)
        time.sleep((systemParseCommandLineArgument(4)))

if __name__ == '__main__':
    main()