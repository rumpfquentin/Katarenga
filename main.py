from board import Board, Piece, MoveRecord
import ai
import kivy

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ListProperty, ObjectProperty, StringProperty
)
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from dataclasses import dataclass

@dataclass
class Move:
    src: tuple
    dst: tuple | str




class GameState:


    def __init__(self):
        self.players = ['human', 'ai']
        self.board = Board()
        self.current_idx = 0
        self.phase = ""
    
    def end_move(self):

        self.current_idx = (self.current_idx +1) % len(self.players)
        self.phase = "awaiting input"

    def start_move(self):
        pass

    @property
    def current_player(self):
        return self.players[self.current_idx]

    def get_legal_moves(self):

        return self.board.get_legal_moves(self.current_player)

    def events_apply_move(self, move):

        ok, err, record = self.board.apply_move(move)
        events = []
        if ok:
            events.append({"type": 'move', "from": move.src, 'to': move.dst})
            if record.captured_piece != None:
                events.append({"type": 'capture', 'at': move.dst})
        else:
            events.append({"type": "error", "message": err})
        return events

class BoardView(BoxLayout):
    

    status = StringProperty()
    gs = ObjectProperty(allownone = True)
    highlights = ListProperty([])

    def on_kv_post(self, base_widget):
        gs = GameState()
        gs.start_move()
    

class KatarengaApp(App):
    title = 'Katarenga'

    def build(self):
        return BoardView()
    
    def start_game(self):
        print('starting...')

if __name__ == "__main__":
    KatarengaApp().run()



        





        

