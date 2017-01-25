import re
import json
from os import listdir
import os

def SGF2Json(inpath, outpath, rule='Other', end=None, sz=19, komi=0):  # result > 0 black win result < 0, white win
    pattern = re.compile(r'(B|b|W|w)(\[)([a-s][a-s])?(\])')
    content = ''
    result = []
    
    with open(inpath, 'rb') as insgf:
        try:
            content = insgf.read().decode('utf-8')
        except UnicodeDecodeError:
            with open(inpath, 'rb') as insgf:
                try:
                    content = insgf.read().decode('gb2312')
                except:
                    return

    res = pattern.findall(content)
    # print(res)
    for onestep in res:
        if len(onestep[2]) != 2:
            i = -1
            j = -1
        else:
            i = ord(onestep[2][0]) - ord('a')
            j = ord(onestep[2][1]) - ord('a')
        result.append([i, j])

    with open(outpath, 'w') as out:
        json.dump(dict(name=os.path.basename(inpath), record=result, rule=rule, result=end, linenum=sz, komi=komi), out)
