import random

class Piece:
    def __init__(self, player,x,y):
        self.player = player
        self.posx = x
        self.posy = y
    def movepiece():
        pass
class Board:
    def __init__(self):
        self.colors = [
        ['R', 'Y', 'G', 'B', 'R', 'Y', 'G', 'B'],
        ['Y', 'R', 'B', 'G', 'Y', 'R', 'B', 'G'],
        ['G', 'B', 'R', 'Y', 'G', 'B', 'R', 'Y'],
        ['B', 'G', 'Y', 'R', 'B', 'G', 'Y', 'R'],
        ['R', 'Y', 'G', 'B', 'R', 'Y', 'G', 'B'],
        ['Y', 'R', 'B', 'G', 'Y', 'R', 'B', 'G'],
        ['G', 'B', 'R', 'Y', 'G', 'B', 'R', 'Y'],
        ['B', 'G', 'Y', 'R', 'B', 'G', 'Y', 'R'],
    ]
        board = []
        for rows in range(8):
            row = []
            for col in range(8):
                row.append({'colour' : self.colors[rows][col], 'piece': None})
            board.append(row)
        for col in range(8):
            board[0][col]['piece'] = f'B{col}'
            board[7][col]['piece'] = f'W{col}'
        self.boardlayout = board   
           
    def randomlayout(self):
        with open('Tiles.txt') as f:
            x = f.readlines().strip()
            for i in range(4):
                x.pop(random.randint(1,(8-i)))
                for j in range(random.randint(1,4)):
                    if j == 1:
                        x[i] = x[i][::-1]   
                    if j == 2:
                        y = []
                        for row_num, row in enumerate(x):
                            y.append()


    
    def printGrid(self):
        print("    A   B   C   D   E   F   G   H")
        print("  +---+---+---+---+---+---+---+---+")
        for row_num, row in enumerate(self.boardlayout):
            row_str = f'{8-row_num}  |'
            for square in row:
                if square['piece']:
                    piece = square['piece']
                else:
                    piece = '  '
                row_str += f"{square['colour']}{piece}|"
            print(row_str + f" {8 - row_num}")
            print("  +---+---+---+---+---+---+---+---+")
        print("    A   B   C   D   E   F   G   H")

B = Board()
B.printGrid()

