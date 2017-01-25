from .__init__ import training_set_path
import os
import hashlib

out_path = training_set_path


def check_and_create():
    global out_path
    flag = True
    for id1 in range(255):
        folder1 = out_path + os.sep + '%02x' % id1
        if not os.path.exists(folder1):
            os.makedirs(folder1)
            flag = False
        for id2 in range(255):
            folder2 = out_path + os.sep + '%02x' % id1 + os.sep + '%02x' % id2
            if not os.path.exists(folder2):
                os.makedirs(folder2)
                flag = False
    return flag


def move_file_to_hash(file_path, buf_size=65536, debug=False):
    global out_path
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

    # Move file
    hash_code = md5.hexdigest()
    filename = file_path.split(os.sep)[-1]
    if len(filename.split('.')) != 1:
        extension = filename.split('.')[-1]
    else:
        extension = None

    destination = out_path + os.sep + hash_code[0:2] + os.sep + hash_code[2:4] + os.sep + hash_code
    if extension:
        destination = destination + '.' + extension

    if debug:
        print(file_path, 'MD5:', hash_code)
        print('Extension', extension)
        print('Destination', destination)

    try:
        os.rename(file_path, destination)
    except PermissionError as e:
        print(e)
        return False
    return True


# Return path of file
def read_file_from_hash(file_md5, extension=None):
    global out_path

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
