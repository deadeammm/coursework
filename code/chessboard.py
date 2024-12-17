import pygame
from config import Config
from figures.Bishop import Bishop
from figures.King import King
from figures.Rook import Rook
from resloader import ResLoader
from infopanel import InfoPanel
import bot


class Square:

    def __init__(self, x, y, width, height, board):

        self.x = x
        # инвертировать доску
        self.y = y if board.player_color == 'w' else 7 - y
        self.width = width
        self.height = height
        self.board = board
        self.screen = board.screen

        self.abs_x = self.board.left_offset + x * width
        self.abs_y = self.board.top_offset + y * height
        self.pos = (self.x, self.y)
        self.draw_color = self.board.LIGHT_COLOR if not sum(self.pos) % 2 else self.board.DARK_COLOR
        self._figure = None
        self.coord = self.get_coord()
        self.highlight, self.check, self.checkmate = False, False, False

        self.rect = pygame.Rect(self.abs_x, self.abs_y, self.width, self.height)

    def __str__(self):
        return f"{self.coord}"

    def get_coord(self):
        columns = 'abcdefgh'
        return columns[self.pos[0]] + str(8 - self.pos[1])

    def set_figure(self, figure):
        self._figure = figure
        if figure:
            self._figure.set_pos(self.pos)

    @property
    def figure(self):
        return self._figure

    def draw(self):
        pygame.draw.rect(self.screen, self.draw_color, self.rect)
        if self.highlight:
            pygame.draw.circle(self.screen, self.board.HIGHLIGHT_COLOR, self.rect.center, self.width // 3, 5)

        if self.check:
            pygame.draw.rect(self.screen, self.board.CHECK_COLOR, self.rect, width=5)

        if self.checkmate:
            pygame.draw.rect(self.screen, self.board.CHECK_COLOR, self.rect)

        if self.figure is not None:
            centering_rect = self.figure.img.get_rect()
            centering_rect.center = self.rect.center
            self.screen.blit(self.figure.img, centering_rect.topleft)


class Board:

    DARK_COLOR = (160, 89, 50)
    LIGHT_COLOR = (224, 179, 133)
    CHECK_COLOR = (160, 10, 10)
    HIGHLIGHT_COLOR = (0, 128, 10)

    def __init__(self, screen, width, height):
        self.width = width
        self.height = height
        self.screen = screen
        self.panel_width = 200
        self.left_offset = (self.screen.get_width() - self.width) // 2
        self.top_offset = (self.screen.get_height() - self.height) // 2
        self.border_offset = 40
        self.tile_width = (width - self.panel_width) // 8
        self.tile_height = height // 8
        self.cfg = Config.get()
        self.history = {}
        self.player_color = self.cfg.PLAYER_COLOR
        self.bot_color = self.invert(self.player_color)
        self.infopanel = InfoPanel(self)
        self.level = self.cfg.DIFFICULTY if self.cfg.DIFFICULTY > 0 else 1
        self.enemy_bot = bot.Minimax(self, self.bot_color, self.level)
        self.player_bot = bot.Minimax(self, self.invert(self.bot_color), self.level)

    def new_game(self, fen=None):
        self._game_result = 0
        self._message = ''
        self.selected_figure = None
        self.turn = 'w'
        self.without_attack = 0
        self.moves = 1

        if fen is None:
            self.history.clear()
            fen = self.cfg.START_POSITION
            self.infopanel.timers.reset()

        self.parse_fen(fen)

        self.history = {k:v for k, v in self.history.items() if k <= self.moves}
        self.squares = self.generate_squares()
        self.setup_board()
        self.is_in_game_over()

    def save_game(self):
        self.cfg.START_POSITION = self.generate_fen()
        self.cfg.save_config()

    def game_over(self, result=None):
        if result:
            self._game_result = result

        if self._game_result:
            if abs(self._game_result) == 1:
                self._message = f'Пат!'
            elif self._game_result == 2:
                self._message = f'Мат черным!'
            elif self._game_result == -2:
                self._message = f'Мат белым!'
            elif self._game_result == 3:
                self._message = f'Время черных вышло!'
            elif self._game_result == -3:
                self._message = f'Время белых вышло!'
            return True

    def is_in_game_over(self):
        if self.without_attack > 50:
            self.game_over(1)
        else:
            self.game_over(self.is_in_checkmate('b') or -self.is_in_checkmate('w'))

        if self._game_result:
            return self._message
        else:
            return ''

    def change_side(self):
        self.update_history(self.clicked_square.pos)

        if self.turn == 'b':
            self.moves += 1

        self.clear_highlight(True)
        self.selected_figure = None
        self.turn = self.invert(self.turn)

    def invert(self, color):
        return 'w' if color == 'b' else 'b'

    def get_pos_from_coord(self, pos):
        return ('abcdefgh'.index(pos[0]), int(pos[1]) - 1)

    def parse_fen(self, fen):
        params = fen.split()
        self.position = params[0]
        if len(params) > 1:
            self.turn = params[1]
            self.without_attack = int(params[2])
            self.moves = int(params[3])

    def generate_squares(self):
        square = []
        for y in range(8):
            for x in range(8):
                square.append(Square(x, y, self.tile_width, self.tile_height, self))
        return square

    def __call__(self, pos):
        y = pos[1] if self.player_color == 'w' else 7 - pos[1]
        return self.squares[y * 8 + pos[0]]

    def find_squares_by_figure(self, color=None, notation=None):

        if notation is not None:
            if color:
                return [i for i in self.squares if i.figure is not None and i.figure.color == color and i.figure.notation == notation]
            else:
                return [i for i in self.squares if i.figure is not None and i.figure.notation == notation]
        else:
            if color:
                return [i for i in self.squares if i.figure is not None and i.figure.color == color]
            else:
                return [i for i in self.squares if i.figure is not None]

    def setup_board(self):
        for y, row in enumerate(self.position.split('/')[:8]):
            x = 0
            irow = iter(row)
            while x < 8:
                figure = next(irow, '')
                square = self((x, y))
                if figure.isdigit():
                    x += int(figure)
                else:
                    color = 'b' if figure in 'rbk' else 'w'
                    if figure in 'Rr':
                        square.set_figure(Rook((x, y), color, self))

                    elif figure in 'Bb':
                        square.set_figure(Bishop((x, y), color, self))

                    elif figure in 'Kk':
                        square.set_figure(King((x, y), color, self))

                    x += 1
#                     print(f"figure: {square.figure} {square.figure.pos}.")

    def generate_fen(self):
        fen = []
        for y in range(8):
            row = ''
            skip = 0
            for x in range(8):
                figure = self((x, y)).figure
                if figure is not None:
                    if skip > 0:
                        row += str(skip)
                        skip = 0
                    row += str(figure)
                else:
                    skip += 1

            if skip > 0:
                row += str(skip)
            fen.append(row)
        return '/'.join(fen) + f" {self.invert(self.turn)} {self.without_attack} {self.moves}"

    def update_history(self, to_pos):
        move = self.history.setdefault(self.moves, {})
        move[self.turn] = str(self.selected_figure) + f'{self((to_pos)).coord}'
        move[f"{self.turn}fen"] = self.generate_fen()
        print(move)

    def clear_highlight(self, clear_check=False):
        for i in self.squares:
            i.highlight = False
            if clear_check:
                i.check = False

    def on_click(self, mx, my):
        x = (mx - self.left_offset) // self.tile_width
        y = (my - self.top_offset) // self.tile_height
        if self.player_color == 'b':
            y = 7 - y

        if 0 <= x <= 7 and 0 <= y <= 7:
            self.clicked_square = self((x, y))
            if not self.clicked_square is None:
#                 print(self.clicked_square.pos)

                self.clear_highlight()
                if not self.clicked_square.figure is None:
                    if self.clicked_square.figure.color == self.turn:
                        self.selected_figure = self.clicked_square.figure
                        return

                if not self.selected_figure is None:
                    return self.selected_figure.move(self.clicked_square)

    def virtual_move(self, from_to, on_moved, *args):  # from_to = [(x1, y1), (x2, y2)]
        changes = {pos:self(pos).figure for pos in from_to}

        self(from_to[1]).set_figure(self(from_to[0]).figure)
        self(from_to[0]).set_figure(None)
        try:
            if callable(on_moved):
                return on_moved(*args)

        finally:
            for pos, figure in changes.items():
                self(pos).set_figure(figure)

    def is_in_check(self, color, from_to=None):  # from_to = [(x1, y1), (x2, y2)]

        def on_moved():
            kings = self.find_squares_by_figure(color, 'K')
            if kings:
                for enemy_squares in self.find_squares_by_figure(self.invert(color)):
                    for square in enemy_squares.figure.attacking_squares():
                        if square.pos == kings[0].pos:
                            return True

        if from_to is not None:
            return self.virtual_move(from_to, on_moved)
        else:
            return on_moved()

    def all_valid_moves(self, color):
        return {s.figure.pos: s.figure.get_valid_moves() for s in self.find_squares_by_figure(color)}

    def is_valid_moves_exists(self, color):
        if any(self.all_valid_moves(color).values()):
            return True

    def is_in_checkmate(self, color):
        result = 0

        kings = self.find_squares_by_figure(color, 'K')
        if not kings:
            return 2
        if not self.is_valid_moves_exists(color):
            if self.is_in_check(color):
                result = 2
                kings[0].checkmate = True
            elif self.turn == color:
                result = 1
        elif self.is_in_check(color):
            kings[0].check = True

        return result

    def draw(self):
        tiles_border = pygame.Rect(self.left_offset, self.top_offset, self.tile_width * 8, self.tile_height * 8)
        board_border = pygame.Rect(self.left_offset - self.border_offset, self.top_offset - self.border_offset, self.width - self.panel_width + 80, self.height + 80)
        pygame.draw.rect(self.screen, self.LIGHT_COLOR, board_border)

        rl = ResLoader.get_instance()
        for i, c in enumerate('abcdefgh', 1):
            text = rl.create_text(c, ['Arial'], 20, color=self.DARK_COLOR)
            self.screen.blit(text, (tiles_border.left + i * self.tile_width - (self.tile_width + text.get_width()) // 2,
                                tiles_border.bottom + text.get_height() // 4))

            self.screen.blit(text, (tiles_border.left + i * self.tile_width - (self.tile_width + text.get_width()) // 2,
                                tiles_border.top - self.border_offset + text.get_height() // 2))

        for i, c in enumerate('87654321' if self.player_color == 'w' else '12345678', 1):
            text = rl.create_text(c, ['Arial'], 20, color=self.DARK_COLOR)
            self.screen.blit(text, (tiles_border.left - self.border_offset + text.get_width() + 5,
                                self.top_offset + i * self.tile_height - (self.tile_height + text.get_height()) // 2))
            self.screen.blit(text, (tiles_border.right + text.get_width(),
                                self.top_offset + i * self.tile_height - (self.tile_height + text.get_height()) // 2))

        for square in self.squares:
            square.draw()

        if self.selected_figure is not None:
            self(self.selected_figure.pos).highlight = True
            for square in self.selected_figure.get_valid_moves():
                square.highlight = True

        pygame.draw.rect(self.screen, self.DARK_COLOR, board_border, width=5)
        pygame.draw.rect(self.screen, self.DARK_COLOR, tiles_border, width=5)

