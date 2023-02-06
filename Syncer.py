import os
import shutil
import sys
import time
import types
from FileComparer import FileComparer


class Syncer:

    def __init__(self):
        self.__setConstants()
        self.__parseCommandLineArguments()
        self.__listInit()
        self.__logFile = open(self.__logFilePath, "a")
        self.__pathStepLen = len(self.__originalFolderPath) + 1
        self.__validatePath()

    def __validatePath(self):
        if self.__originalFolderPath[-1] != "\\":
            self.__originalFolderPath = self.__originalFolderPath + "\\"
        if self.__secondFolderPath[-1] != "\\":
            self.__secondFolderPath = self.__secondFolderPath + "\\"
        self.__originalFolderPath = self.__originalFolderPath.replace(os.sep, '/')
        self.__secondFolderPath = self.__secondFolderPath.replace(os.sep, '/')
        if not os.path.exists(self.__secondFolderPath):
            os.mkdir(self.__secondFolderPath)

    def __listInit(self):
        self.__originalFilePath = []
        self.__originalFolderPathList = []
        self.__secondFolderPaths = []
        self.__secondFilePaths = []

    def __parseCommandLineArguments(self):
        if not self.__validateCommandLineArguments():
            raise Exception("Bad command line arguments!")
        self.__originalFolderPath = self.__systemParseCommandLineArgument(self.consts.OriginalFolder)
        self.__secondFolderPath = self.__systemParseCommandLineArgument(self.consts.SyncedFolder)
        self.__logFilePath = self.__systemParseCommandLineArgument(self.consts.LogFilePlace)
        self.__SyncTime = self.__systemParseCommandLineArgument(self.consts.Delay)

    def __setConstants(self):
        self.consts = types.SimpleNamespace()
        self.consts.OriginalFolder = 1
        self.consts.SyncedFolder = 2
        self.consts.LogFilePlace = 3
        self.consts.Delay = 4
        self.consts.instruction = "First value: - Original path, \n Second value: - Sync files to path: \n Third " \
                                  "value: - Log file path, \n Fourth value - Time between operations in seconds "
        self.consts.expectedCommandLine = 5

    def __pathFolderCreation(self, FolderPath):
        SyncedFolder = os.path.join(self.__secondFolderPath, FolderPath[self.__pathStepLen::])
        if not os.path.exists(SyncedFolder):
            os.mkdir(SyncedFolder)
            self.log("Created directory {} in {}".format(SyncedFolder, self.__secondFolderPath))

    def __copyFiles(self):
        for folder in self.__originalFolderPathList:
            self.__pathFolderCreation(folder)
        for file in self.__originalFilePath:
            self.__pathFileCopy(file)

    def __getOriginalFolderContent(self):
        originalFolders, originalFiles = self.__getFolderContent(self.__originalFolderPath, True)
        self.__originalFolderPathList = originalFolders
        self.__originalFilePath = originalFiles

    def __getFolderContent(self, targetFolder, topdown=False):
        resultFolders = []
        resultFiles = []
        for (root, folder_names, file_names) in os.walk(targetFolder, topdown=topdown):
            for folder in folder_names:
                resultFolders.append(os.path.join(root, folder))
            for file in file_names:
                resultFiles.append(os.path.join(root, file))
        return resultFolders, resultFiles

    def __getSecondFolderContent(self):
        secondFolders, secondFiles = self.__getFolderContent(self.__secondFolderPath, False)
        self.__secondFolderPaths = secondFolders
        self.__secondFilePaths = secondFiles

    def __compareExistingFiles(self, FolderTwoPath):
        destination = FolderTwoPath.replace(self.__secondFolderPath, self.__originalFolderPath)
        comparer = FileComparer(FolderTwoPath, destination)
        if not comparer.isFileSame():
            os.replace(FolderTwoPath, destination)
            self.log("Replaced File {} with {}".format(FolderTwoPath, destination))

    def log(self, str):
        self.__logFile.write("{}\n".format(str))
        print(str)

    def __pathFileCopy(self, File):
        synced_file = os.path.join(self.__secondFolderPath, File[self.__pathStepLen::])
        shutil.copy(File, synced_file)
        self.log("Copied {} to {}".format(File, synced_file))

    def folderSync(self):
        while True:
            self.__listInit()
            self.__getOriginalFolderContent()
            self.__copyFiles()
            self.__getSecondFolderContent()
            self.__secondFilePaths.sort(key=len, reverse=True)
            self.__secondFolderPaths.sort(key=len, reverse=True)
            self.__syncSecondFolder()
            time.sleep(self.__SyncTime)

    def __systemParseCommandLineArgument(self, option):
        try:
            match option:
                case self.consts.OriginalFolder | self.consts.SyncedFolder | self.consts.LogFilePlace:
                    return sys.argv[option]
                case self.consts.Delay:
                    return float(sys.argv[option])
        except:
            print(self.consts.instruction)

    def __validateCommandLineArguments(self):
        if len(sys.argv) != self.consts.expectedCommandLine:
            print(self.consts.instruction)
            return False
        return True

    def __syncSecondFolder(self):
        for file in self.__secondFilePaths:
            if file.replace(self.__secondFolderPath, self.__originalFolderPath) not in self.__originalFilePath:
                os.remove(file)
                self.log("Removed file {}".format(file))
            if file.replace(self.__secondFolderPath, self.__originalFolderPath) in self.__originalFilePath:
                self.__compareExistingFiles(file)
        for folder in self.__secondFolderPaths:
            if folder.replace(self.__secondFolderPath, self.__originalFolderPath) not in self.__originalFolderPathList:
                shutil.rmtree(folder)
                self.log("Removed directory {}".format(folder))
