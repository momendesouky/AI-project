from pyswip import Prolog

EMPTY = '.'
ATTACKER = 'A'
DEFENDER = 'D'
KING = 'K'
CORNER = 'X'

SIZE = 11
THRONE_POS = (5, 5)
CORNERS = [(0, 0), (0, 10), (10, 0), (10, 10)]

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
    'x': 'X',
    'E': '.',
    'A': 'A',
    'D': 'D',
    'K': 'K',
    'X': 'X'
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


def parse_pos_term(item):
    """
    Converts Prolog term pos(R,C,Piece) to Python tuple.
    Example: pos(4,5,d) -> (4, 5, 'D')
    """
    text = str(item).strip()
    text = text.replace("pos(", "").replace(")", "")

    parts = [p.strip() for p in text.split(",")]

    if len(parts) != 3:
        raise ValueError(f"Invalid captured term format: {text}")

    cr = int(parts[0])
    cc = int(parts[1])
    piece_key = parts[2].strip()

    piece = PL_TO_PY[piece_key]

    return cr, cc, piece


def parse_move_term(item):
    """
    Converts Prolog term move(R,C,NR,NC) to Python tuple.
    Example: move(0,3,2,3) -> (0, 3, 2, 3)
    """
    text = str(item).strip()
    text = text.replace("move(", "").replace(")", "")

    parts = [p.strip() for p in text.split(",")]

    if len(parts) != 4:
        raise ValueError(f"Invalid move term format: {text}")

    return tuple(map(int, parts))


def apply_move(board, player, r, c, nr, nc, silent=False):
    b = board_to_pl(board)
    p = player_to_pl(player)

    q = f"apply_move({b},{p},{r},{c},{nr},{nc},NewBoard,Captured)."

    try:
        result = list(prolog.query(q))
    except Exception as e:
        if not silent:
            print("Prolog error in apply_move:", e)
        return False, []

    if not result:
        if not silent:
            print("Invalid move")
        return False, []

    new_board = pl_board_to_py(result[0]["NewBoard"])

    for i in range(SIZE):
        for j in range(SIZE):
            board[i][j] = new_board[i][j]

    captured = []

    try:
        for item in result[0]["Captured"]:
            captured.append(parse_pos_term(item))
    except Exception as e:
        if not silent:
            print("Captured parsing error:", e)
        captured = []

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
        moves.append(parse_move_term(m))

    return moves


class HnefataflAI:
    def __init__(self, difficulty=DIFFICULTY_MEDIUM):
        self.difficulty = difficulty

    def get_best_move(self, board, player):
        b = board_to_pl(board)
        p = player_to_pl(player)

        try:
            result = list(prolog.query(
                f"best_move({b},{p},{self.difficulty},BestMove,BestValue)."
            ))
        except Exception as e:
            print("Prolog error in best_move:", e)
            return None

        if not result:
            return None

        return parse_move_term(result[0]["BestMove"])
