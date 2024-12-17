import pygame_widgets
from pygame_widgets.button import Button
from resloader import ResLoader

_widgets_ = []


class Menu:

    def __init__(self, board):
        global _widgets_
        self.screen = board.screen
        self.board = board
        self.width = board.panel_width
        self.font = ResLoader.get_instance().get_font(['Arial'], 14, bold=True)

        _widgets_.append(self.button_new_game())
        _widgets_.append(self.button_save_config())

    def height(self):
        return _widgets_[-1].getHeight()

    def button_new_game(self):

        return Button(self.screen,
                self.board.left_offset + self.board.border_offset + self.board.width - self.width,
                self.board.top_offset - self.board.border_offset,
                self.width // 2,
                self.board.border_offset,
                text='Новая игра',
                inactiveColour=self.board.LIGHT_COLOR,
                hoverColour=[i - 20 for i in self.board.LIGHT_COLOR],
                pressedColour=[i - self.board.border_offset for i in self.board.LIGHT_COLOR],
                textColour=self.board.DARK_COLOR,
                font=self.font,
                onClick=self.board.new_game
            )

    def button_save_config(self):

        return Button(self.screen,
                self.board.left_offset + self.board.border_offset + self.board.width - self.width // 2,
                self.board.top_offset - self.board.border_offset,
                self.width // 2,
                self.board.border_offset,
                text='Сохранить',
                inactiveColour=self.board.LIGHT_COLOR,
                hoverColour=[i - 20 for i in self.board.LIGHT_COLOR],
                pressedColour=[i - 40 for i in self.board.LIGHT_COLOR],
                textColour=self.board.DARK_COLOR,
                font=self.font,
                onClick=self.board.save_game
            )

    def draw(self, events):
        pygame_widgets.update(events)

