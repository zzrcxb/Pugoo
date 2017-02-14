# Copy gui_run.py to parent folder and type 'python3 gui_run.py'

from GoGame.chessboard import ChessBoard
from GoGame.game import Game
from GoGame.phantom import phantom
import tkinter as tk
from GoGame.final import circle_analysis
from time import sleep

root = tk.Tk()

b = ChessBoard(root, (30, 30), 35, 19)
b.create_board()
g = Game(b, _backup=False)

button = tk.Button(root, text='Show Groups', command=g.show_groups)
button.pack(side=tk.LEFT)
button = tk.Button(root, text='Exit', command=root.destroy)
button.pack(side=tk.LEFT)

g.show_groups()
g.load_game('./Samples/sample.bg')

print("Going to the end of game, and sleep 3s")
g.goto(len(g.record))  # Goto the end of game
sleep(3)  #

print("Gonna remove dead groups and sleep 5s")
g.remover()  # Remove dead groups
sleep(5)

print("Gonna get final score")
score = g.score_final()  # Get final score
print("Final score is", score)

root.mainloop()
