from board import Board, Piece, MoveRecord
import ai
B = Board()
B.randomlayout()
B.printGrid()
while True:
    while True:
        ok, err, record = B.apply_move('W',input('Enter the label of the piece you want to move (e.g. W0): ').strip(), input('Enter the coordinates of where you want to move the piece (e.g. E2): ').strip().upper())
        if not ok:
            print(err)
            continue
        break
    B.printGrid()
    if B.isOver():
        break
    print('AI is thinking')
    ai_Move = ai.find_best_move(B, 'B', 3)
    piece_label, coords = ai_Move
    if coords != 'camp':
        row, col = coords
        col = chr(col + ord('A'))
        row = 8 - row
        coordinates = col + str(row)
    else: 
        coordinates = 'camp'
    ok, err, record = B.apply_move('B', piece_label, coordinates)
    assert ok, err
    B.printGrid()
    if B.isOver():
        break


