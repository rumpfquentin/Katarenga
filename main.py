from dataclasses import dataclass
from typing import Union
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, ListProperty, NumericProperty, ColorProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics import Rectangle
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.metrics import dp
from kivy.uix.image import Image


from board import Board, Piece, MoveRecord
from ai import AI_Player




@dataclass
class Move:
    src: tuple
    dst: Union[tuple, str]

class Cell(Button, RecycleDataViewBehavior):
    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)
        self._rect = None 
        self.cell_image_source = 'assets/Blue_Square.png'
        self.background_color = 0,0,0,0
        self.white_piece_image_source = 'assets/white_pawn.png'
        self.black_piece_image_source = 'assets/black_pawn.png'
        self.piece_rect = None
        self.bind(size = self.sync_pieces, pos = self.sync_pieces)

    def refresh_view_attrs(self, rv, index, data):
        ret = super().refresh_view_attrs(rv, index, data)
        self._rv = rv

        self.cell_index = index
        self.cell_text = data.get('text', '')
        self.cell_image_source = data.get('cell_image_source', 'assets/Blue_Square.png')
        self.background_normal = self.cell_image_source
        self.background_down = self.cell_image_source
        self.background_disabled_normal = self.cell_image_source
        self.background_disabled_down = self.cell_image_source
        self.background_color = (1, 1, 1, 1)
        self.border = (0, 0, 0, 0)

        self.piece = data.get('piece')
        Clock.create_trigger(lambda dt: self.update_piece(), -1)()
        return ret
    
    def sync_pieces(self, *args):
        if self.piece_rect:
            self.piece_rect.pos = self.pos
            self.piece_rect.size = self.size

    def update_piece(self):
        if self.piece is None:
            if self.piece_rect:
                self.canvas.after.remove(self.piece_rect)
                self.piece_rect = None
            return
        if self.piece.player == 'B':
            piece_image_source = self.black_piece_image_source
        elif self.piece.player == "W":
            piece_image_source = self.white_piece_image_source
        if self.piece != None:
            if not self.piece_rect: 
                with self.canvas.after:
                    self.piece_rect = Rectangle(
                        size = self.size,
                        pos = self.pos ,
                        source = piece_image_source
                        )
            else:
                self.piece_rect.source = piece_image_source
                self.piece_rect.pos = self.pos
                self.piece_rect.size = self.size



    def on_release(self):
        r, c = divmod(self.cell_index, 8)
        parent = self.parent
        while parent and not isinstance(parent, BoardView):
            parent = parent.parent
        if parent:
            parent.on_cell_tap(r, c)
    

class GameState:

    def __init__(self):
        self.players = ['human', 'ai']
        self.b = Board()
        self.ai = AI_Player()
        self.current_idx = 0
        self.phase = ""

    def end_move(self):
        self.current_idx = (self.current_idx + 1) % len(self.players)
        self.phase = "awaiting input"

        if self.current_player == 'ai':
            return 'ai'

    def ai_move(self):
        move = self.ai.find_best_move(self.b, 'B', 3)
        move = Move(src=move[0], dst= move[1]) 
        return move


    def start_move(self):
        self.phase = "awaiting input"

    @property
    def current_player(self):
        return self.players[self.current_idx]


    def events_apply_move(self, move):
        if self.current_player == 'human':
            player_color = 'W'
        elif self.current_player == 'ai':
            player_color = 'B'
        ok, err, record = self.b.apply_move(player_color, move.src, move.dst)
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
    selected = ObjectProperty(allownone = True)

    def on_kv_post(self, _):
        self.gs = GameState()
        self.gs.start_move()
        self.status = f"Turn: {self.gs.current_player}"
        Clock.schedule_once(self._tighten, 0)
        self.refresh_board()

    def _tighten(self, *_):
        rv = self.ids.rv
        lm = rv.layout_manager
        rv.size = (lm.minimum_width, lm.minimum_height)

    def refresh_board(self):
        cells = []
        for r in range(8):
            for c in range(8):
                background_color = self.gs.b.colours[r][c]
                piece =  self.gs.b.boardlayout[r][c]["piece"]

                if background_color == 'Y':
                    cell_image_source = 'assets/Yellow_Square.png'
                elif background_color == 'R':
                    cell_image_source = 'assets/Red_Square.png'
                elif background_color == 'G':
                    cell_image_source = 'assets/Green_Square.png'
                elif background_color == 'B':
                    cell_image_source = 'assets/Blue_Square.png'
                idx = r * 8 + c
                cells.append({
                    "text": "",
                    "index": idx,
                    "cell_image_source": cell_image_source,
                    "piece": piece
                })
        self.ids.rv.data = cells
        self.ids.rv.refresh_from_data()

    def on_ai_move(self,dt):
        move = self.gs.ai_move()
        self.gs.events_apply_move(move)
        self.refresh_board()
        self.gs.end_move()


    def on_human_move(self, r,c, player_color):
        
        if self.selected is None:
            if self.is_own_piece(r,c, player_color):
                self.selected = (r,c)
                self.status = 'selected'
            return 
        
        if (self.selected,(r,c)) in self.gs.b.get_legal_moves(player_color):
            move = Move(src = self.selected, dst=(r,c))
            events = self.gs.events_apply_move(move)
            self.refresh_board()
            self.gs.end_move()
            Clock.schedule_once(self.on_ai_move, 0)
            return 
        
        if self.is_own_piece(r,c, player_color):
            self.selected = (r,c)
            return 
        self.selected = None
        
        
    def on_cell_tap(self, r, c):
        if self.gs.current_player == 'human':
            player_color = 'W'
            self.on_human_move(r,c,player_color)
        elif self.gs.current_player == 'ai':
            print('ai is thinking')
            return 

        

    def is_own_piece(self, r, c, player_color):
        if self.gs.b.boardlayout[r][c]['piece']:
            if player_color == self.gs.b.boardlayout[r][c]['piece'].player:
                return True
        return False



class KatarengaApp(App):
    title = "Katarenga"
    def build(self):
        return Builder.load_file("katarenga.kv")
    def start_game(self, *args):
        print("starting...")


if __name__ == "__main__":
    KatarengaApp().run()