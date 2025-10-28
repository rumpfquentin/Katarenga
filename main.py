from dataclasses import dataclass
from typing import Union
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, ListProperty, NumericProperty, ColorProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics import Rectangle, Color, Line
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.dropdown import DropDown

from board import Board, Piece, MoveRecord
from ai import AI_Player
import copy
import json

@dataclass
class Move:
    src: tuple
    dst: Union[tuple, str]



class Cell(Button, RecycleDataViewBehavior):
    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)
        self._rect = None 
        self.cell_image_source = 'assets/Brown_Square.png'
        self.background_color = 0,0,0,0
        self.white_piece_image_source = 'assets/white_pawn.png'
        self.black_piece_image_source = 'assets/black_pawn.png'
        self.piece_rect = None
        self.high_rect = None
        self.high_color = None
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

        self.is_highlighted = data.get('highlighted')

        self.piece = data.get('piece')
        Clock.create_trigger(lambda dt: self.update_piece(), -1)()
        Clock.create_trigger(lambda dt: self.update_highlights(), -1)()
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

    def update_highlights(self):
        if self.high_color:
            try:
                self.canvas.after.remove(self.high_color)
            except:
                pass
            self.high_color = None
            
        if self.high_rect:
            try:
                self.canvas.after.remove(self.high_rect)
            except:
                pass
            self.high_rect = None        
    
    
        if self.is_highlighted:
            if not self.high_rect:
                with self.canvas.after:
                        self.high_color = Color(1,1,1)
                        self.high_rect = Line(rectangle = (self.x, self.y, dp(56), dp(56)), width = dp(2))

    def on_release(self):
        r, c = divmod(self.cell_index, 10)
        parent = self.parent
        while parent and not isinstance(parent, BoardView):
            parent = parent.parent
        if parent:
            parent.on_cell_tap(r, c)

class MenuScreen(Screen):
    pass

class PlayerDropDown(DropDown):
    pass

class DropDownButton(Button):
    
    def __init__(self, **kw):
        super().__init__(**kw)
        self.txt = 'Player'

class SetupScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.DifficultyDropdown = DropDown()
        for dif in ['Hard', 'Medium', 'Easy']:
            btn = Button(
                text = dif,
                size_hint_y = None,
                size_hint_x = 50,
                font_size = 32
            )
            btn.bind(on_release = lambda btn, d = dif: self.select_difficulty(d))
            self.DifficultyDropdown.add_widget(btn)
        
        self.PlayerDropdown = DropDown()

    
    def select_difficulty(self, difficulty):

        app = App.get_running_app()

        if difficulty == 'Hard':
            app.set_difficulty_hard()
        elif difficulty == 'Medium':
            app.set_difficulty_medium()
        elif difficulty == 'Easy':
            app.set_difficulty_easy()
        
        self.DifficultyDropdown.dismiss()
        self.manager.transition.direction = 'up'
        app.root.current = 'Board'

    def open_dropdown(self, widget):

        self.DifficultyDropdown.open(widget)

class WinningScreen(Screen):
    message = StringProperty("")

class WindowManager(ScreenManager):
    pass


class GameState:

    def __init__(self):
        self.players = ['ai', 'human']
        self.b = Board()
        self.ai = AI_Player()
        self.current_idx = 0
    
        self.difficulty = 2
        self.mode = '1vAI'
        self.colors = ['W', 'B']
        


    def end_move(self):
        self.current_idx = (self.current_idx + 1) % len(self.players)
        Over, winner = self.b.isOver()
        if Over:
            Clock.schedule_once(lambda *_: App.get_running_app().game_won(winner))
        if self.mode == '1vAI':
            if self.current_player == 'ai':
                Clock.schedule_once(self.ai_move, 0)




    def save_grid(self):
        grid = copy.deepcopy(self.b.boardlayout)
        for row in grid:
            for square in row:
                square['piece'] = str(square['piece'])
        data = {
                "to_move": ['W', 'B'][self.current_idx],
                "camps": self.b.camps,
                "grid": grid
            }

        with open('SaveGame.json', 'w') as f:
            json.dump(data, f)

    def load_grid(self):
        with open('Savegame.json', 'r') as f:
            loaded = json.load(f)
        self.b.camps = loaded['camps']
        self.current_idx = ['W', 'B'].index(loaded['to_move'])
        board = loaded['grid']
        colours = []
        for row in board:
            row_colours = []
            for square in row:
                if square['piece'] == 'None':
                    square['piece'] = None
                else: 
                    colour, label = square['piece'][0], square['piece'][1:3]
                    square['piece'] = Piece(colour, label)
                row_colours.append(square['colour'])
            colours.append(row_colours)
        self.b.colours = colours
                
        return board
        


    def two_player_mode(self):
        self.mode = '1v1'
        self.players = ['W', 'B']

    def AI_mode(self):
        self.mode = '1vAI'
        self.players = ['ai', 'human']

    def ai_move(self,dt):
        color = self.colors[self.players.index('ai')]
        move= self.ai.find_best_move(self.b, color, self.difficulty)
        move = Move(src=move[0], dst= move[1]) 
        ok, err, record = self.b.apply_move(color, move.src, move.dst)
        App.get_running_app().root.get_screen('Board').refresh_board()
        self.end_move()


    def start_move(self):
        print(self.current_player)
        if self.current_player == 'ai':
            Clock.schedule_once(self.ai_move, 1)
        return 

    @property
    def current_player(self):
        return self.players[self.current_idx]


    def events_apply_move(self, move):
        if self.mode == '1vAI':
            player_color = self.colors[self.players.index(self.current_player)]
        else:
            player_color = self.current_player
    
        ok, err, record = self.b.apply_move(player_color, move.src, move.dst)
        events = []
        if ok:
            events.append({"type": 'move', "from": move.src, 'to': move.dst})
            if record.captured_piece is not None:
                events.append({"type": 'capture', 'at': move.dst})
        else:
            events.append({"type": "error", "message": err})
        return events

