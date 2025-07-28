import random

class Piece:
    def __init__(self, player,label):
        self.player = player
        self.label = label


class Board:
    def __init__(self):
        self.pieces = {'W': [], 'B': []}
        self.create_pieces()
        self.colours = [
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
                row.append({'colour' : self.colours[rows][col], 'piece': None, 'LegalMoves': []})
            board.append(row)
        for col in range(8):
            board[0][col]['piece'] = self.pieces['B'][col]
            board[7][col]['piece'] = self.pieces['W'][col]
        self.boardlayout = board   

    def create_pieces(self):
        for col in range(8):
            self.pieces['W'].append(Piece('W',f'W{col}' ))
            self.pieces['B'].append(Piece('B', f'B{col}'))

    def movepiece(self, player):
        piece_label = input('Enter the label of the piece you want to move: ')
        coordinates = input('Enter the coordinates of where you want to move the piece e.g. E2: ')
        
        try:
            col = ord(coordinates[0]) - ord('A')
            row = 8 - int(coordinates[1])  
        except (IndexError, ValueError):
            print("Invalid input format.")
            return
        
        piece_to_move = None
        for r in range(8):
            for c in range(8):
                piece = self.boardlayout[r][c]['piece']
                if piece and piece.label == piece_label:
                    piece_to_move = piece
                    old_row, old_col = r, c
                    break
            if piece_to_move:
                break

        if not piece_to_move:
            print('No piece found with that label')
            return


        self.boardlayout[old_row][old_col]['piece'] = None
        self.boardlayout[row][col]['piece'] = piece_to_move

    def get_legal_moves(self):
        for r in range(len(self.boardlayout)):
            for c in range(len(self.boardlayout[i])):
                if self.boardlayout[r][c]['piece']:
                    if self.boardlayout[r][c]['colour'] == 'R':
                        for i in range(r, -1 ,-1):
                            if self.boardlayout[i][c]['colour'] != 'R':
                                pass
                            if self.boardlayout[i][c]['piece']:
                                if self.boardlayout[i][c]['piece'].player == self.boardlayout[r][c]['piece'].player:
                                    pass
                                
                                
                    elif self.boardlayout[r][c]['colour'] == 'B':
                        pass
                    elif self.boardlayout[r][c]['colour'] == 'G':
                        pass
                    elif self.boardlayout[r][c]['colour'] == 'Y':
                        pass




    
        
        
        



        

    def randomlayout(self):
        pass
        # y = []
        # with open('Tiles.txt') as f:
        #     x = f.readlines()
        #     x = [line.strip() for line in x]
        #     x = [list(line) for line in x]
        #     for i in range(1,5):
        #         x.pop(random.randint(1,(8-i)))
        #     print(x)
        #     for i in range(4):
        #         x[i] = [x[i][k:k+4] for k in range (0, len(x[i]), 4)]
        #         for j in range(random.randint(1,4)):
        #             if j == 1:
        #                 x[i] = LeftRotate90(x[i])
        #             elif j == 2:
        #                 x[i] = RightRotate90(x[i])
        #             elif j ==3:
        #                 x[i] = Rotate180(x[i])
        #             for item in x[i]:
        #                 y.append(item)
        # colours = []
        # print(len(y))
        # for i in range(4):
        #     colours.append(y[i]+y[i+4]+y[i+8]+y[i+12])
        # self.colours = x
        # board = []

        # for rows in range(8):
        #     row = []
        #     for col in range(8):
        #         row.append({'colour' : self.colours[rows][col], 'piece': None})
        #     board.append(row)
        # for col in range(8):
        #     board[0][col]['piece'] = f'B{col}'
        #     board[7][col]['piece'] = f'W{col}'
        # self.boardlayout = board      


    
    def printGrid(self):
        print("    A   B   C   D   E   F   G   H")
        print("  +---+---+---+---+---+---+---+---+")
        for row_num, row in enumerate(self.boardlayout):
            row_str = f'{8-row_num}  |'
            for square in row:
                if square['piece']:
                    piece = square['piece'].label
                else:
                    piece = '  '
                row_str += f"{square['colour']}{piece}|"
            print(row_str + f" {8 - row_num}")
            print("  +---+---+---+---+---+---+---+---+")
        print("    A   B   C   D   E   F   G   H")

def RightRotate90(grid):
    return [list(reversed(col)) for col in zip(*grid)]
def LeftRotate90(grid):
    return [list(row) for row in zip(*grid)][::-1]
    
def Rotate180(grid):
    return  [row[::-1] for row in grid[::-1]]

B = Board()
B.printGrid()
B.movepiece('W')
B.printGrid()