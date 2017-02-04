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
    if labels['HA'] != 0:
        del labels['AB']

    pattern = re.compile(r'[^A](B|W)(\[)([a-s]?[a-s]?)(\])')
    result = []
    handicap = []
    steps = pattern.findall(sgf)

    # Find handicap
    if labels['HA'] != 0:
        pos = sgf.find('AB[')
        for i in range(int(labels['HA'])):
            temp = sgf[pos:len(sgf)].find('[')
            if temp == -1:
                raise FileContentError()
            pos = temp + pos + 1
            x = sgf[pos]
            y = sgf[pos + 1]
            handicap.append([ord(x) - ord('a'), ord(y) - ord('a')])
        result.append([-1, -1, 1])  # Add a null black point

    # Deal with labels
    for step in steps:
        if len(step[2]) == 0:  # Someone pass
            i = -1
            j = -1
        elif len(step[2]) == 2:
            i = ord(step[2][0]) - ord('a')
            j = ord(step[2][1]) - ord('a')
        else:
            raise FileStepError()
        if step[0] == 'B':
            color = 1
        elif step[0] == 'W':
            color = -1
        else:
            raise FileContentError()
        result.append([i, j, color])

    bg_path = tmp_path + filename + '.bg'
    try:
        with open(bg_path, 'w') as out:
            json.dump(dict(record=result, attrs=labels, handicap=handicap), out)
    except IOError as e:
        print(e, 'From converter')
        return False

    go_base = GoBase(fileformat='bg', size=labels['SZ'], rule=labels['RU'], komi=labels['KM'],
                     result=labels['RE'], handicap=labels['HA'])
    return go_base