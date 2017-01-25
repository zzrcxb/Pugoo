class FileFormatError(Exception):
    pass


class FileDecodeError(UnicodeDecodeError):
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