class BoardView(Screen):
    status = StringProperty("")
    gs = ObjectProperty(allownone=True)
    highlights = ListProperty([])
    selected = ObjectProperty(allownone = True)

    def on_kv_post(self, _):
        self.gs = GameState()
        self.status = f"Turn: {self.gs.current_player}"
        Clock.schedule_once(self._tighten, 0)
        self.refresh_board()

    def new_game(self):
        self.selected = None
        difficulty = self.gs.difficulty
        mode = self.gs.mode
        players = self.gs.players
        self.gs = None
        self.gs = GameState()
        self.gs.difficulty = difficulty
        self.gs.mode = mode
        self.gs.players = players
        self.highlights = []
        self.refresh_board()
    
    def teardown(self):
        rv = self.ids.rv
        rv.data = []
        rv.refresh_from_data()

    def _tighten(self, *_):
        rv = self.ids.rv
        lm = rv.layout_manager
        rv.size = (lm.minimum_width+dp(4), lm.minimum_height+dp(4))

    def refresh_board(self):
        cells = []
        for r in range(10):
            for c in range(10):
                is_highlighted = None
                if r == 0 or c == 0 or r==9 or c ==9:
                    if (r,c) == (0,0):
                        cell_image_source = 'assets/camp.png'
                        if len(self.gs.b.camps['W']) > 0:
                            piece = self.gs.b.camps['W'][0]
                        else:
                            piece = None
                    elif (r,c) == (0,9):
                        cell_image_source = 'assets/camp.png'
                        if len(self.gs.b.camps['W']) > 1:
                            piece = self.gs.b.camps['W'][1]
                        else:
                            piece = None
                    elif (r,c) == (9,0):
                        cell_image_source = 'assets/camp.png'
                        if len(self.gs.b.camps['B']) > 0:
                            piece = self.gs.b.camps['B'][0]
                        else:
                            piece = None
                    elif (r,c) == (9,9):
                        cell_image_source = 'assets/camp.png'
                        if len(self.gs.b.camps['B']) > 1:
                            piece = self.gs.b.camps['B'][1]
                        else:
                            piece = None

                    else: 
                        cell_image_source = 'assets/Brown_Square.png'
                        piece = None
                else:  
                    background_color = self.gs.b.colours[r-1][c-1]
                    piece =  self.gs.b.boardlayout[r-1][c-1]["piece"]
                    if background_color == 'Y':
                        cell_image_source = 'assets/Yellow_Square.png'
                    elif background_color == 'R':
                        cell_image_source = 'assets/Red_Square.png'
                    elif background_color == 'G':
                        cell_image_source = 'assets/Green_Square.png'
                    elif background_color == 'B':
                        cell_image_source = 'assets/Blue_Square.png'
                is_highlighted = False
                if (r,c) in [(0,0), (0,9)]:
                    if ('campsW') in self.highlights:
                        is_highlighted = True
                elif (r,c) in [(9,0), (9,9)]:
                    if ('campsB') in self.highlights:
                        is_highlighted = True 
                elif (r-1, c-1) in self.highlights:
                    is_highlighted = True

                idx = r * 10 + c
                cells.append({
                    "text": "",
                    "index": idx,
                    "cell_image_source": cell_image_source,
                    "piece": piece,
                    'highlighted': is_highlighted
                })
        self.ids.rv.data = cells
        self.ids.rv.refresh_from_data()



    def on_human_move(self, r,c, player_color):

        if r in [0,9] or c in [0,9]:
            if player_color == 'W' and (r,c) in [(0,0), (0,9)]:
                if (self.selected, ('camp')) in self.gs.b.get_legal_moves(player_color):
                    move = Move(src = self.selected, dst=('camp'))
                    events = self.gs.events_apply_move(move)
                    self.refresh_board()
                    self.gs.end_move()
                    return 
            elif player_color == 'B' and (r,c) in [(9,0), (9,9)]:
                if (self.selected, ('camp')) in self.gs.b.get_legal_moves(player_color):
                    move = Move(src = self.selected, dst=('camp'))
                    events = self.gs.events_apply_move(move)
                    self.refresh_board()
                    self.gs.end_move()
                    return 

            else: 
                return 

        if self.selected is None:
            if self.is_own_piece(r-1,c-1, player_color):
                self.selected = (r-1,c-1)
                self.status = 'selected'
                self.update_highlights(player_color)
            self.update_highlights(player_color)
            return 
        
        if (self.selected,(r-1,c-1)) in self.gs.b.get_legal_moves(player_color):
            move = Move(src = self.selected, dst=(r-1,c-1))
            events = self.gs.events_apply_move(move)
            self.selected = None
            self.update_highlights(player_color)
            self.refresh_board()
            self.gs.end_move()
            return 
        
        if self.is_own_piece(r-1,c-1, player_color):
            self.selected = (r-1,c-1)
            self.update_highlights(player_color)
            return 
        
        self.selected = None
        self.update_highlights(player_color)
        self.refresh_board()
        return
    
    def update_highlights(self, player_color):

        self.highlights = []

        if not self.selected:
            self.refresh_board()
            return 
        
        legal_moves = self.gs.b.get_legal_moves(player_color)
        for src, dst in legal_moves:
            if src == self.selected:
                if dst == 'camp':
                    if player_color == 'W':
                        camps = ('campsW')
                        self.highlights.append(camps)
                    elif player_color == 'B':
                        camps = ('campsB')
                        self.highlights.append(camps)
                else:
                    self.highlights.append(dst)
        self.refresh_board()
        
    def on_cell_tap(self, r, c):
        if self.gs.mode == '1v1':
            self.on_human_move(r,c,self.gs.current_player)
        else:
            if self.gs.current_player == 'human':
                player_color = self.gs.colors[self.gs.players.index('human')]
                self.on_human_move(r,c,player_color)
            elif self.gs.current_player == 'ai':
                return 

        

    def is_own_piece(self, r, c, player_color):
        if self.gs.b.boardlayout[r][c]['piece']:
            if player_color == self.gs.b.boardlayout[r][c]['piece'].player:
                return True
        return False



