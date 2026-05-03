import copy

EMPTY = '.'
ATTACKER = 'A'
DEFENDER = 'D'
KING = 'K'
CORNER = 'X'

SIZE = 11
THRONE_POS = (SIZE // 2, SIZE // 2)
CORNERS = [(0, 0), (0, SIZE-1), (SIZE-1, 0), (SIZE-1, SIZE-1)]


def create_board():
    board = [[EMPTY] * SIZE for _ in range(SIZE)]
    mid = SIZE // 2

    board[mid][mid] = KING

    defenders = [
        (mid-1, mid), (mid+1, mid), (mid, mid-1), (mid, mid+1),
        (mid-2, mid), (mid+2, mid), (mid, mid-2), (mid, mid+2),

        (mid-1, mid-1), (mid-1, mid+1),
        (mid+1, mid-1), (mid+1, mid+1),
    ]
    for r, c in defenders:
        board[r][c] = DEFENDER

    attackers = [
        (0, mid-2),(0, mid-1),(0, mid),(0, mid+1),(0, mid+2),
        (1, mid),

        (SIZE-1, mid-2),(SIZE-1, mid-1),(SIZE-1, mid),(SIZE-1, mid+1),(SIZE-1, mid+2),
        (SIZE-2, mid),

        (mid-2, 0),(mid-1, 0),(mid, 0),(mid+1, 0),(mid+2, 0),
        (mid, 1),

        (mid-2, SIZE-1),(mid-1, SIZE-1),(mid, SIZE-1),(mid+1, SIZE-1),(mid+2, SIZE-1),
        (mid, SIZE-2)
    ]
    for r, c in attackers:
        board[r][c] = ATTACKER

    for r, c in CORNERS:
        board[r][c] = CORNER

    return board


def print_board(board):
   
    print("    " + " ".join(f"{i:2}" for i in range(SIZE)))

    
    print("   +" + "--" * SIZE + "+")

    
    for i, row in enumerate(board):
        print(f"{i:2} |" + " ".join(f"{cell:2}" for cell in row) + " |")

   
    print("   +" + "--" * SIZE + "+")


def is_valid_move(board, player, r, c, nr, nc):
    if not (0 <= r < SIZE and 0 <= c < SIZE and 0 <= nr < SIZE and 0 <= nc < SIZE):
        return False, "Out of bounds"

    piece = board[r][c]

    if player == ATTACKER and piece != ATTACKER:
        return False, "Not your piece"
    if player == DEFENDER and piece not in [DEFENDER, KING]:
        return False, "Not your piece"

    if (r, c) == (nr, nc):
        return False, "Same position"

    if r != nr and c != nc:
        return False, "Must move straight"

    if (nr, nc) in CORNERS:
        if piece != KING:
            return False, "Only king can enter corners"
    else:
        if board[nr][nc] != EMPTY:
            return False, "Target not empty"

    if (nr, nc) == THRONE_POS and piece != KING:
        return False, "Only king can enter throne"

    dr = 0 if nr == r else (1 if nr > r else -1)
    dc = 0 if nc == c else (1 if nc > c else -1)

    cr, cc = r + dr, c + dc
    while (cr, cc) != (nr, nc):
        if board[cr][cc] != EMPTY:
            return False, "Path blocked"
        cr += dr
        cc += dc

    return True, "Valid"


def get_moves(board, r, c):
    moves = []
    piece = board[r][c]

    for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        nr, nc = r + dr, c + dc
        while 0 <= nr < SIZE and 0 <= nc < SIZE:
            if board[nr][nc] != EMPTY:
                break

            if (nr, nc) == THRONE_POS and piece != KING:
                break

            if (nr, nc) in CORNERS:
                if piece == KING:
                    moves.append((nr, nc))
                break

            moves.append((nr, nc))
            nr += dr
            nc += dc

    return moves


if __name__ == "__main__":
    board = create_board()
    print_board(board)