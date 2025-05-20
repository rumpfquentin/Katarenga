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
        self.shape = [ch for ch in ID if ch.upper() in ('█', '1')]
        self.type = ID[1]
class Puzzle:
    def __init__(self, ID):
        self.shape = [ch.upper() for ch in ID if ch.upper() in ("░", "█")]
        self.type = ID[1]

    def printShape(self):
        outstr = ''
        for i in range(len(self.shape)):
            outstr += self.shape[i]
            if i%5==4:
                outstr += '\n'
        return outstr
        
'''
    @property
    def shape(self):
        outstr = ''
        for i in range(len(self.shape)):
            outstr += self.shape[i]
            if i%5==4:
                outstr += '\n'
        return outstr      
       
    @shape.setter
    def shape(self, s):
        self.shape = s   
'''

for puzzleID in puzzles:
    print(puzzleID)
    puzzle = Puzzle(puzzleID)
    if puzzle.type == "W":
        Whitestack.append(puzzle)
    elif puzzle.type == "B":
        Blackstack.append(puzzle)
for pid in pieces:
    piece_objects.append(Piece(pid))

[print(puzzle.printShape()) for puzzle in Whitestack]
[print(piece.shape) for piece in piece_objects]
