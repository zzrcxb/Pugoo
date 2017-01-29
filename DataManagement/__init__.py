from config import *
from os import sep
from HashSys.hashsys import check_and_create

if not RAW_DATA_PATH.endswith(sep):
    raw_path = RAW_DATA_PATH + sep
else:
    raw_path = RAW_DATA_PATH

if not DOWNLOAD_PATH.endswith(sep):
    dl_path = DOWNLOAD_PATH + sep
else:
    dl_path = DOWNLOAD_PATH

if not ROOT_PATH.endswith(sep):
    root_path = ROOT_PATH + sep
else:
    root_path = ROOT_PATH

if not TRAINING_SET_PATH.endswith(sep):
    train_path = TRAINING_SET_PATH + sep
else:
    train_path = TRAINING_SET_PATH

if not TMP_PATH.endswith(sep):
    tmp_path = TMP_PATH + sep
else:
    tmp_path = TMP_PATH

db_url = ''.join(['mysql+pymysql://', DB_USER, ':', DB_PASSWD , '@', DB_DOMAIN, '/', DB_NAME])
