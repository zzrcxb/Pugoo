# This is a sample file used to convert source file from 'sgf' to 'bg' and add file to database
# Make sure your database configurations are correctly set.
# Please copy to parent folder and type 'python3 data_run.py'

from HashSys.clear import *
from DataManagement.add2set import *
from HashSys.hashsys import check_and_create

path = ''  # Your input filw directory

check_and_create()
clear_files(path)
add2set(path, source='Where are data from?', log_path='./Log', mode='normal')
