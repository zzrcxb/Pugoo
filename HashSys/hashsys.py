from .__init__ import out_path
import os
import hashlib


def check_and_create():
    flag = True
    for id1 in range(256):
        folder1 = out_path + os.sep + '%02x' % id1
        if not os.path.exists(folder1):
            os.makedirs(folder1)
            flag = False
        for id2 in range(256):
            folder2 = folder1 + os.sep + '%02x' % id2
            if not os.path.exists(folder2):
                os.makedirs(folder2)
                flag = False
    return flag


def get_file_md5(file_path, buf_size=65536):
    md5 = hashlib.md5()
    # Get file hash
    try:
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(buf_size)
                if not data:
                    break
                md5.update(data)
    except FileNotFoundError as e:
        print(e)
        return False
    except IOError as e:
        print(e)
        return False
    return md5.hexdigest()


def get_file_sha1(file_path, buf_size=65536):
    sha1 = hashlib.sha1()
    try:
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(buf_size)
                if not data:
                    break
                sha1.update(data)
    except FileNotFoundError as e:
        print(e)
        return False
    except IOError as e:
        print(e)
        return False
    return sha1.hexdigest()


def move_file_by_hash(hash_code, file_path, extension=None, debug=False):
    destination = out_path + hash_code[0:2] + os.sep + hash_code[2:4] + os.sep + hash_code
    if extension:
        destination = destination + '.' + extension

    if debug:
        print(file_path, 'MD5:', hash_code)
        print('Extension', extension)
        print('Destination', destination)

    try:
        if not os.path.exists(destination):
            os.rename(file_path, destination)
        else:
            print('File existed!', file_path, '=>', destination)
            return None
    except PermissionError as e:
        print(e)
        return False
    except FileExistsError as e:
        print(e)
        return False
    return destination


# Return path of file
def read_file_from_hash(file_md5, extension=None):
    if len(file_md5) < 4:
        return False
    folder1 = file_md5[0:2]
    folder2 = file_md5[2:4]

    file_path = out_path + os.sep + folder1 + os.sep + folder2 + os.sep + file_md5
    if extension:
        file_path = file_path + '.' + extension

    if os.path.exists(file_path):
        return file_path
    else:
        return False
