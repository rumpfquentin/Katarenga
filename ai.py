from board import Board, Piece, MoveRecord

INF = 10**12
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

    M = len(Board.get_legal_moves(player)) - len(Board.get_legal_moves(opponent))

    P = count_pieces(Board, player) - count_pieces(Board, opponent)

    T = count_Threats(Board, player) - count_Threats(Board, opponent)

    S = safe_pieces(Board, player) - safe_pieces(Board, opponent)

    O = count_open_lines(Board, player) - count_open_lines(Board, opponent)

    Z = Zugzwang(Board, player) - Zugzwang(Board, opponent)

    wD = 50

    wM = 10

    wP = 6

    wT = 4

    wS = 3

    wO = 3

    wZ = 2


    return (C
            + wD * D
            + wM * M
            + wP * P
            + wT * T
            + wS * S
            + wO * O
            + wZ +Z)

def count_open_lines(Board, player):
    open_lines = 0

    for r in range(8):
        for c in range(8):
            piece = Board.boardlayout[r][c]['piece']
            if  piece is None or piece.player != player:
                continue

            colour = Board.boardlayout[r][c]['colour']
            if colour == 'R':
                dirs = ROOK_DIRS
            elif colour == 'Y':
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
    return count

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
    return count

def two_best_distances(Board, player):
    if player == 'W':
        distances = 0
        count = 0
        for r in range(8):
            for c in range(8):
                if Board.boardlayout[r][c]['piece']:
                    if Board.boardlayout[r][c]['piece'].player == player:
                        distances+=r
                        count +=1
                    if count == 2:
                        return distances
    elif player == 'B':
        distances = 0
        count = 0
        for r in range(7,-1,-1):
            for c in range(8):
                if Board.boardlayout[r][c]['piece']:
                    if Board.boardlayout[r][c]['piece'].player == player:
                        distances+= (7-r)
                        count +=1
                    if count == 2:
                        return distances
                    
def MiniMax(board, player,  depth, alpha, beta ):
    opponent = 'B' if player == 'W' else 'W'
    if depth == 0 or board.isOver():
        return evaluate(board, player)
    
    if player == 'W':
        maxEval = -INF
        for move in board.get_legal_moves(player):
            piece_label, coords = move
            if coords != 'camp':
                row, col = coords
                col = chr(col + ord('A'))
                row = 8 - row
                coordinates = col + str(row)
            else: 
                coordinates = 'camp'
            ok, err, record = board.apply_move(player, piece_label, coordinates)
            assert ok, err
            score = MiniMax(board, opponent, depth-1, alpha, beta)
            maxEval = max(maxEval, score)
            alpha = max(alpha, score)
            board.undo_move(record)
            if beta <= alpha:
                break
        return maxEval
    else:
        minEval = INF
        for move in board.get_legal_moves(player):
            piece_label, coords = move
            if coords != 'camp':
                row, col = coords
                col = chr(col + ord('A'))
                row = 8 - row
                coordinates = col + str(row)
            else: 
                coordinates = 'camp'
            ok, err, record = board.apply_move(player, piece_label, coordinates)
            assert ok, err
            score = MiniMax(board, opponent, depth-1, alpha, beta)
            minEval = min(minEval, score)
            beta = min(beta, score)
            board.undo_move(record)
            if beta <= alpha:
                break
        return minEval
    
def find_best_move(board, player, depth):
    best_Move = None
    opponent = 'B' if player =='W' else 'W'

    if player == 'W':
        bestScore = -INF
    else:
        bestScore = INF

    for move in board.get_legal_moves(player):
        piece_label, coords = move
        if coords != 'camp':
                row, col = coords
                col = chr(col + ord('A'))
                row = 8 - row
                coordinates = col + str(row)
        else: 
            coordinates = 'camp'
        ok, err, record = board.apply_move(player, piece_label, coordinates)
        assert ok, err

        score = MiniMax(board, player, depth -1, -INF, INF)

        board.undo_move(record)

        if player == 'W':
            if score > bestScore:
                best_Move = move
                bestScore = score
        elif player == 'B':
            if score < bestScore:
                best_Move = move
                bestScore = score

    return best_Move

    
