from figures import Figure


class Bishop(Figure.Figure):

    def __init__(self, pos, color, board):
        self.notation = 'B'
        super().__init__(pos, color, board)

    def get_possible_moves(self):
        avail = []

        moves_ne = []
        for i in range(1, 8):
            if self.x + i > 7 or self.y - i < 0:
                break
            moves_ne.append(self.board((self.x + i, self.y - i)))
        avail.append(moves_ne)

        moves_se = []
        for i in range(1, 8):
            if self.x + i > 7 or self.y + i > 7:
                break
            moves_se.append(self.board((self.x + i, self.y + i)))
        avail.append(moves_se)

        moves_sw = []
        for i in range(1, 8):
            if self.x - i < 0 or self.y + i > 7:
                break
            moves_sw.append(self.board((self.x - i, self.y + i)))
        avail.append(moves_sw)

        moves_nw = []
        for i in range(1, 8):
            if self.x - i < 0 or self.y - i < 0:
                break
            moves_nw.append(self.board((self.x - i, self.y - i)))
        avail.append(moves_nw)

        return avail
