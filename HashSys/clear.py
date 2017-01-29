import os
from .hashsys import *
from .__init__ import *


def clear_dirs():
    for id1 in range(255):
        folder1 = out_path + os.sep + '%02x' % id1
        for id2 in range(255):
            folder2 = folder1 + os.sep + '%02x' % id2
            if not os.path.exists(folder2):
                continue
            else:
                for file in os.listdir(folder2):
                    os.remove(folder2 + os.sep + file)


def clear_by_hash(file_hash, extension=None):
    if extension:
        file_name = file_hash + '.' + extension
    else:
        file_name = file_hash

    folder1 = file_hash[0:2]
    folder2 = file_hash[2:4]
    path = out_path + folder1 + os.sep + folder2 + os.sep + file_name
    try:
        os.remove(path)
    except FileNotFoundError as e:
        print(e)
        return None
    return file_hash


def clear_files(source_path, extension=None):
    hash_pool = []
    for root, dirs, files in os.walk(source_path):
        for file in files:
            file_path = root + os.sep + file
            hash_pool.append(get_file_md5(file_path))
    hash_pool = list(set(hash_pool))
    # if extension:
    for hash in hash_pool:
        clear_by_hash(hash, extension)
    # else:
    #     map(clear_by_hash, hash_pool)