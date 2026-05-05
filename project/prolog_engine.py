from pyswip import Prolog

EMPTY = '.'
ATTACKER = 'A'
DEFENDER = 'D'
KING = 'K'
CORNER = 'X'

SIZE = 11
THRONE_POS = (5, 5)
CORNERS = [(0,0), (0,10), (10,0), (10,10)]

DIFFICULTY_EASY = 1
DIFFICULTY_MEDIUM = 2
DIFFICULTY_HARD = 3

prolog = Prolog()
prolog.consult("hnefatafl_logic.pl")

PY_TO_PL = {
    '.': 'e',
    'A': 'a',
    'D': 'd',
    'K': 'k',
    'X': 'x'
}

PL_TO_PY = {
    'e': '.',
    'a': 'A',
    'd': 'D',
    'k': 'K',
    'x': 'X'
}

def player_to_pl(player):
    return 'a' if player == ATTACKER else 'd'

def board_to_pl(board):
    rows = []
    for row in board:
        rows.append("[" + ",".join(PY_TO_PL[cell] for cell in row) + "]")
    return "[" + ",".join(rows) + "]"

def pl_board_to_py(pl_board):
    return [[PL_TO_PY[str(cell)] for cell in row] for row in pl_board]

def create_board():
    result = list(prolog.query("initial_board(Board)."))[0]
    return pl_board_to_py(result["Board"])

def is_valid_move(board, player, r, c, nr, nc):
    b = board_to_pl(board)
    p = player_to_pl(player)
    q = f"legal_move({b},{p},{r},{c},{nr},{nc})."
    ok = bool(list(prolog.query(q)))
    return ok, "Valid" if ok else "Invalid move"

def apply_move(board, player, r, c, nr, nc, silent=False):
    b = board_to_pl(board)
    p = player_to_pl(player)

    q = f"apply_move({b},{p},{r},{c},{nr},{nc},NewBoard,Captured)."
    result = list(prolog.query(q))

    if not result:
        if not silent:
            print("Invalid move")
        return False, []

    new_board = pl_board_to_py(result[0]["NewBoard"])

    for i in range(SIZE):
        for j in range(SIZE):
            board[i][j] = new_board[i][j]

    captured = []
    for item in result[0]["Captured"]:
        text = str(item)
        # pos(R,C,Piece)
        text = text.replace("pos(", "").replace(")", "")
        parts = text.split(",")
        cr = int(parts[0])
        cc = int(parts[1])
        piece = PL_TO_PY[parts[2]]
        captured.append((cr, cc, piece))

    return True, captured

def king_escaped(board):
    b = board_to_pl(board)
    return bool(list(prolog.query(f"king_escaped({b}).")))

def is_king_captured(board):
    b = board_to_pl(board)
    return bool(list(prolog.query(f"king_captured({b}).")))

def get_all_moves(board, player, pieces=None):
    b = board_to_pl(board)
    p = player_to_pl(player)

    result = list(prolog.query(f"all_moves({b},{p},Moves)."))
    if not result:
        return []

    moves = []
    for m in result[0]["Moves"]:
        text = str(m)
        text = text.replace("move(", "").replace(")", "")
        r, c, nr, nc = map(int, text.split(","))
        moves.append((r, c, nr, nc))

    return moves

class HnefataflAI:
    def __init__(self, difficulty=DIFFICULTY_MEDIUM):
        self.difficulty = difficulty

    def get_best_move(self, board, player):
        b = board_to_pl(board)
        p = player_to_pl(player)

        result = list(prolog.query(
            f"best_move({b},{p},{self.difficulty},BestMove,BestValue)."
        ))

        if not result:
            return None

        text = str(result[0]["BestMove"])
        text = text.replace("move(", "").replace(")", "")
        r, c, nr, nc = map(int, text.split(","))
        return (r, c, nr, nc)