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
        self.legal_moves = []
        self.camps = {'W' : None, 'B' : None}

    def create_pieces(self):
        for col in range(8):
            self.pieces['W'].append(Piece('W',f'W{col}' ))
            self.pieces['B'].append(Piece('B', f'B{col}'))

    def movepiece(self, player):
        while True:
            piece_label = input('Enter the label of the piece you want to move (e.g. W0): ').strip()
            coordinates = input('Enter the coordinates of where you want to move the piece (e.g. E2): ').strip().upper()
            camp = False

            if coordinates == 'camp':
                if player == 'W' and old_row == 0:
                    self.legal_moves.append((piece_to_move, ('camp')))
                    camp = True
                if player =='B' and old_row == 7:
                    self.legal_moves.append((piece_to_move, ('camp')))
                    camp = True
                move = 'camp'
            else:
                if len(coordinates) != 2 or not coordinates[0].isalpha() or not coordinates[1].isdigit():
                    print("Invalid coordinate format.")
                    continue

            col = ord(coordinates[0]) - ord('A')
            row = 8 - int(coordinates[1])

            if not (0 <= col <= 7 and 0 <= row <= 7):
                print("Coordinates out of bounds.")
                continue

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
                print("No piece found with that label.")
                continue

            if piece_to_move.player != player:
                print("That's not your piece.")
                continue
            if coordinates.lower() == 'camp':
                if (player == 'W' and old_row == 0) or (player == 'B' and old_row == 7):
                    self.camps[player] = piece_to_move
                    self.boardlayout[old_row][old_col]['piece'] = None
                    print(f"{piece_to_move.label} has entered the enemy camp!")
                    break
                else:
                    print("You can only enter the camp from the enemy back row.")
                    continue

            self.get_legal_moves()

            

            if not camp:
                move = (row, col)

            if (piece_to_move.label, move) not in self.legal_moves:
                print("That move is not legal.")
                self.legal_moves = []
                continue


            self.boardlayout[old_row][old_col]['piece'] = None
            if camp:
                break
            else:
                self.boardlayout[row][col]['piece'] = piece_to_move
            self.legal_moves = []
            break



    def get_legal_moves(self):
        for r in range(len(self.boardlayout)):
            for c in range(len(self.boardlayout[r])):
                if self.boardlayout[r][c]['piece']:
                    if self.boardlayout[r][c]['colour'] == 'R':
                        self.rook_moves(r,c)   
                    elif self.boardlayout[r][c]['colour'] == 'B':
                        self.king_moves(r,c) 
                    elif self.boardlayout[r][c]['colour'] == 'G':
                        self.knight_moves(r,c) 
                    elif self.boardlayout[r][c]['colour'] == 'Y':
                        self.bishop_moves(r,c) 


    def rook_moves(self, row, col):
        piece = self.boardlayout[row][col]['piece']
        for c in range(col-1, -1, -1):
            if self.boardlayout[row][c]['piece']:
                if self.boardlayout[row][c]['piece'].player == self.boardlayout[row][col]['piece'].player:
                    break
            self.legal_moves.append((piece.label, (row, c)))
            if self.boardlayout[row][c]['colour'] == 'R':
                break
        for c in range(col+1, 8):
            if self.boardlayout[row][c]['piece']:
                if self.boardlayout[row][c]['piece'].player == self.boardlayout[row][col]['piece'].player:
                    break
            self.legal_moves.append((piece.label, (row, c)))
            if self.boardlayout[row][c]['colour'] == 'R':
                break
        for r in range(row-1, -1, -1):
            if self.boardlayout[r][col]['piece']:
                if self.boardlayout[r][col]['piece'].player == self.boardlayout[row][col]['piece'].player:
                    break
            self.legal_moves.append((piece.label, (r, col)))
            if self.boardlayout[r][col]['colour'] == 'R':
                break
        for r in range(row+1, 8):
            if self.boardlayout[r][col]['piece']:
                if self.boardlayout[r][col]['piece'].player == self.boardlayout[row][col]['piece'].player:
                    break
            self.legal_moves.append((piece.label, (r, col)))
            if self.boardlayout[r][col]['colour'] == 'R':
                break

            
        


    def knight_moves(self, row, col):
        all_moves = [(row +2, col-1), (row+2, col+1), (row+1, col-2), (row+1, col+2), (row-1, col-2), (row-1, col+2), (row-2, col-1), (row-2, col+1)]
        piece = self.boardlayout[row][col]['piece']
        for move in all_moves:
            if 0 <= move[0] <= 7 and 0 <= move[1] <= 7:
                if self.boardlayout[move[0]][move[1]]['piece']:
                    if piece.player != self.boardlayout[move[0]][move[1]]['piece'].player:
                        self.legal_moves.append((piece.label, (move)))
                self.legal_moves.append((piece.label, (move)))

    def bishop_moves(self, row, col):
        piece = self.boardlayout[row][col]['piece']
        i = 1
        for r in range(row-1, -1, -1):
            if col-i < 0:
                break
            if self.boardlayout[r][col-i]['piece']:
                if self.boardlayout[r][col-i]['piece'].player == piece.player:
                    break
            self.legal_moves.append((piece.label, (r, col-i)))
            if self.boardlayout[r][col-i]['colour'] == 'Y':
                break
            i+=1
        i = 1
        for r in range(row-1, -1, -1):
            if col+i > 7:
                break
            if self.boardlayout[r][col+i]['piece']:
                if self.boardlayout[r][col+i]['piece'].player == piece.player:
                    break
            self.legal_moves.append((piece.label, (r, col+i)))
            if self.boardlayout[r][col+i]['colour'] == 'Y':
                break
            i+=1
        i = 1
        for r in range(row+1, 8):
            if col - r > 0:
                break
            if self.boardlayout[row][col-i]['piece']:
                if self.boardlayout[row][col-i]['piece'].player == piece.player:
                    break
            self.legal_moves.append((piece.label, (row, col-i)))
            if self.boardlayout[row][col-i]['colour'] == 'Y':
                break
            i+=1
        i = 0
        for r in range(row+1, 8):
            if col+i >7:
                break
            if self.boardlayout[row][col+i]['piece']:
                if self.boardlayout[row][col+i]['piece'].player == piece.player:
                    break
            self.legal_moves.append((piece.label, (row, col+i)))
            if self.boardlayout[row][col+i]['colour'] == 'Y':
                break
            i+=1
            
    
            



    def king_moves(self, row, col):
        all_moves = [(row +1, col-1), (row+1, col+1), (row+1, col), (row, col+1), (row, col-1), (row-1, col+1), (row-1, col-1), (row-1, col)]
        piece = self.boardlayout[row][col]['piece']
        for move in all_moves:
            if 0 <= move[0] <= 7 and 0 <= move[1] <= 7:
                if self.boardlayout[move[0]][move[1]]['piece']:
                    if piece.player != self.boardlayout[move[0]][move[1]]['piece'].player:
                        self.legal_moves.append((piece.label, (move)))
                self.legal_moves.append((piece.label, (move)))
        
    def isOver(self):
        b_pieces = []
        w_pieces = []
        for r in range (8):
            for c in range(8):
                piece =  self.boardlayout[r][c]['piece']
                if piece:
                    if piece.player == 'W':
                        w_pieces.append(piece.label)
                    elif piece.player == 'B':
                        b_pieces.append(piece.label)
        if len(b_pieces) < 2 or len(w_pieces)

                
    
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

B = Board()
B.printGrid()
while True:
    B.movepiece('W')
    B.printGrid()
    B.movepiece('B')
    B.printGrid()
