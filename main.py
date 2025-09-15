from dataclasses import dataclass
from typing import Union
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, ListProperty, NumericProperty, ColorProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.recycleview.views import RecycleDataViewBehavior

from board import Board, Piece, MoveRecord
class Board_GUI: 
    def get_legal_moves(self, who): return []
    def apply_move(self, move): return True, None, type("R", (), {"captured_piece": None})()

class Cell(Button, RecycleDataViewBehavior):
    cell_index: NumericProperty
    cell_color: ColorProperty
    cell_image_source: StringProperty
    cell_text: StringProperty

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cell_text = ''

    def refresh_view_attrs(self, rv, index, data):
        self.cell_index = index
        data['text'] = self.cell_text

    
    def on_release(self):
        self.cell_text = '♟'

    
@dataclass
class Move:
    src: tuple
    dst: Union[tuple, str]

class GameState:
    def __init__(self):
        self.players = ['human', 'ai']
        self.board = Board()
        self.current_idx = 0
        self.phase = ""

    def end_move(self):
        self.current_idx = (self.current_idx + 1) % len(self.players)
        self.phase = "awaiting input"

    def start_move(self):
        self.phase = "awaiting input"

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
            if record.captured_piece is not None:
                events.append({"type": 'capture', 'at': move.dst})
        else:
            events.append({"type": "error", "message": err})
        return events

class BoardView(BoxLayout):
    status = StringProperty("")
    gs = ObjectProperty(allownone=True)
    highlights = ListProperty([])

    def on_kv_post(self, _):
        self.gs = GameState()
        self.gs.start_move()
        self.status = f"Turn: {self.gs.current_player}"
        self.refresh_board()
        Clock.schedule_once(self._tighten, 0)

    def _tighten(self, *_):
        rv = self.ids.rv
        lm = rv.layout_manager
        rv.size = (lm.minimum_width, lm.minimum_height)

    def refresh_board(self):
        cells = []
        for r in range(8):
            for c in range(8):
                idx = r * 8 + c
                cells.append({
                    "text": "",
                    "index": idx,
                    "background_color": (0.85, 0.85, 0.85, 1)
                        if (r + c) % 2 == 0 else (0.25, 0.25, 0.25, 1),
                })
        self.ids.rv.data = cells

class KatarengaApp(App):
    title = "Katarenga"
    def build(self):
        return Builder.load_file("katarenga.kv")
    def start_game(self, *args):
        print("starting...")
    def place_piece():
        BoardView.create_piece()
        BoardView.refresh_board()

if __name__ == "__main__":
    KatarengaApp().run()