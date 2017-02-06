from HashSys.clear import *
from DataManagement.add2set import *

path_base = '/home/neil/Database/NNGS/'
path = path_base + '1997'

clear_files(path)
add2set(path, source='NNGS', debug=True, log_path='./Log', mode='normal')
