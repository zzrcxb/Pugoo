from GoGame.game import Game
from GoGame.phantom import phantom

from time import time

start = time()
b = phantom(None, (30, 30), 40, 19)
g = Game(b, _backup=False, _tic=True)

g.load_game('/home/neil/Database/training/00/09/0009d0384f8d9121f469ed78208b9fd5')
# g.load_game('/home/neil/Database/training/06/49/0649b9245943c425b82a7ca997d8c546')

g.goto(len(g.record))
g.remove_dead()
print(g.score_final())
print(time() - start)
print(g.monitor)