class KatarengaApp(App):


    title = "Katarenga"
    def build(self):
        Window.size = (800, 700)
        return Builder.load_file("katarenga.kv")
    
    def new_game(self):
        sm = self.root
        game = sm.get_screen("Board")
        game.teardown()
        game.new_game()

    def game_won(self, winner_name):
        sm = self.root
        win = sm.get_screen("Win")
        win.message = f"{winner_name} wins!"
        sm.current = "Win"

    def set_difficulty_hard(self):
        sm = self.root
        board = sm.get_screen("Board")
        board.gs.difficulty = 3
        board.gs.AI_mode()
        
    def set_difficulty_medium(self):
        sm = self.root
        board = sm.get_screen("Board")
        board.gs.difficulty = 2
        board.gs.AI_mode()

    def set_difficulty_easy(self):
        sm = self.root
        board = sm.get_screen("Board")
        board.gs.difficulty = 1
        board.gs.AI_mode()
    
    def OneVsOne(self):
        sm = self.root
        board = sm.get_screen("Board")
        board.gs.two_player_mode()

    def save_game(self):
        sm = self.root
        board = sm.get_screen("Board")
        board.gs.save_grid()

    def load_game(self):
        sm = self.root
        board = sm.get_screen("Board")
        grid = board.gs.load_grid()
        board.refresh_board()
        board.gs.b.boardlayout = grid
        board.refresh_board()

    def start_move(self):
        sm = self.root
        board = sm.get_screen('Board')
        board.gs.start_move()


if __name__ == "__main__":
    KatarengaApp().run()