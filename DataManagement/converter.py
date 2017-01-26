import re
import json
from .__init__ import *
from .file_errors import *
from .gobase import GoBase
import os


# need to catch IOError
def SGF2Json(sgf, labels, filename):  # result > 0 black win result < 0, white win
    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)

    pattern = re.compile(r'(B|W)(\[)([a-s]?[a-s]?)(\])')
    result = []
    steps = pattern.findall(sgf)
    # Deal with labels
    for step in steps:
        if len(step[2]) == 0:  # Someone pass
            i = -1
            j = -1
        elif len(step[2]) == 2:
            i = ord(step[2][0]) - ord('a')
            j = ord(step[2][1]) - ord('a')
        else:
            return None
        result.append([i, j])

    bg_path = tmp_path + filename + '.bg'
    try:
        with open(bg_path, 'w') as out:
            json.dump(dict(record=result, attrs=labels), out)
    except IOError as e:
        print(e, 'From converter')
        return False

    go_base = GoBase(fileformat='bg', size=labels['SZ'], rule=labels['RU'], komi=labels['KM'], result=labels['RE'])
    return go_base