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
from kivy.uix.modalview import ModalView

import sys 
import time
import math

from board import Board, Piece, MoveRecord
from ai import AI_Player
import copy
import json
from pathlib import Path

base_directory = Path(__file__).resolve().parent #base directory used for packagin using pyinstaller

@dataclass
class Move: #used in ai_move() to pass the ai's move to the apply_move() function in board.py
    src: tuple
    dst: Union[tuple, str]

class StyledDropDown(DropDown):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.container.spacing = dp(3)
        self.container.padding= (dp(4), dp(4))
        self.container.cols = 1

class FormattedButton(Button):
    radius = ListProperty([dp(14), dp(14),dp(14), dp(14)])
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class GameOverPopup(ModalView, BoxLayout):
    winner_text = StringProperty('Winner')
    reason = StringProperty('Error')
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class GameClock:
    def __init__(self):
        self.remaining = {'W': 600, "B": 600}
        self.initial_time = {'W': 600, "B": 600}
        self.current = None
        self.last_update = None
        self.fisher_time = 3

    def start(self, colour):
    
        self.current = colour
        self.last_update = time.monotonic()

    def update(self):
        if self.current == None or self.last_update == None:
            return
        now = time.monotonic()
        dt = now - self.last_update
        self.remaining[self.current] -= dt
        self.last_update = now
    
    def pause(self):
        self.update()
        self.current = None
        self.last_update = None
    
    def get_remaining(self,player,ai):
        if player == self.current and player != ai:
            self.update()
        return max(0.0, self.remaining[player])
    
    def switch(self, colour):
        self.current = colour


