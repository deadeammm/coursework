from resloader import ResLoader


class Figure:

    def __init__(self, pos, color, board):
        self.set_pos(pos)
        self.color = color
        self.board = board
        self.has_moved = False
        self.width, self.height = board.tile_width - 20, board.tile_height - 20
        self.img = ResLoader.get_instance().getImage(f'resources/{color}_{self.notation.lower()}.png', self.width, self.height)

    def __str__(self):
        fig = self.notation if self.color == 'w' else self.notation.lower()
        return fig

    def set_pos(self, pos):
        self.pos = pos
        self.x, self.y = pos

    def move(self, to_square, force=False):
        if to_square in self.get_valid_moves() or force:
            old_square = self.board(self.pos)
            to_square.set_figure(self)
            old_square.set_figure(None)

            # число предыдущих ходов без взятий
            if to_square in self.attacking_squares():
                self.board.without_attack = 0
            else:
                self.board.without_attack += 1

            self.has_moved = True

            return True

    def get_moves(self):
        avail = []
        for direction in self.get_possible_moves():
            for square in direction:
                if square.figure is not None:
                    if square.figure.color == self.color:
                        break
                    else:
                        avail.append(square)
                        break
                else:
                    avail.append(square)
        return avail

    def get_valid_moves(self):
        avail = []
        for square in self.get_moves():
            if not self.board.is_in_check(self.color, from_to=[self.pos, square.pos]):
                avail.append(square)

        return avail

    # Направление атаки одинаково для всех кроме пешки
    def attacking_squares(self):
        return self.get_moves()
