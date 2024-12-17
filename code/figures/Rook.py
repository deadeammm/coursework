from figures import Figure


class Rook(Figure.Figure):

    def __init__(self, pos, color, board):
        self.notation = 'R'
        super().__init__(pos, color, board)

    def get_possible_moves(self):
        avail = []

        moves_north = []
        for y in range(self.y)[::-1]:
            moves_north.append(self.board((self.x, y)))
        avail.append(moves_north)

        moves_east = []
        for x in range(self.x + 1, 8):
            moves_east.append(self.board((x, self.y)))
        avail.append(moves_east)

        moves_south = []
        for y in range(self.y + 1, 8):
            moves_south.append(self.board((self.x, y)))
        avail.append(moves_south)

        moves_west = []
        for x in range(self.x)[::-1]:
            moves_west.append(self.board((x, self.y)))
        avail.append(moves_west)

        return avail
