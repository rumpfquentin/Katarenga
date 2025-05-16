Whitestack = []
Blackstack = []

with open("Puzzles.txt.rtf") as file:
    puzzles = (file.readlines())

class Event:
    def __init__(self):
        pass
class
class Puzzle:
    def __init__(self, ID):
        self.shape = [chr.upper() for chr in ID if chr.upper() in ("0", "X")]
        self.type = ID[1]


for puzzleID in puzzles:
    print(puzzleID)
    puzzle = Puzzle(puzzleID)
    if puzzle.type == "W":
        Whitestack.append(puzzle)
    elif puzzle.type == "B":
        Blackstack.append(puzzle)

[print(puzzle.shape) for puzzle in Whitestack]
    
