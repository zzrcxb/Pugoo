import re
import json
from .__init__ import *
from .gobase import GoBase
import os

def SGF2Json(sgf, labels, filename):  # result > 0 black win result < 0, white win
    if os.path.exists(tmp_path):
        os.makedirs(tmp_path)

    pattern = re.compile(r'(B|W)(\[)([a-s]?)([a-s]?)(\])')
    result = []
    steps = pattern.findall(sgf)
    # Deal with labels




    for step in steps:
        if len(step[2]) != 2:  # Someone pass
            i = -1
            j = -1
        else:
            i = ord(step[2][0]) - ord('a')
            j = ord(step[2][1]) - ord('a')
        result.append([i, j])

    bg_path = tmp_path + filename + '.bg'
    try:
        with open(bg_path, 'w') as out:
            json.dump(dict(record=result, rule=rule, result=end, linenum=sz, komi=komi), out)
    except IOError as e:
        print(e)
        return False
