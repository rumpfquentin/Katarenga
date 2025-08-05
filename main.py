
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
    while True:
        ok, err, record = B.apply_move('B',input('Enter the label of the piece you want to move (e.g. B0): ').strip(), input('Enter the coordinates of where you want to move the piece (e.g. E2): ').strip().upper())
        if not ok:
            print(err)
            continue
        break
    B.printGrid()
    if B.isOver():
        break