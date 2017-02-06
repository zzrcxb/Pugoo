from config import *
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from DataManagement.gobase import GoBase
from GoGame.phantom import phantom
from GoGame.game import Game
from HashSys.hashsys import read_file_from_hash

db_url = ''.join(['mysql+pymysql://', DB_USER, ':', DB_PASSWD , '@', DB_DOMAIN, '/', DB_NAME])

engine = create_engine(db_url)
DBSession = sessionmaker(bind=engine)
session = DBSession()

statistic = {_:0 for _ in range(10)}
statistic[400] = 0
large_list = []
err_file = []
offset = 0
limit = 100
b = phantom(None, (30, 30), 40, 19)
while 1:
    results = session.query(GoBase.filehash, GoBase.result).filter(GoBase.result != 400).filter(GoBase.result != -400)\
        .filter(GoBase.size==19).filter(GoBase.result < 10).filter(GoBase.result > -10).offset(offset).limit(limit)
    for result in results:
        g = Game(b, _backup=False)
        g.load_game(read_file_from_hash(result.filehash))
        if not g.goto(len(g.record)):
            err_file.append(result.filehash)
            print("[Error!]" + result.filehash)
            continue
        g.remove_dead()
        res = g.score_final()
        diff = abs(res - result.result)
        print(res, diff)
        if diff < 10:
            statistic[diff] += 1
        else:
            statistic[400] += 1
            large_list.append([result.filehash, result.result])
    print("offset", offset)
    if offset == 900:
        break
    if len(list(results)) != limit:
        break
    offset += len(list(results))

print(statistic)
print(large_list)
with open('../result.txt', 'w') as f:
    f.write(repr(statistic) + '\n')
    f.write(repr(large_list) + '\n')
    f.write(repr(err_file) + '\n')
