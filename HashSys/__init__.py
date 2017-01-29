import config
from config import *
from os import sep

if not RAW_DATA_PATH.endswith(sep):
    raw_path = RAW_DATA_PATH + sep
else:
    raw_path = RAW_DATA_PATH

if not TRAINING_SET_PATH.endswith(sep):
    out_path = TRAINING_SET_PATH + sep
else:
    out_path = TRAINING_SET_PATH