from GoGame.chessboard import ChessBoard
from GoGame.game import Game, Point
from GoGame.phantom import phantom
import tkinter as tk

root = tk.Tk()

b = ChessBoard(root, (30, 30), 50, 19)
b.create_board()
g = Game(b)

g.show_groups()
g.load_game('/home/neil/Pugoo/Database/training/00/09/0009d4f91a7b48a8fec4fcc54dc2fdb4')
g.goto(len(g.record))

button = tk.Button(root, text='Next', command=g.next_step)
button.pack(side=tk.LEFT)
button = tk.Button(root, text='Prev', command=g.prev_step)
button.pack(side=tk.LEFT)
button = tk.Button(root, text='Show', command=g.show_groups)
button.pack(side=tk.LEFT)
button = tk.Button(root, text='Exit', command=root.destroy)
button.pack(side=tk.LEFT)

root.mainloop()
