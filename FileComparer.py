import hashlib


class FileComparer:
    def __init__(self, FileA, FileB):
        self.__FileA = FileA
        self.__FileB = FileB

    def __get_file_hash(self, filename):
        buffer_size = 65536
        sha1 = hashlib.sha1()
        with open(filename, 'rb') as f:
            while True:
                data = f.read(buffer_size)
                if not data:
                    break
                sha1.update(data)
        return sha1.hexdigest()

    def isFileSame(self):
        if self.__FileB == self.__FileA:
            return True
        FileAHash = self.__get_file_hash(self.__FileA)
        FileBHash = self.__get_file_hash(self.__FileB)
        return True if FileAHash == FileBHash else False
