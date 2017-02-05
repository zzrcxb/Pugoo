from GoGame.game import Game
from GoGame.phantom import phantom

from time import time

start = time()
b = phantom(None, (30, 30), 40, 19)
b.create_board()
g = Game(b, _tic=True, _backup=False)

g.load_game('/home/neil/Database/training/00/09/0009d0384f8d9121f469ed78208b9fd5')
# g.load_game('/home/neil/Database/training/06/49/0649b9245943c425b82a7ca997d8c546')

g.goto(len(g.record))
print('Developed', time() - start)

nodes = [53]
# nodes = [165, 32, 79, 120, 19, 17, 111, 9, 189, 55, 26, 192, 97, 118]
for i in nodes:
    g.clear_group(i)
g.score_final(debug=True)
print("Period", time() - start)
print("Performance report")
print(g.monitor)