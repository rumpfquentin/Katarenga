from board import Board, Piece, MoveRecord
import ai
import kivy

B = Board()
B.randomlayout()
B.printGrid()
gamemode = input('multiplayer or singleplayer?: ').strip().lower()
while True:
    while True:
        piece = input('Enter the coordinates of the piece you want to move: ').strip().lower()
        move = input('Enter the coordinates of where you want to move the piece (e.g. E2): ').strip().lower()
        if move != 'camp':
            col =   ord(move[0])  -ord('a')
            row = 8 - int(move[1])
            move = (row, col)
        old_col =   ord(piece[0])  -ord('a')
        old_row = 8 - int(piece[1])
        piece_pos = (old_row, old_col)
        ok, err, record = B.apply_move('W',piece_pos, move)
        if not ok:
            print(err)
            continue
        break
    B.printGrid()
    over, winner = B.isOver()
    if over:
        print(winner)
        break
    if gamemode == 'singleplayer':
        print('AI is thinking')
        ai_Move = ai.find_best_move(B, 'B', 3)
        piece_label, coords = ai_Move
        ok, err, record = B.apply_move('B', piece_label, coords)
        assert ok, err
        print(f'AI moved {piece_label} to {move}')
        B.printGrid()
        over, winner = B.isOver()
        if over:
            print(winner)
            break
    elif gamemode == 'multiplayer':
        while True:
            piece = input('Enter the coordinates of the piece you want to move: ').strip().lower()
            move = input('Enter the coordinates of where you want to move the piece (e.g. E2): ').strip().lower()
            if move != 'camp':
                col =   ord(move[0])  -ord('a')
                row = 8 - int(move[1])
                move = (row, col)
            old_col =   ord(piece[0])  -ord('a')
            old_row = 8 - int(piece[1])
            piece_pos = (old_row, old_col)
            ok, err, record = B.apply_move('B',piece_pos, move)
            if not ok:
                print(err)
                continue
            break
        B.printGrid()
        over, winner = B.isOver()
        if over:
            print(winner)
            break


