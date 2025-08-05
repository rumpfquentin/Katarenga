import random
from dataclasses import dataclass
from typing import Optional, Union, Tuple




class Piece:
    def __init__(self, player,label):
        self.player = player
        self.label = label

@dataclass
class MoveRecord:
    piece : Piece
    src : Tuple[int, int]
    dest : tuple[int, int]
    captured_piece : Optional[Piece] = None
    was_camped: bool = False

class Board:


    def __init__(self):
        self.pieces = {'W': [], 'B': []}
        self.create_pieces()
        self.colours = self.randomlayout()

        print("    A   B   C   D   E   F   G   H")
        print("  +---+---+---+---+---+---+---+---+")
        for row_num, row in enumerate(self.colours):
            row_str = f'{8-row_num} |'
            for square in row:
                row_str += f" {square} |"
            print(row_str + f" {8 - row_num}")
            print("  +---+---+---+---+---+---+---+---+")
        print("    A   B   C   D   E   F   G   H")

        blacksside = input('Enter the side you want to play on (top, bottom, left, right): ').lower()

        if blacksside == 'bottom':
            self.colours = Rotate180(self.colours)
        elif blacksside == 'right':
            self.colours = LeftRotate90(self.colours)
        elif blacksside == 'left':
            self.colours = RightRotate90(self.colours)

        board = []
        for rows in range(8):
            row = []
            for col in range(8):
                row.append({'colour' : self.colours[rows][col], 'piece': None})
            board.append(row)
        for col in range(8):
            board[0][col]['piece'] = self.pieces['B'][col]
            board[7][col]['piece'] = self.pieces['W'][col]
        self.boardlayout = board   
        self.legal_moves = []
        self.camps = {'W' : [], 'B' : []}

    def create_pieces(self):
        for col in range(8):
            self.pieces['W'].append(Piece('W',f'W{col}' ))
            self.pieces['B'].append(Piece('B', f'B{col}'))

    def apply_move(self, player, piece_label, coordinates):
        camp = False

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
            
        if coordinates == 'CAMP':
            camp = True
            move = ('camp')
        else:
            try:
                col = ord(coordinates[0]) - ord('A')
                row = 8 - int(coordinates[1])
            except:
                return False, 'Coordinates must be like E2 or camp', ''
            
            if len(coordinates) != 2 or not coordinates[0].isalpha() or not coordinates[1].isdigit():
                return False, 'Coordinates must be like E2 or camp', ''
            
            if not (0 <= col <= 7 and 0 <= row <= 7):
                return False, 'Coordinates out of bounds', ''
            
            move = (row, col)

        if not piece_to_move:
            return False, 'No piece found with that label', ''
        

        legal = self.get_legal_moves(player)


        if (piece_to_move.label, move) not in legal:
            return False, 'That move is not legal', ''
        
        captured_piece = None

        if self.boardlayout[row][col]['piece']:
            if self.boardlayout[row][col]['piece'].player != piece_to_move.player:
                captured_piece = self.boardlayout[row][col]['piece']

        record = MoveRecord(piece_to_move, (old_row, old_col), (row, col), captured_piece, camp)

        self.boardlayout[old_row][old_col]['piece'] = None
        if not camp:
            self.boardlayout[row][col]['piece'] = piece_to_move
        else:
            self.camps[player].append(piece_to_move)
        legal = []
        return True, '', record

    def undo_move(self, record):
    
        if record.was_camped:
            self.camps[record.piece.player].remove(record.piece)    
        else:
            (row, col) = record.dest
            self.boardlayout[row][col]['piece'] = record.captured_piece

        (new_row, new_col) = record.src
        self.boardlayout[new_row][new_col]['piece'] = record.piece




    def get_legal_moves(self, player):
        legal_moves = []
        for r in range(len(self.boardlayout)):
            for c in range(len(self.boardlayout[r])):
                if self.boardlayout[r][c]['piece'] and self.boardlayout[r][c]['piece'].player == player:
                    if self.boardlayout[r][c]['colour'] == 'R':
                        legal_moves.extend(self.rook_moves(r,c))   
                    elif self.boardlayout[r][c]['colour'] == 'B':
                        legal_moves.extend(self.king_moves(r,c))   
                    elif self.boardlayout[r][c]['colour'] == 'G':
                        legal_moves.extend(self.knight_moves(r,c))   
                    elif self.boardlayout[r][c]['colour'] == 'Y':
                        legal_moves.extend(self.bishop_moves(r,c))
                    if r == 0 and player == 'W':
                        legal_moves.append((self.boardlayout[r][c]['piece'].label, 'camp'))   
                    elif r == 7 and player == 'B':
                        legal_moves.append((self.boardlayout[r][c]['piece'].label, 'camp'))  
        return legal_moves


    def rook_moves(self, row, col):
        legal_moves = []

        piece = self.boardlayout[row][col]['piece']
        for c in range(col-1, -1, -1):
            if self.boardlayout[row][c]['piece']:
                if self.boardlayout[row][c]['piece'].player == self.boardlayout[row][col]['piece'].player:
                    break
            legal_moves.append((piece.label, (row, c)))
            if self.boardlayout[row][c]['colour'] == 'R':
                break
        for c in range(col+1, 8):
            if self.boardlayout[row][c]['piece']:
                if self.boardlayout[row][c]['piece'].player == self.boardlayout[row][col]['piece'].player:
                    break
            legal_moves.append((piece.label, (row, c)))
            if self.boardlayout[row][c]['colour'] == 'R':
                break
        for r in range(row-1, -1, -1):
            if self.boardlayout[r][col]['piece']:
                if self.boardlayout[r][col]['piece'].player == self.boardlayout[row][col]['piece'].player:
                    break
            legal_moves.append((piece.label, (r, col)))
            if self.boardlayout[r][col]['colour'] == 'R':
                break
        for r in range(row+1, 8):
            if self.boardlayout[r][col]['piece']:
                if self.boardlayout[r][col]['piece'].player == self.boardlayout[row][col]['piece'].player:
                    break
            legal_moves.append((piece.label, (r, col)))
            if self.boardlayout[r][col]['colour'] == 'R':
                break
        return legal_moves
            
        


    def knight_moves(self, row, col):
        legal_moves = []
        all_moves = [(row +2, col-1), (row+2, col+1), (row+1, col-2), (row+1, col+2), (row-1, col-2), (row-1, col+2), (row-2, col-1), (row-2, col+1)]
        piece = self.boardlayout[row][col]['piece']
        for move in all_moves:
            if 0 <= move[0] <= 7 and 0 <= move[1] <= 7:
                if self.boardlayout[move[0]][move[1]]['piece']:
                    if piece.player != self.boardlayout[move[0]][move[1]]['piece'].player:
                        legal_moves.append((piece.label, (move)))
                else:
                    legal_moves.append((piece.label, (move)))
        return legal_moves

    def bishop_moves(self, row, col):
        piece = self.boardlayout[row][col]['piece']
        legal_moves = []
        
        #upright
        i = 1
        while row - i >= 0 and col + i <= 7:
            if self.boardlayout[row - i][col + i]['piece']:
                if self.boardlayout[row - i][col + i]['piece'].player == piece.player:
                    break
            legal_moves.append((piece.label, (row - i, col + i)))
            if self.boardlayout[row - i][col + i]['colour'] == 'Y':
                break
            i += 1

        #downright
        i = 1
        while row + i <= 7 and col + i <= 7:
            if self.boardlayout[row + i][col + i]['piece']:
                if self.boardlayout[row + i][col + i]['piece'].player == piece.player:
                    break
            legal_moves.append((piece.label, (row + i, col + i)))
            if self.boardlayout[row + i][col + i]['colour'] == 'Y':
                break
            i += 1

        #downleft
        i = 1
        while row + i <= 7 and col - i >= 0:
            if self.boardlayout[row + i][col - i]['piece']:
                if self.boardlayout[row + i][col - i]['piece'].player == piece.player:
                    break
            legal_moves.append((piece.label, (row + i, col - i)))
            if self.boardlayout[row + i][col - i]['colour'] == 'Y':
                break
            i += 1

        #upleft
        i = 1
        while row - i >= 0 and col - i >= 0:
            if self.boardlayout[row - i][col - i]['piece']:
                if self.boardlayout[row - i][col - i]['piece'].player == piece.player:
                    break
            legal_moves.append((piece.label, (row - i, col - i)))
            if self.boardlayout[row - i][col - i]['colour'] == 'Y':
                break
            i += 1

        return legal_moves

    
            



    def king_moves(self, row, col):
        legal_moves = []

        all_moves = [(row +1, col-1), (row+1, col+1), (row+1, col), (row, col+1), (row, col-1), (row-1, col+1), (row-1, col-1), (row-1, col)]
        piece = self.boardlayout[row][col]['piece']
        for move in all_moves:
            if 0 <= move[0] <= 7 and 0 <= move[1] <= 7:
                if self.boardlayout[move[0]][move[1]]['piece']:
                    if piece.player != self.boardlayout[move[0]][move[1]]['piece'].player:
                        legal_moves.append((piece.label, (move)))
                else:
                    legal_moves.append((piece.label, (move)))
        return legal_moves
        
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
        if len(self.camps['W']) == 2:
            print('White has won')
            return True
        elif len(self.camps['B']) == 2:
            print('Black has won')
            return True
        if len(b_pieces) < 2 or len(w_pieces) <2:
            print()
            return True
        

                
    
    def printGrid(self):
        print("    A   B   C   D   E   F   G   H")
        print("  +---+---+---+---+---+---+---+---+")
        for row_num, row in enumerate(self.boardlayout):
            row_str = f'{8-row_num} |'
            for square in row:
                if square['piece']:
                    piece = square['piece'].label
                    row_str += f"{square['colour']}{piece}|"
                else:
                    row_str += f" {square['colour']} |"
                
            print(row_str + f" {8 - row_num}")
            print("  +---+---+---+---+---+---+---+---+")
        print("    A   B   C   D   E   F   G   H")

    def randomlayout(self):
        with open('Tiles.txt') as f:
            grids = f.readlines()
            grids = [grid.strip('\n') for grid in grids]

        x = []

        for i in range(1, 8, 2):
            x.append(random.randint(i-1,i))
        grids_to_use = [grids[y] for y in x] 

        for grid in grids_to_use:
            move = random.randint(1,4)
            if move == 1:
                grid = RightRotate90(grid)
            elif move == 2:
                grid = LeftRotate90(grid)
            elif move == 3:
                grid = Rotate180(grid)
            #if move is 4 then the grid isn't rotated so nothing happens

        random.shuffle(grids_to_use)

        chunked_grids = []
        for grid in grids_to_use:
            chunks = [grid[i:i+4] for i in range(0,15,4)]
            chunked_grids.append(chunks)

        final_grid = []

        for i in range(8):
            if i < 4:
                final_grid.append(str(chunked_grids[0][i]) + str(chunked_grids[1][i]))
            else:
                final_grid.append(str(chunked_grids[2][i-4]) + str(chunked_grids[3][i-4]))

        for i in range(8):
            final_grid[i] = list(final_grid[i])

        return final_grid
    

def RightRotate90(grid):
    return [list(reversed(col)) for col in zip(*grid)]

def LeftRotate90(grid):
    return [list(row) for row in zip(*grid)][::-1]
    
def Rotate180(grid):
    return  [row[::-1] for row in grid[::-1]]




