class Minimax:

    def __init__(self, board, color, depth):
        self.board = board
        self.depth = depth
        self.color = color
        self.player_color = self.board.invert(color)

        self.bishopEval = [
                [ -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
                [ -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
                [ -1.0, 0.0, 0.5, 1.0, 1.0, 0.5, 0.0, -1.0],
                [ -1.0, 0.5, 0.5, 1.0, 1.0, 0.5, 0.5, -1.0],
                [ -1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, -1.0],
                [ -1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0],
                [ -1.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.5, -1.0],
                [ -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]
            ]

        self.rookEval = [
                [  0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [  0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5],
                [ -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
                [ -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
                [ -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
                [ -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
                [ -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
                [  0.0, 0.0, 0.0, 0.5, 0.5, 0.0, 0.0, 0.0]
            ]

        self.kingEval = [
                [ -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
                [ -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
                [ -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
                [ -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
                [ -2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0],
                [ -1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0],
                [  2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0],
                [  2.0, 3.0, 1.0, 0.0, 0.0, 1.0, 3.0, 2.0]
            ]

    def getFigureValue(self, figure):
        if figure is None:
            return 0
        x, y = figure.pos

        def getAbsoluteValue():
            if figure.notation == 'R':
                return 50 + (self.rookEval[y][x] if figure.color == 'w' else self.rookEval[7 - y][x])
            elif figure.notation == 'B':
                return 33 + (self.bishopEval[y][x] if figure.color == 'w' else self.bishopEval[7 - y][x])
            elif figure.notation == 'K':
                return 900 + (self.kingEval[y][x] if figure.color == 'w' else  self.kingEval[7 - y][x])

        absoluteValue = getAbsoluteValue()
        return absoluteValue if figure.color == self.player_color else -absoluteValue

    def evaluateBoard(self):
        return sum(self.getFigureValue(s.figure) for s in self.board.find_squares_by_figure())

    def minimaxRoot (self, depth, is_maximazing):
        color = self.color if is_maximazing else self.player_color
        all_moves = self.board.all_valid_moves(color)
        bestMove = -9999
        bestMoveFound = None, None

        for f_pos, squares in all_moves.items():
            for square in squares:
                new_pos = square.pos
                value = self.board.virtual_move([f_pos, new_pos], self.minimax, depth - 1, -10000, 10000, not is_maximazing)

                if (value >= bestMove):
                    bestMove = value
                    bestMoveFound = f_pos, new_pos

        return bestMoveFound;

    def minimax (self, depth, alpha, beta, is_maximazing):

        def on_moved():
            if is_maximazing:
                return  max(bestMove, self.minimax(depth - 1, alpha, beta, not is_maximazing))
            else:
                return  min(bestMove, self.minimax(depth - 1, alpha, beta, not is_maximazing))

        color = self.color if is_maximazing else self.player_color

        if depth == 0:
            return -self.evaluateBoard()

        bestMove = -9999 if is_maximazing else 9999

        if not self.board.game_over():
            all_moves = self.board.all_valid_moves(color)
            for f_pos, squares in all_moves.items():
                for square in squares:
                        if is_maximazing:
                            bestMove = self.board.virtual_move([f_pos, square.pos], on_moved)
                            alpha = max(alpha, bestMove)

                        else:
                            bestMove = self.board.virtual_move([f_pos, square.pos], on_moved)
                            beta = min(beta, bestMove)

                        if (beta <= alpha):
                            return bestMove

        return bestMove

    def getBestMove(self, qres):
        res = self.minimaxRoot(self.depth, True)
        qres.put(res)
        return res

