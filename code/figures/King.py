from figures import Figure


class King(Figure.Figure):

    def __init__(self, pos, color, board):
        self.notation = 'K'
        super().__init__(pos, color, board)

    def get_possible_moves(self):
        avail = []
        moves = [
            (0, -1),  # north
            (1, -1),  # ne
            (1, 0),  # east
            (1, 1),  # se
            (0, 1),  # south
            (-1, 1),  # sw
            (-1, 0),  # west
            (-1, -1),  # nw
        ]

        for move in moves:
            new_pos = (self.x + move[0], self.y + move[1])
            if (0 <= new_pos[0] < 8 and 0 <= new_pos[1] < 8):
                avail.append([self.board(new_pos)])

        return avail

