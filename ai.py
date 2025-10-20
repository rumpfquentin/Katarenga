from board import Board, Piece, MoveRecord
import time
import math
import random
INF = math.inf
ROOK_DIRS   = [(-1,0),(1,0),(0,-1),(0,1)]
BISHOP_DIRS = [(-1,-1),(-1,1),(1,-1),(1,1)]
class AI_Player:

    def evaluate(self, Board, root_player, current_player_moves, current_opponent_moves, current_player): 
        opponent = 'B' if root_player == 'W' else 'W'

        if root_player == current_player:
            player_legal_moves = current_player_moves
            opponent_legal_moves = current_opponent_moves
        else:
            player_legal_moves = current_opponent_moves
            opponent_legal_moves = current_player_moves

        open_lines_player, count_pieces_player, two_best_distances_player = self.Board_Iterations(Board, root_player) 
        open_lines_opponent, count_pieces_opponent, two_best_distances_opponent = self.Board_Iterations(Board, opponent) 

        if len(Board.camps[root_player])>= 2 or (count_pieces_opponent) + len(Board.camps[opponent])  < 2: 
            return  INF
        if len(Board.camps[opponent]) >= 2 or (count_pieces_player) + len(Board.camps[root_player]) < 2:
            return -INF
        

        C = 1000 * (len(Board.camps[root_player]) - len(Board.camps[opponent]))

        D = two_best_distances_opponent - two_best_distances_player

        M = len(player_legal_moves) - len(opponent_legal_moves)

        P = count_pieces_player - count_pieces_opponent

        T = self.count_Threats(Board, root_player, opponent_legal_moves) - self.count_Threats(Board, opponent, player_legal_moves)

        S = self.safe_pieces(Board, root_player, opponent_legal_moves) - self.safe_pieces(Board, opponent, player_legal_moves)

        O = open_lines_player - open_lines_opponent




        wD = 50

        wM = 25

        wP = 120

        wT = 10

        wS = 200

        wO = 30


        return (C
                + wD * D
                + wM * M
                + wP * P
                + wT * T
                + wS * S
                + wO * O)


    def Board_Iterations(self, Board, player):
        open_lines = 0
        count = 0
        distances = []
        for r in range(8):
            for c in range(8):
                piece = Board.boardlayout[r][c]['piece']
                if  piece is None or piece.player != player:
                    continue
                count +=1
                if player == 'W':
                    distances.append(r)
                else:
                    distances.append(7-r)

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

        distances = sorted(distances)
        if len(distances) > 1:
            two_best_distances = distances[0] + distances[1]
        else: 
            two_best_distances = distances[0]

        return open_lines, count, two_best_distances



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

        player_moves = board.get_legal_moves(player_to_move)
        opponent_moves = board.get_legal_moves(opponent)

        if depth == 0:
            return self.evaluate(board, root, player_moves, opponent_moves, player_to_move)
        over, winner = board.isOver()
        if over:
            return self.evaluate(board,root, player_moves, opponent_moves, player_to_move)
        

        if player_to_move == root:
            maxEval = -INF
            for move in player_moves:
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
            for move in player_moves:
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

        
