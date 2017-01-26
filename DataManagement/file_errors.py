class FileFormatError(Exception):
    pass


class FileDecodeError(Exception):
    pass


class FileContentError(Exception):
    pass


class FileResultError(FileContentError):
    pass


class FileKomiError(FileContentError):
    pass


class FileSizeError(FileContentError):
    pass


class FileLabelMissed(FileContentError):
    pass

class FileStepError(FileContentError):
    pass

class FileHandicapError(FileContentError):
    pass