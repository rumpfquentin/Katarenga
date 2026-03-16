from board import Board, Piece, MoveRecord
import time
import math
import random 
INF = 1e10 
'''not using math.inf as a winning position should consider the depth at which it occurs to insure ai plays first winning move.
math.inf+depth = math.inf and hence I use a large integer instead
'''
ROOK_DIRS   = [(-1,0),(1,0),(0,-1),(0,1)]
BISHOP_DIRS = [(-1,-1),(-1,1),(1,-1),(1,1)]
class AI_Player:

    def order_moves(self, board, current_player, current_player_moves, current_opponent_moves, depth):
        '''a function that orders the legal moves a player can make in order of importance

        args: 
        board (dict)
        current_player (str)
        current_player_moves (list)
        current_opponents_moves (list)
        depth (int) the depth of the Minimax function 

        
        ret: returns the list of sorted legal moves in descending order.
        '''
        target = 'W' if current_player == 'B' else 'B'
        def score_move(move):
            src, dst = move
            score = 0 
            #Critical
            if dst == 'camp':
                if len(board.camps[current_player]) == 1:
                    score += 1_000_000
                #Medium Impact:
                else:
                    score += 50_000
                return score

            #High Impact
            if board.boardlayout[dst[0]][dst[1]]['piece']:
                if board.boardlayout[dst[0]][dst[1]]['piece'].player == target:
                    score += (5000 * (depth))
                    ''' Depth acts as a scale factor so early on in the tree captures are explored sooner while later 
                    progress to camps outweighs captures.
                    '''
            
            #progress towards camps
            if current_player == 'W': 
                score += 1_000 * (src[0] - dst[0])
            else:
                score += 1_000 * (dst[0] - src[0])
            
            #moving a threatened piece to a save square
            enemydsts = []
            for enemysrc, enemydst in current_opponent_moves:
                enemydsts.append(enemydst)
            if src in enemydsts and dst not in enemydsts:
                score += 5_000
            

            if board.colours[dst[0]][dst[1]] in ['R', 'Y']:
                score += 2_000

            return score

        return sorted(current_player_moves, key= score_move, reverse=True)



    def evaluate(self, Board, root_player, current_player_moves, current_opponent_moves, current_player, depth): 
        opponent = 'B' if root_player == 'W' else 'W'
        #root_player is the player that the find_best_move() function was called from, this will differ from the player who we want to evaluate at a minimzing node
        #therefore a check is implemented so that we always evaluate the correct player's position
        if root_player == current_player:
            player_legal_moves = current_player_moves
            opponent_legal_moves = current_opponent_moves
        else:
            player_legal_moves = current_opponent_moves
            opponent_legal_moves = current_player_moves

        open_lines_player, count_pieces_player, two_best_distances_player = self.Board_Iterations(Board, root_player) 
        open_lines_opponent, count_pieces_opponent, two_best_distances_opponent = self.Board_Iterations(Board, opponent) 

        #if the game can be won by either side on the next move then the evaluation returned is positive or negative infinity 

        if len(Board.camps[root_player])>= 2 or (count_pieces_opponent) + len(Board.camps[opponent])  < 2: 
            return  (INF + depth)
        if len(Board.camps[opponent]) >= 2 or (count_pieces_player) + len(Board.camps[root_player]) < 2:
            return  (-INF - depth)
        
        #differnet attributes of a position that the evaluate function compares, important here is that it's a zero-sum game so one person's loss is the other's gain

        C = (len(Board.camps[root_player]) - len(Board.camps[opponent]))

        D = two_best_distances_opponent - two_best_distances_player

        M = len(player_legal_moves) - len(opponent_legal_moves)

        P = count_pieces_player - count_pieces_opponent

        S = self.safe_pieces(Board, root_player, opponent_legal_moves) - self.safe_pieces(Board, opponent, player_legal_moves)

        O = open_lines_player - open_lines_opponent


        wC = 5000

        wD = 120

        wM = 20

        wP = 400

        wS = 100

        wO = 55


        return (wC * C
                + wD * D
                + wM * M
                + wP * P
                + wS * S
                + wO * O)

    #all of the board iterations have been lumped together to increase efficiency
    def Board_Iterations(self, Board, player):
        open_lines = 0
        count = 0
        distances = []
        for r in range(8):
            for c in range(8):
                # The code below counts the two best distances that a player has
                piece = Board.boardlayout[r][c]['piece']
                if  piece is None or piece.player != player:
                    continue
                count +=1
                if player == 'W':
                    distances.append(r)
                else:
                    distances.append(7-r)
                #using the pre-defined directions the code below checks for open lines
                colour = Board.boardlayout[r][c]['colour']
                if colour == 'R':
                    dirs = ROOK_DIRS
                elif colour == 'Y':
                    dirs = BISHOP_DIRS
                else:
                    continue
                
                for dr, dc in dirs:

                    rr = dr + r #this offsets the starting row by the row we are currently on
                    cc = dc +c #this offsets the strating column by the column we are currently on
                    blocked = False
                    while rr < 8 and rr > -1 and cc <8 and cc> -1 and not blocked:

                        if Board.boardlayout[rr][cc]['piece']:
                            blocked = True
                            break

                        if Board.boardlayout[rr][cc]['colour'] == colour:
                            break

                        rr += dr #this increments the row by one unit of the row direction
                        cc += dc #this increments the column by one unit of the column direction
                    if not blocked:
                        open_lines+=1

        distances = sorted(distances)
        if len(distances) > 1:
            two_best_distances = distances[0] + distances[1]
        elif len(distances) == 0: 
            two_best_distances = 0
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
            if occ is not None and occ.player != player: #if there is there is an enemy piece that you can take add 1 to your threats
                threats += 1
        return threats               

    def safe_pieces(self,Board, player, opponent_legal_moves): #similar to threats checks how many of your pieces can be taken
        opponent = 'W' if player == 'B' else 'B'
        unsafe = {m[1] for m in opponent_legal_moves if m[1]!="camp"}
        return sum(1 for r in range(8) for c in range(8) if (p:=Board.boardlayout[r][c]['piece']) and p.player==player and (r,c) not in unsafe)

                        
    def MiniMax(self, board, player_to_move,  depth, alpha, beta, root ):
        ''' calculates the best move for the player to move at the current position

        args: 
        board (dict) the game board
        player_to_move (str) the player that is about to move
        depth (int) how many moves to search ahead
        alpha (int) best score maximising player can guarantee
        beta (int) best score the minimising player can guarantee

        ret: The evaluation of the position
        
        '''


        opponent = 'B' if player_to_move == 'W' else 'W'

        player_moves = board.get_legal_moves(player_to_move)
        opponent_moves = board.get_legal_moves(opponent)

        if depth == 0:
            return self.evaluate(board, root, player_moves, opponent_moves, player_to_move, depth)
        over, winner, reason = board.isOver()
        if over:
            return self.evaluate(board,root, player_moves, opponent_moves, player_to_move, depth)
        
        ordered_moves = self.order_moves(board, player_to_move, player_moves, opponent_moves, depth)

        if player_to_move == root:
            maxEval = -INF
            for move in ordered_moves:
                src, coords = move
                ok, err, record = board.apply_move(player_to_move, src, coords)
                assert ok, err
                score = self.MiniMax(board, opponent, depth-1, alpha, beta, root)
                maxEval = max(maxEval, score)
                alpha = max(alpha, score)
                board.undo_move(record)
                if beta <= alpha: #the minimiser already has a branch where he can guarantee a lower score hence the current branch will never be played
                    break
            return maxEval
        else:
            minEval = INF
            for move in ordered_moves:
                src, coords = move
                ok, err, record = board.apply_move(player_to_move, src, coords)
                assert ok, err
                score = self.MiniMax(board, opponent, depth-1, alpha, beta, root)
                minEval = min(minEval, score)
                beta = min(beta, score)
                board.undo_move(record)
                if beta <= alpha: #the maximiser already has a branch where he can guarantee a higher score hence the current branch will never be played.
                    break
            return minEval



    def find_best_move(self,board, player, depth):
        '''finds the best move for a given position
        
        args:
        board (dict) the game board
        player (str) the player trying to find the best move
        depth (int) the number of moves to search ahead

        ret: 
        the best moeve
        
        '''

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

        