class ClockWidget(BoxLayout):
    white_text = StringProperty('10:00')
    black_text = StringProperty('10:00')
    ai = StringProperty(None)
    def __init__(self, **kwargs):
        self.gs = None
        super().__init__(**kwargs)

    def on_kv_post(self, _):
        Clock.schedule_interval(self.refresh, 0.1)

    def refresh(self, dt):
        self.app = App.get_running_app()
        self.gs = App.get_running_app().root.get_screen("Board").gs
        clock = self.gs.clock
        self.ai = ''
        for i in  range(len(self.gs.players)):
            if self.gs.players[i] == 'ai':
                self.ai = self.gs.colors[i]
                break
        if clock.current is not None and not self.gs.game_over:
            if math.floor(clock.get_remaining(clock.current, self.ai)*10,) == 0:
                clock.pause()
                winner = 'Black' if clock.current == 'W' else 'White'
                reason = 'Timed Out'
                self.app.game_won(winner, reason)
        



        w = clock.get_remaining('W', self.ai)
        b = clock.get_remaining('B', self.ai)
        minutesw = int(w//60)
        minutesb = int(b//60)
        secondsw = w%60
        secondsb = b%60

        if secondsw < 10:  
            if  minutesw == 0:
                secondsw = f'0{math.floor(secondsw)}:{math.floor((secondsw*10)%10)}'
            else:
                secondsw = f'0{math.floor(secondsw)}'
        else:
            secondsw = math.floor(secondsw)

        if secondsb < 10:  
            if  minutesb == 0:
                secondsb = f'0{math.floor(secondsb)}:{math.floor((secondsb*10)%10)}'
            else:
                secondsb = f'0{math.floor(secondsb)}'
        else:
            secondsb = math.floor(secondsb)
        
        self.white_text = f'{minutesw}:{secondsw}' if self.ai != 'W' else '00:00'
        self.black_text = f'{minutesb}:{secondsb}' if self.ai != 'B' else '00:00'



class Cell(Button, RecycleDataViewBehavior): #inherits fron Button and RecycleDataViewBehaviour
    def __init__(self, **kwargs): 
        
        super().__init__(**kwargs)
        
        self._rect = None 
        self.cell_image_source = str(base_directory/'assets'/'Brown_Square.png')
        self.background_color = 0,0,0,0
        self.white_piece_image_source = str(base_directory/'assets'/'white_pawn.png')
        self.black_piece_image_source = str(base_directory/'assets'/'black_pawn.png')
        self.piece_rect = None
        self.high_rect = None
        self.bind(size = self.sync_pieces, pos = self.sync_pieces) #everytime pos or size change sync pieces is automatically called
        



    def refresh_view_attrs(self, rv, index, data): #this function is automatically called when the grid changes and using poylmorphism I can customize what it does
        ret = super().refresh_view_attrs(rv, index, data)
        self._rv = rv
        #The code below syncs the Cells of the grid with the Recycle View or rv which changes when any of the boards elements change e.g. a piece is moved
        self.cell_index = index
        self.cell_text = data.get('text', '')
        self.cell_image_source = data.get('cell_image_source')
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
    #if the window is rescaled this ensures that pieces keep their relative size and position
    def sync_pieces(self, *args):
        if self.piece_rect:
            self.piece_rect.pos = self.pos
            self.piece_rect.size = self.size
    #This function will redraw the pieces onto their relevant squares
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
    #This function redraws the highlights when a piece is selected
    def update_highlights(self):
            
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
    #This links the built in on_release() function with the BoardView's on_human_move() function
    def on_release(self):
        r, c = divmod(self.cell_index, 10) #converts the cells ID number to a row and column number
        parent = self.parent
        while parent and not isinstance(parent, BoardView):
            parent = parent.parent
        if parent:
            parent.on_cell_tap(r, c)

class MenuScreen(Screen):
    pass


class SetupScreen(Screen): #This class inherits from a Screen class but I overwrite it.
    player1 = StringProperty('White: Human')
    player2 = StringProperty('Black: AI')
    time_format = StringProperty('Time Format: 10 min')
    difficulty_text = StringProperty('Difficulty: Medium')
    def on_kv_post(self, base_widget):
        return super().on_kv_post(base_widget)

    def __init__(self, **kw):
        super().__init__(**kw)
        #The dropdowns work better when created in python file and not .kv file so the init function creates all of the dropdowns
        self.DifficultyDropdown = StyledDropDown()
        self.white_drop_down = StyledDropDown()
        self.black_drop_down = StyledDropDown()
        self.time_drop_down = StyledDropDown()
        

        self.current_txt_w = 'human'

        for dif in ['Hard', 'Medium', 'Easy']:
            btn = FormattedButton(
                text = dif,
                size_hint_y = None,
                size_hint_x = 50,
                font_size = 32,
                radius = [dp(4),]
            )
            btn.bind(on_release = lambda btn, d = dif: self.select_difficulty(d))
            self.DifficultyDropdown.add_widget(btn)
        for player in ['Human', 'AI']:
            btn = FormattedButton(
                text = player,
                size_hint_y = None,
                size_hint_x = 50,
                font_size = 32,
                radius = [dp(4),]
            )
            btn.bind(on_release = lambda btn, p = player: self.select_white_player(p))
            self.white_drop_down.add_widget(btn)
        for player in ['Human', 'AI']:
            btn = FormattedButton(
                text = player,
                size_hint_y = None,
                size_hint_x = 50,
                font_size = 32,
                radius = [dp(4),]
            )
            btn.bind(on_release = lambda btn, p = player: self.select_black_player(p))
            self.black_drop_down.add_widget(btn)
        for time in ['1 min','1|1', '3|2', '10 min']:
            btn = FormattedButton(
                text = time,
                size_hint_y = None,
                size_hint_x = 50,
                font_size = 32,
                radius = [dp(4),]
            )
            btn.bind(on_release = lambda btn, t = time: self.change_time_format(t))
            self.time_drop_down.add_widget(btn)

    #the following functions link the differnt dropdown buttons to their corresponding function in the KatarengaApp class

    def select_black_player(self, p):
        self.player2 = f'Black: {p}'
        app = App.get_running_app() #this retreives the KatarengaApp class
        app.change_players(1, p)

    def select_white_player(self, p):
        self.player1 = f'White: {p}'
        app = App.get_running_app()
        app.change_players(0, p)

    def select_difficulty(self, difficulty):
        self.difficulty_text = f"Difficulty: {difficulty}"
        app = App.get_running_app()

        if difficulty == 'Hard':
            app.set_difficulty_hard()
        elif difficulty == 'Medium':
            app.set_difficulty_medium()
        elif difficulty == 'Easy':
            app.set_difficulty_easy()
        
        self.DifficultyDropdown.dismiss() #closes the dropdown
    
    def change_time_format(self, format):
        self.time_format = f"Time Format: {format}"
        app = App.get_running_app()
        app.ChangeTimeFormat(format)



class WindowManager(ScreenManager):
    pass


class GameState: #This manages the game loop

    def __init__(self):
        self.players = ['human', 'ai']
        self.b = Board()
        self.clock = GameClock()
        self.ai = AI_Player()
        self.current_idx = 0 #either 0 or 1 denoting white and black respectively
        self.difficulty = 2
        self.colors = ['W', 'B']
        self.game_over = False
        

    def end_move(self): #game loop includes an endless start move and end move cycle until the game is won or lost
        mover = self.colors[self.current_idx]
        self.clock.pause()
        self.current_idx = (self.current_idx + 1) % len(self.players) #changes the current idx to the next players 
        Over, winner, reason = self.b.isOver()
        if Over:
            Clock.schedule_once(lambda *_: App.get_running_app().game_won(winner, reason ))#triggers the game won function in the KatarengaApp class
        
        fisher_time = self.clock.remaining[mover] + self.clock.fisher_time
        
        self.clock.remaining[mover] = min(self.clock.initial_time[mover], fisher_time)
        

        self.start_move()
    




    def save_grid(self): #makes a dictionary out of the entire grid and saves that to a json file
        grid = copy.deepcopy(self.b.boardlayout)
        for row in grid:
            for square in row:
                square['piece'] = str(square['piece'])
        camps = {'W': [], "B": []}
        for i in range(len(self.b.camps['W'])):
            camps['W'].append(str(self.b.camps['W'][i]))
        for i in range(len(self.b.camps['B'])):
            camps['B'].append(str(self.b.camps['B'][i]))
        self.clock.update()
        white_time_remaining = self.clock.remaining['W']
        black_time_remaining = self.clock.remaining['B']
        time_remaining = f'{str(white_time_remaining)},{str(black_time_remaining)}'
        fisher_time = str(self.clock.fisher_time)
    
        data = {
                "to_move": ['W', 'B'][self.current_idx],
                "camps": camps,
                "grid": grid,
                'time_remaining': time_remaining,
                'fisher_time': fisher_time
            }

        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'): #checks whether launched from IDE or .app version
            base = Path(sys._MEIPASS)
        else:
            base = Path(__file__).resolve().parent
        #The base path ensures that whether launching from IDE or packaged .app version Savegame.json can be found
        path = str(base / 'Savegame.json')
        with open(path, 'w') as f:
            json.dump(data, f)


    def load_grid(self):
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'): #checks whether launched from IDE or .app version
            base = Path(sys._MEIPASS)
        else:
            base = Path(__file__).resolve().parent
        #The base path ensures that whether launching from IDE or packaged .app version Savegame.json can be found
        path = str(base / 'Savegame.json')
        with open(path, 'r') as f:
            loaded = json.load(f)
        camps = loaded['camps']
        for i in range(len(camps['W'])):
            camps['W'][i] = Piece((camps["W"][i][0]),camps['W'][i][1:-1])
        for i in range(len(camps['B'])):
            camps['B'][i] = Piece((camps["B"][i][0]),camps['B'][i][1:-1])
        self.b.camps = camps
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
        time_remaining = loaded['time_remaining']
        time_remaining = time_remaining.split(',')
        self.clock.remaining['W'] = float(time_remaining[0])
        self.clock.remaining['B'] = float(time_remaining[1])
        self.clock.fisher_time = loaded['fisher_time']

                
        return board
        

    def ai_move(self,dt):
        color = self.colors[self.current_idx]
        move= self.ai.find_best_move(self.b, color, self.difficulty)
        move = Move(src=move[0], dst= move[1]) 
        ok, err, record = self.b.apply_move(color, move.src, move.dst)
        App.get_running_app().root.get_screen('Board').refresh_board()
        self.end_move()


    def start_move(self): #This gets called after end_move() and checks if it is the player's or ai's turn
        self.clock.start(self.colors[self.current_idx])
        if not self.game_over:
            if self.current_player == 'ai':
                Clock.schedule_once(self.ai_move, 1)
        return   #if it is the player's turn the player can now interact with his pieces freely so the function can terminate

    @property
    def current_player(self): #useful property throughout the program as it allows to keep track of who's turn it is
        return self.players[self.current_idx]

    def events_apply_move(self, move): #This is an events backend that I can later use for animations, sounds and error messages to the user
        
        player_color = self.colors[self.current_idx]
    
        ok, err, record = self.b.apply_move(player_color, move.src, move.dst)
        events = []
        if ok:
            events.append({"type": 'move', "from": move.src, 'to': move.dst})
            if record.captured_piece is not None:
                events.append({"type": 'capture', 'at': move.dst})
        else:
            events.append({"type": "error", "message": err})
        return events

class BoardView(Screen): #This class handles the way the board is graphically represented or viewed

    status = StringProperty("")
    gs = ObjectProperty(allownone=True)
    highlights = ListProperty([])
    selected = ObjectProperty(allownone = True)

    def on_kv_post(self, _): #automatically gets called when the BoardView screen is first instantiated
        self.gs = GameState()
        self.status = f"Turn: {self.gs.current_player}" #property that can be used for animations and messages to the user. For example an animation when AI is thinking
        Clock.schedule_once(self._tighten, 0)
        self.refresh_board()

    def new_game(self): #sets up a fresh game where all the settings are dicated by the preset in gamestate
        self.selected = None
        difficulty = self.gs.difficulty
        players = self.gs.players
        self.gs = None
        self.gs = GameState()
        self.gs.difficulty = difficulty
        self.gs.players = players
        self.highlights = []
        self.refresh_board()
    
    #ensures that when a new game is created the old one gets removed properly
    def teardown(self):
        rv = self.ids.rv
        rv.data = []
        rv.refresh_from_data()
    #makes the rv size the same as the layout managers minimum size so that everything narrowly fits onto the board.
    def _tighten(self, *_):
        rv = self.ids.rv
        lm = rv.layout_manager
        rv.size = (lm.minimum_width+dp(4), lm.minimum_height+dp(4))

    def refresh_board(self): #This directly changes the recycle view's data 
        cells = []
        for r in range(10):
            for c in range(10):
                is_highlighted = None
                if r == 0 or c == 0 or r==9 or c ==9: #assigns the enemy camps different textures than the other surrounding squares
                    if (r,c) == (0,0):
                        cell_image_source = str(base_directory/'assets'/'camp.png')
                        if len(self.gs.b.camps['W']) > 0:
                            piece = self.gs.b.camps['W'][0]
                        else:
                            piece = None
                    elif (r,c) == (0,9):
                        cell_image_source = str(base_directory/'assets'/'camp.png')
                        if len(self.gs.b.camps['W']) > 1:
                            piece = self.gs.b.camps['W'][1]
                        else:
                            piece = None
                    elif (r,c) == (9,0):
                        cell_image_source = str(base_directory/'assets'/'camp.png')
                        if len(self.gs.b.camps['B']) > 0:
                            piece = self.gs.b.camps['B'][0]
                        else:
                            piece = None
                    elif (r,c) == (9,9):
                        cell_image_source = str(base_directory/'assets'/'camp.png')
                        if len(self.gs.b.camps['B']) > 1:
                            piece = self.gs.b.camps['B'][1]
                        else:
                            piece = None

                    else: 
                        cell_image_source = str(base_directory/'assets'/'Brown_Square.png')
                        piece = None
                else:  #applies the correct texture to the differntly coloured squares
                    background_color = self.gs.b.colours[r-1][c-1]
                    piece =  self.gs.b.boardlayout[r-1][c-1]["piece"]
                    if background_color == 'Y':
                        cell_image_source =  str(base_directory/'assets'/'Yellow_Square.png')
                    elif background_color == 'R':
                        cell_image_source =  str(base_directory/'assets'/'Red_Square.png')
                    elif background_color == 'G':
                        cell_image_source =  str(base_directory/'assets'/'Green_Square.png')
                    elif background_color == 'B':
                        cell_image_source =  str(base_directory/'assets'/'Blue_Square.png')
                
                is_highlighted = False
                #manage highlighting the camps
                if (r,c) in [(0,0), (0,9)]:
                    if ('campsW') in self.highlights: #self.highlights are all the squares that the currently selected piece is able to move to
                        is_highlighted = True
                elif (r,c) in [(9,0), (9,9)]:
                    if ('campsB') in self.highlights:
                        is_highlighted = True 

                #manages highlighting all othe squares
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
                    self.update_highlights(player_color)
                    self.gs.end_move()
                    return 
            elif player_color == 'B' and (r,c) in [(9,0), (9,9)]:
                if (self.selected, ('camp')) in self.gs.b.get_legal_moves(player_color):
                    move = Move(src = self.selected, dst=('camp'))
                    events = self.gs.events_apply_move(move)
                    self.refresh_board()
                    self.update_highlights(player_color)
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

        if self.gs.game_over:
            return 
        else:
            if self.gs.current_player == 'human':
                player_color = self.gs.colors[self.gs.current_idx]
                self.on_human_move(r,c,player_color)
            elif self.gs.current_player == 'ai':
                return 

        

    def is_own_piece(self, r, c, player_color):
        if r > 7 or c > 7:
            return False
        if self.gs.b.boardlayout[r][c]['piece']:
            if player_color == self.gs.b.boardlayout[r][c]['piece'].player:
                return True
        return False



class KatarengaApp(App):
    gs = ObjectProperty(None)

    title = "Katarenga"

    def on_start(self):
        self.gs = self.root.get_screen("Board").gs

    def build(self):
        Window.size = (850, 700)
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'): #checks whether launched from IDE or .app version
            base = Path(sys._MEIPASS)
        else:
            base = Path(__file__).resolve().parent
        #The base path ensures that whether launching from IDE or packaged .app version katarenga.kv can be found
        kv_path = base / "ui.kv"
        #This opens the GUI window in the format sepcified in the katarenga.kv setup file
        return Builder.load_file(str(kv_path))
    def new_game(self):
        sm = self.root
        game = sm.get_screen("Board")
        game.teardown()
        game.new_game()
        #Links the NEW GAME GUI button to game logic


    def game_won(self, winner, reason):
        sm = self.root
        game = sm.get_screen("Board")

        game.gs.game_over = True   

        winner_text = f'{winner} Wins!'
        loser = 'Black' if winner == 'White' else 'White'
        if reason == 'Timed Out':
            reason_text = f'{loser} Timed Out'
        elif reason == 'Insufficient Material':
            reason_text = f'{loser} has Insufficient Material'
        elif reason == 'two camps':
            reason_text = f'{winner} Infiltrated the Enemies Camps'

        GameOverPopup(winner_text = winner_text, reason = reason_text).open()

    def ChangeTimeFormat(self, format):
        sm = self.root
        game = sm.get_screen("Board")

        if format == "3|2":
            game.gs.clock.remaining = {'W': 180, 'B': 180}
            game.gs.clock.initial_time = {'W': 180, 'B': 180}
            game.gs.clock.fisher_time = 2
            
        elif format == '1 min':
            game.gs.clock.remaining = {'W': 60, 'B': 60}
            game.gs.clock.initial_time = {'W': 60, 'B': 60}
            game.gs.clock.fisher_time = 0
        
        elif format == '10 min':
            game.gs.clock.remaining = {'W': 600, 'B': 600}
            game.gs.clock.initial_time = {'W': 600, 'B': 600}
            game.gs.clock.fisher_time = 0

        elif format == '1|1':
            game.gs.clock.remaining = {'W': 60, 'B': 60}
            game.gs.clock.initial_time = {'W': 60, 'B': 60}
            game.gs.clock.fisher_time = 1
        
            

    def set_difficulty_hard(self):
        sm = self.root
        board = sm.get_screen("Board")
        board.gs.difficulty = 3
        #Links the difficulty HARD GUI button to game logic


    def set_difficulty_medium(self):
        sm = self.root
        board = sm.get_screen("Board")
        board.gs.difficulty = 2
        #Links the difficulty MEDIUM GUI button to game logic

    def set_difficulty_easy(self):
        sm = self.root
        board = sm.get_screen("Board")
        board.gs.difficulty = 1
        #Links the difficulty EASY GUI button to game logic

    def save_game(self):
        sm = self.root
        board = sm.get_screen("Board")
        board.gs.save_grid()
        #Links the difficulty SAVE GAME GUI button to game logic

    def load_game(self):
        sm = self.root
        board = sm.get_screen("Board")
        grid = board.gs.load_grid()
        board.refresh_board()
        board.gs.b.boardlayout = grid
        board.refresh_board()
        #Links the difficulty LOAD GAME GUI button to game logic

    def start_move(self):#This starts the start move and end move cycle included in the game logic
        sm = self.root
        board = sm.get_screen('Board')
        board.gs.clock.start('W')
        board.gs.start_move()

    def change_players(self, color, player):
        sm = self.root
        board = sm.get_screen('Board')
        board.gs.players[color] = player.lower()
        #When the player changes either white or black player this links that change to the players attribute in GameState

if __name__ == "__main__":
    KatarengaApp().run()
