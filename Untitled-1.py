
move = ('x', (1,6))
piece_label, coords = move
row, col = coords
col = chr(col + ord('A'))
print(col)