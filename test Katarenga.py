import unittest
from board import MoveRecord, Board, Piece

def empty_board():
    b = Board()
    for r in range(8):
        for c in range(8):
            b.boardlayout[r][c]['piece'] = None
    return b 

def board_str(b):
    bstring = []
    for r in range (8):
        for c in range(8):
            square = b.colors[r][c]+ str(b.boardlayout[r][c]['piece'])
            bstring.append(square)
    bstring.append(f"Wc:{len(b.camps['W'])}")
    bstring.append(f"Wb:{len(b.camps['B'])}")

    return '|'.join(bstring)

class TestSetup(unittest.TestCase):

    def test_count_pieces(self):
        b = Board()
        
        for player, r in [('B',0), ('W', 7)]:
            for c in range(8):
                piece = b.boardlayout[r][c]['piece']
                self.assertIsNotNone(piece)
                self.assertEqual(piece.player, player)
        for r in range(1,7):
            for c in range(8):
                self.assertIsNone(b.boardlayout[r][c]['piece'])
    
    def test_no_first_turn_captures(self):
        for _ in range(50):
            b = Board()
            for c in range(8):
                self.assertFalse(b.colors[0][c] == 'R' and b.colors[7][c] == 'R')
                self.assertFalse(b.colors[0][0] == 'Y' and b.colors[7][7] == 'Y')
                self.assertFalse(b.colors[0][7] == 'Y' and b.colors[7][0] == 'Y')

class TestLegalMoves(unittest.TestCase):
    
    def test_friendly_captures(self):
        b = Board()
        for player in ['W', 'B']:
            legal_moves = b.get_legal_moves(player)
            for src, dst in legal_moves:
                r,c = dst
                if b.boardlayout[r][c]['piece']:
                    self.assertNotEqual(b.boardlayout[r][c]['piece'].player, player)


    def test_camp_only_from_backrank(self):
        b = empty_board()
        b.boardlayout[0][3]['piece'] = Piece('W', 'T1')
        b.boardlayout[7][3]['piece'] = Piece('B', 'T2')
        dst_list = []
        for player in ['W', 'B']:
            legal_moves = b.get_legal_moves(player)
            for src, dst in legal_moves:
                dst_list.append(dst)
        count = 0
        for dst in dst_list:
            if dst == 'camp':
                count+=1
        self.assertEqual(count, 2)

        b = empty_board()
        b.boardlayout[1][4]['piece'] = Piece('W', 'T1')
        b.boardlayout[5][3]['piece'] = Piece('B', 'T2')
        dst_list = []
        for player in ['W', 'B']:
            legal_moves = b.get_legal_moves(player)
            for src, dst in legal_moves:
                dst_list.append(dst)
        count = 0
        for dst in dst_list:
            if dst == 'camp':
                count+=1
        self.assertEqual(count, 0)

class TestApplyAndUnodMove(unittest.TestCase):
    def test_move_and_undo(self):
        b = Board()
        for player in ['W', 'B']:
            legal_moves = b.get_legal_moves(player)
            for src, dst in legal_moves:
                if dst == 'camp': 
                    continue
                else:
                    before = board_str(b)
                    ok, err, record = b.apply_move(player, src, dst)
                    self.assertTrue(ok)
                    self.assertIsNone(b.boardlayout[src[0]][src[1]]['piece'])
                    after = board_str(b)
                    self.assertNotEqual(before, after)
                    b.undo_move(record)
                    after = board_str(b)
                    self.assertEqual(after, before)
    def test_camp_and_undo(self):
        b = empty_board()
        b.boardlayout[0][3]['piece'] = Piece('W', 'T1')
        b.boardlayout[7][3]['piece'] = Piece('B', 'T2')
        for player, src  in [('W', (0,3)),  ('B', (7,3))]:
            before = board_str(b)
            ok, err, record = b.apply_move(player, src, 'camp')
            self.assertTrue(ok)
            self.assertIsNone(b.boardlayout[src[0]][src[1]]['piece'])
            after = board_str(b)
            self.assertNotEqual(before, after)
            b.undo_move(record)
            after = board_str(b)
            self.assertEqual(after, before)

    def test_illegal_move(self):
        b = Board()
        ok, err, record = b.apply_move('W', (7,0), (3,3))
        self.assertFalse(ok)

class TestGameOver(unittest.TestCase):

    def test_two_camp_win(self):
        b = Board()
        b.camps['W'] = [Piece('W', 'T1'), Piece('W', 'T2')]
        over, winner, reason = b.isOver()
        self.assertTrue(over)
        self.assertEqual(winner, 'White')
    
    def test_insufficient_material(self):
        for player in ['W', 'B']:
            b = Board()
            for r in range(8):
                for c in range(8):
                    if b.boardlayout[r][c]['piece']:
                        if b.boardlayout[r][c]['piece'].player == player:
                            b.boardlayout[r][c]['piece'] = None
            opponent = 'Black' if player == 'W' else 'White'
            over, winner, reason = b.isOver()
            self.assertTrue(over)
            self.assertEqual(winner, opponent)
    
unittest.main()