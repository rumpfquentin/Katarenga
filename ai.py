from board import Board, Piece, MoveRecord

ROOK_DIRS   = [(-1,0),(1,0),(0,-1),(0,1)]
BISHOP_DIRS = [(-1,-1),(-1,1),(1,-1),(1,1)]

def evaluate(Board, player):

    opponent = 'B' if player == 'W' else 'W'

    if len(Board.camps[player])>= 2 or count_pieces(Board, opponent) < 2: 
        return  1_000_000
    if len(Board.camps[opponent]) >= 2 or count_pieces(Board, player) < 2:
        return -1_000_000
    
    C = 1000 * (len(Board.camps[player]) - len(Board.camps[opponent]))

    D = two_best_distances(Board, player) - two_best_distances(Board, opponent)

    M = len(Board.get_legal_moves(Board, player)) - len(Board.get_legal_moves(Board, opponent))

    P = count_pieces(Board, player) - count_pieces(Board, opponent)

    T = count_Threats(Board, player) - count_Threats(Board, opponent)

    O = count_open_lines(Board, player) - count_open_lines(Board, opponent)

    Z = Zugzwang(Board, player) = Zugzwang(Board, opponent)

    wD = 50

    wM = 10

    wP = 6

    wT = 4

    wO = 3

    wZ = 2


    return (C
            + wD * D
            + wM * M
            + wP * P
            + wT * T
            + wO * O
            + wZ +Z)

def count_open_lines(Board, player):
    open_lines = 0

    for r in range(8):
        for c in range(8):
            piece = Board.boardlayout[r][c]['piece']
            if not piece and piece.player != player:
                continue

            colour = Board.boardlayout[r][c]['colour']
            if colour == 'R':
                dirs = ROOK_DIRS
            elif colour == 'R':
                dirs = BISHOP_DIRS
            else:
                continue

            for dr, dc in dirs:
                rr = dr + r
                cc = dc +c
                blocked = False
                while rr < 8 and rr > -1 and cc <8 and cc> -1 and not blocked:

                    if Board.boardlayout[rr][cc]['piece']:
                        blocked = True
                        break

                    if Board.boardlayout[rr][cc]['colour'] == colour:
                        break

                    rr += dr
                    cc += dc
                if not blocked:
                    open_lines+=1
                    
    return open_lines



def count_Threats(Board, player):
    threats = 0
    for piece_label, dest in Board.get_legal_moves(player):
        if dest == 'camp':
            continue
        r, c = dest
        occ = Board.boardlayout[r][c]['piece']
        if occ is not None and occ.player != player:
            threats += 1
    return threats               



def safe_pieces(Board, player):
    count = 0

    opponent = 'B' if player == 'W' else 'W'

    legal_moves = Board.get_legal_moves(opponent)
    for r in range(8):
        for c in range(8):
            if Board.boardlayout[r][c]['piece']:
                if Board.boardlayout[r][c]['piece'].player == player:
                    for move in legal_moves:
                        if move[1] == (r,c):
                            count+=1

def Zugzwang(Board, player):
    legal = Board.get_legal_moves(player)
    if len(legal) <= 1:
        return 1
    else:
        return 0



def count_pieces(Board, player):
    count = 0
    for r in range(8):
        for c in range(8):
            if Board.boardlayout[r][c]['piece']:
                if Board.boardlayout[r][c]['piece'].player == player:
                    count+=1

def two_best_distances(Board, player):
    if player == 'W':
        distances = 0
        count = 0
        for r in range(8):
            for c in range(8):
                if Board.boardlayout[r][c]['piece']:
                    if count == 2:
                        return distances
                    if Board.boardlayout[r][c]['piece'].player == player:
                        distances+=r
                        count +=1
    elif player == 'B':
        distances = 0
        count = 0
        for r in range(7,-1,-1):
            for c in range(8):
                if Board.boardlayout[r][c]['piece']:
                    if count == 2:
                        return distances
                    if Board.boardlayout[r][c]['piece'].player == player:
                        distances+= (7-r)
                        count +=1
                    

                
