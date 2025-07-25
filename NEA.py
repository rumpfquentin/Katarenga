import random

class Piece:
    def __init__(self, player,x,y):
        self.player = player
        self.posx = x
        self.posy = y
    def movepiece():
        pass
class Board:
    def __init__(self):
        self.layout = []
    def randomlayout(self):
        with open('Tiles.txt') as f:
            x = f.readlines().strip()
            for i in range(4):
                x.pop(random.randint(1,8))
        

