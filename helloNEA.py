Whitestack = []
Blackstack = []
piece_objects = []
with open("Puzzles.txt.rtf") as file:
    puzzles = (file.readlines())
with open("Pieces.txt") as file:
    pieces = (file.readlines())
class Event:
    def __init__(self):
        pass
class Piece:
    def __init__(self, ID):
        self.shape = [ch for ch in ID if ch.upper() in ('X', '1')]
        self.type = ID[1]
class Puzzle:
    def __init__(self, ID):
        self.shape = [ch.upper() for ch in ID if ch.upper() in ("0", "X")]
        self.type = ID[1]


for puzzleID in puzzles:
    print(puzzleID)
    puzzle = Puzzle(puzzleID)
    if puzzle.type == "W":
        Whitestack.append(puzzle)
    elif puzzle.type == "B":
        Blackstack.append(puzzle)
for pid in pieces:
    piece_objects.append(Piece(pid))

[print(puzzle.shape) for puzzle in Whitestack]
[print(piece.shape) for piece in piece_objects]