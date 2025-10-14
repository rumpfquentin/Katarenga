from board import Board, Piece, MoveRecord
import time
import math
import random
INF = math.inf
ROOK_DIRS   = [(-1,0),(1,0),(0,-1),(0,1)]
BISHOP_DIRS = [(-1,-1),(-1,1),(1,-1),(1,1)]
class AI_Player:
    
    def evaluate(self, Board, player): 
        opponent = 'B' if player == 'W' else 'W'
        player_legal_moves = Board.get_legal_moves(player)
        opponent_legal_moves = Board.get_legal_moves(opponent)

        if len(Board.camps[player])>= 2 or self.count_pieces(Board, opponent) < 2: 
            return  INF
        if len(Board.camps[opponent]) >= 2 or self.count_pieces(Board, player) < 2:
            return -INF
        
        C = 1000 * (len(Board.camps[player]) - len(Board.camps[opponent]))

        D = self.two_best_distances(Board, opponent) - self.two_best_distances(Board, player)

        M = len(player_legal_moves) - len(opponent_legal_moves)

        P = self.count_pieces(Board, player) - self.count_pieces(Board, opponent)

        T = self.count_Threats(Board, player, opponent_legal_moves) - self.count_Threats(Board, opponent, player_legal_moves)

        S = self.safe_pieces(Board, player, opponent_legal_moves) - self.safe_pieces(Board, opponent, player_legal_moves)

        O = self.count_open_lines(Board, player) - self.count_open_lines(Board, opponent)

        Z = self.Zugzwang(Board, player) - self.Zugzwang(Board, opponent)



        wD = 50

        wM = 25

        wP = 100

        wT = 10

        wS = 20

        wO = 3

        wZ = 2

        return (C
                + wD * D
                + wM * M
                + wP * P
                + wT * T
                + wS * S
                + wO * O
                + wZ * Z)

    def count_open_lines(self, Board, player):
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



    def count_Threats(self,Board, player, legal_moves):
        threats = 0
        for src, dest in legal_moves:
            if dest == 'camp':
                continue
            r, c = dest
            occ = Board.boardlayout[r][c]['piece']
            if occ is not None and occ.player != player:
                threats += 1
        return threats               

    def safe_pieces(self,Board, player, opponent_legal_moves):
        opponent = 'W' if player == 'B' else 'B'
        unsafe = {m[1] for m in opponent_legal_moves if m[1]!="camp"}
        return sum(1 for r in range(8) for c in range(8) if (p:=Board.boardlayout[r][c]['piece']) and p.player==player and (r,c) not in unsafe)

    def Zugzwang(self,Board, player):
        legal = Board.get_legal_moves(player)
        if len(legal) <= 1:
            return 1
        else:
            return 0



    def count_pieces(self,Board, player):
        count = 0
        for r in range(8):
            for c in range(8):
                if Board.boardlayout[r][c]['piece']:
                    if Board.boardlayout[r][c]['piece'].player == player:
                        count+=1
        return count

    def two_best_distances(self,Board, player):
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
        return 16
                        
    def MiniMax(self, board, player_to_move,  depth, alpha, beta, root ):
        opponent = 'B' if player_to_move == 'W' else 'W'
        if depth == 0:
            return self.evaluate(board, root)
        over, winner = board.isOver()
        if over:
            return self.evaluate(board,root)
        
        if player_to_move == root:
            maxEval = -INF
            for move in board.get_legal_moves(player_to_move):
                src, coords = move
                ok, err, record = board.apply_move(player_to_move, src, coords)
                assert ok, err
                score = self.MiniMax(board, opponent, depth-1, alpha, beta, root)
                maxEval = max(maxEval, score)
                alpha = max(alpha, score)
                board.undo_move(record)
                if beta <= alpha:
                    break
            return maxEval
        else:
            minEval = INF
            for move in board.get_legal_moves(player_to_move):
                src, coords = move
                ok, err, record = board.apply_move(player_to_move, src, coords)
                assert ok, err
                score = self.MiniMax(board, opponent, depth-1, alpha, beta, root)
                minEval = min(minEval, score)
                beta = min(beta, score)
                board.undo_move(record)
                if beta <= alpha:
                    break
            return minEval



    def find_best_move(self,board, player, depth):
        moves = board.get_legal_moves(player)
        best_Move = moves[0]
        opponent = 'B' if player =='W' else 'W'

        
        best_score = -INF

        for move in moves:
            src, coords = move
            ok, err, record = board.apply_move(player, src, coords)
            assert ok, err

            score = self.MiniMax(board, opponent, depth -1, -INF, INF, player)

            board.undo_move(record)
            if score > best_score:         
                best_score = score
                best_Move = (src, coords)

        return best_Move

        
