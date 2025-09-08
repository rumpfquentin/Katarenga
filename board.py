import random
from dataclasses import dataclass
from typing import Optional, Tuple


class Piece:
    def __init__(self, player, label):
        self.player = player
        self.label = label


@dataclass
class MoveRecord:
    piece: Piece
    src: Tuple[int, int]
    dest: Tuple[int, int]
    captured_piece: Optional[Piece] = None
    was_camped: bool = False


class Board:
    def __init__(self):
        self.pieces = {'W': [], 'B': []}
        self.create_pieces()
        self.colours = self.randomlayout()

        print("    A   B   C   D   E   F   G   H")
        print("  +---+---+---+---+---+---+---+---+")
        for row_num, row in enumerate(self.colours):
            row_str = f'{8 - row_num} |'
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
                row.append({'colour': self.colours[rows][col], 'piece': None})
            board.append(row)

        for col in range(8):
            board[0][col]['piece'] = self.pieces['B'][col]
            board[7][col]['piece'] = self.pieces['W'][col]

        self.boardlayout = board
        self.legal_moves = []
        self.camps = {'W': [], 'B': []}

    def create_pieces(self):
        for col in range(8):
            self.pieces['W'].append(Piece('W', f'W{col}'))
            self.pieces['B'].append(Piece('B', f'B{col}'))

    def apply_move(self, player, old_coors, coordinates):
        camp = False
        old_row, old_col = old_coors
        piece_to_move = self.boardlayout[old_row][old_col]['piece']
            


        if coordinates == 'camp':
            camp = True
            move = 'camp'
        else:
            try:
                row, col = coordinates
            except:
                if len(str(row)) != 1 or len(str(col)) != 1:
                    return False, 'Coordinates must be like E2 or camp', ''

                elif not (0 <= col <= 7 and 0 <= row <= 7):
                    return False, 'Coordinates out of bounds', ''

            move = (row, col)

        if not piece_to_move:
            return False, 'No piece found at that position', ''

        legal = self.get_legal_moves(player)
        if (old_coors, move) not in legal:
            return False, 'That move is not legal', ''

        captured_piece = None
        if not camp and self.boardlayout[row][col]['piece']:
            if self.boardlayout[row][col]['piece'].player != piece_to_move.player:
                captured_piece = self.boardlayout[row][col]['piece']

        if not camp:
            record = MoveRecord(piece_to_move, (old_row, old_col), (row, col), captured_piece, camp)
        else:
            record = MoveRecord(piece_to_move, (old_row, old_col), 'camp', captured_piece, camp)

        self.boardlayout[old_row][old_col]['piece'] = None
        if not camp:
            self.boardlayout[row][col]['piece'] = piece_to_move
        else:
            self.camps[player].append(piece_to_move)

        return True, '', record

    def undo_move(self, record):
        if record.was_camped:
            self.camps[record.piece.player].remove(record.piece)
        else:
            row, col = record.dest
            self.boardlayout[row][col]['piece'] = record.captured_piece

        new_row, new_col = record.src
        self.boardlayout[new_row][new_col]['piece'] = record.piece

    def get_legal_moves(self, player):
        legal_moves = []
        for r in range(len(self.boardlayout)):
            for c in range(len(self.boardlayout[r])):
                square = self.boardlayout[r][c]
                piece = square['piece']
                if piece and piece.player == player:
                    colour = square['colour']
                    if colour == 'R':
                        legal_moves.extend(self.rook_moves(r, c))
                    elif colour == 'B':
                        legal_moves.extend(self.king_moves(r, c))
                    elif colour == 'G':
                        legal_moves.extend(self.knight_moves(r, c))
                    elif colour == 'Y':
                        legal_moves.extend(self.bishop_moves(r, c))

                    if r == 0 and player == 'W':
                        legal_moves.append(((r,c), 'camp'))
                    elif r == 7 and player == 'B':
                        legal_moves.append(((r,c), 'camp'))
        return legal_moves

    def rook_moves(self, row, col):
        legal_moves = []
        piece = self.boardlayout[row][col]['piece']

        # left
        for c in range(col - 1, -1, -1):
            target = self.boardlayout[row][c]
            if target['piece']:
                if target['piece'].player == piece.player:
                    break
                legal_moves.append(((row,col), (row, c)))
                break
            legal_moves.append(((row,col), (row, c)))
            if target['colour'] == 'R':
                break

        # right
        for c in range(col + 1, 8):
            target = self.boardlayout[row][c]
            if target['piece']:
                if target['piece'].player == piece.player:
                    break
                legal_moves.append(((row,col), (row, c)))
                break
            legal_moves.append(((row,col), (row, c)))
            if target['colour'] == 'R':
                break

        # up
        for r in range(row - 1, -1, -1):
            target = self.boardlayout[r][col]
            if target['piece']:
                if target['piece'].player == piece.player:
                    break
                legal_moves.append(((row,col), (r, col)))
                break
            legal_moves.append(((row,col), (r, col)))
            if target['colour'] == 'R':
                break

        # down
        for r in range(row + 1, 8):
            target = self.boardlayout[r][col]
            if target['piece']:
                if target['piece'].player == piece.player:
                    break
                legal_moves.append(((row,col), (r, col)))
                break
            legal_moves.append(((row,col), (r, col)))
            if target['colour'] == 'R':
                break

        return legal_moves

    def knight_moves(self, row, col):
        legal_moves = []
        piece = self.boardlayout[row][col]['piece']
        moves = [
            (row + 2, col - 1), (row + 2, col + 1),
            (row + 1, col - 2), (row + 1, col + 2),
            (row - 1, col - 2), (row - 1, col + 2),
            (row - 2, col - 1), (row - 2, col + 1),
        ]

        for r, c in moves:
            if 0 <= r <= 7 and 0 <= c <= 7:
                target = self.boardlayout[r][c]['piece']
                if target and target.player != piece.player:
                    legal_moves.append(((row,col), (r, c)))
                elif not target:
                    legal_moves.append(((row,col), (r, c)))

        return legal_moves

    def bishop_moves(self, row, col):
        legal_moves = []
        piece = self.boardlayout[row][col]['piece']

        # upright
        i = 1
        while row - i >= 0 and col + i <= 7:
            target = self.boardlayout[row - i][col + i]
            if target['piece']:
                if target['piece'].player == piece.player:
                    break
                legal_moves.append(((row,col), (row - i, col + i)))
                break
            legal_moves.append(((row,col), (row - i, col + i)))
            if target['colour'] == 'Y':
                break
            i += 1

        # downright
        i = 1
        while row + i <= 7 and col + i <= 7:
            target = self.boardlayout[row + i][col + i]
            if target['piece']:
                if target['piece'].player == piece.player:
                    break
                legal_moves.append(((row,col), (row + i, col + i)))
                break
            legal_moves.append(((row,col), (row + i, col + i)))
            if target['colour'] == 'Y':
                break
            i += 1

        # downleft
        i = 1
        while row + i <= 7 and col - i >= 0:
            target = self.boardlayout[row + i][col - i]
            if target['piece']:
                if target['piece'].player == piece.player:
                    break
                legal_moves.append(((row,col), (row + i, col - i)))
                break
            legal_moves.append(((row,col), (row + i, col - i)))
            if target['colour'] == 'Y':
                break
            i += 1

        # upleft
        i = 1
        while row - i >= 0 and col - i >= 0:
            target = self.boardlayout[row - i][col - i]
            if target['piece']:
                if target['piece'].player == piece.player:
                    break
                legal_moves.append(((row,col), (row - i, col - i)))
                break
            legal_moves.append(((row,col), (row - i, col - i)))
            if target['colour'] == 'Y':
                break
            i += 1

        return legal_moves

    def king_moves(self, row, col):
        legal_moves = []
        piece = self.boardlayout[row][col]['piece']
        moves = [
            (row + 1, col - 1), (row + 1, col), (row + 1, col + 1),
            (row, col + 1), (row, col - 1),
            (row - 1, col + 1), (row - 1, col), (row - 1, col - 1),
        ]

        for r, c in moves:
            if 0 <= r <= 7 and 0 <= c <= 7:
                target = self.boardlayout[r][c]['piece']
                if target and target.player != piece.player:
                    legal_moves.append(((row,col), (r, c)))
                elif not target:
                    legal_moves.append(((row,col), (r, c)))

        return legal_moves

    def isOver(self):
        b_pieces = []
        w_pieces = []
        winner = False
        for r in range(8):
            for c in range(8):
                piece = self.boardlayout[r][c]['piece']
                if piece:
                    if piece.player == 'W':
                        w_pieces.append(piece.label)
                    elif piece.player == 'B':
                        b_pieces.append(piece.label)

        if len(self.camps['W']) == 2:
            winner = 'White has won'
            return True, winner
        elif len(self.camps['B']) == 2:
            winner = 'Black has won'
            return True, winner
        if len(b_pieces) < 2:
            winner = 'Black has won'
        elif len(w_pieces) < 2:
            winner = 'Black has won'
            return True, winner
        return False, winner

    def printGrid(self):
        print("    A   B   C   D   E   F   G   H ")
        print("  +---+---+---+---+---+---+---+---+")
        for row_num, row in enumerate(self.boardlayout):
            row_str = f'{8 - row_num} |'
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
            raw_tiles = [line.strip() for line in f]  
        picks = [random.randint(i-1, i) for i in range(1, 8, 2)]
        quarters = [raw_tiles[i] for i in picks]

        grids = []
        for tile in quarters:
            rows = [list(tile[j:j+4]) for j in range(0, 16, 4)]
            rot = random.randint(1, 4)
            if rot == 1:
                rows = RightRotate90(rows)
            elif rot == 2:
                rows = LeftRotate90(rows)
            elif rot == 3:
                rows = Rotate180(rows)
            grids.append(rows)

        random.shuffle(grids)

        final_grid = []
        for i in range(8):
            if i < 4:
                
                combined = grids[0][i] + grids[1][i]
            else:
                
                combined = grids[2][i-4] + grids[3][i-4]
            final_grid.append(combined)

        return final_grid


def RightRotate90(grid):
    return [list(reversed(col)) for col in zip(*grid)]

def LeftRotate90(grid):
    return [list(col) for col in zip(*grid)][::-1]


def Rotate180(grid):
    return [row[::-1] for row in grid[::-1]]
