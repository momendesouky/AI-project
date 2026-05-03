import copy

# ---------------- CONSTANTS ----------------
EMPTY = '.'
ATTACKER = 'A'
DEFENDER = 'D'
KING = 'K'
CORNER = 'X'

SIZE = 11
THRONE_POS = (SIZE // 2, SIZE // 2)
CORNERS = [(0, 0), (0, SIZE-1), (SIZE-1, 0), (SIZE-1, SIZE-1)]

# ---------------- BOARD SETUP ----------------
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

# ---------------- PRINT ----------------
def print_board(board):
    print("    " + " ".join(f"{i:2}" for i in range(SIZE)))
    print("   +" + "--" * SIZE + "+")

    for i, row in enumerate(board):
        print(f"{i:2} |" + " ".join(f"{cell:2}" for cell in row) + " |")

    print("   +" + "--" * SIZE + "+")

# ---------------- MOVE VALIDATION ----------------
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

# ---------------- SANDWICH CHECK ----------------
def is_in_sandwich(board, row, col, piece):
    if piece == ATTACKER:
        enemy = [DEFENDER, KING]
    elif piece == DEFENDER:
        enemy = [ATTACKER]
    else:
        return False

    if 0 <= col-1 < SIZE and 0 <= col+1 < SIZE:
        if board[row][col-1] in enemy and board[row][col+1] in enemy:
            return True

    if 0 <= row-1 < SIZE and 0 <= row+1 < SIZE:
        if board[row-1][col] in enemy and board[row+1][col] in enemy:
            return True

    return False

# ---------------- CAPTURE ----------------
def check_capture(board, row, col):
    current = board[row][col]
    captured = []

    if current == ATTACKER:
        enemy = DEFENDER
        friendly = [ATTACKER]

    elif current == DEFENDER or current == KING:
        enemy = ATTACKER
        friendly = [DEFENDER, KING]

    else:
        return captured

    directions = [(-1,0), (1,0), (0,-1), (0,1)]

    for dr, dc in directions:
        adj_r = row + dr
        adj_c = col + dc
        behind_r = row + 2 * dr
        behind_c = col + 2 * dc

        if not (0 <= adj_r < SIZE and 0 <= adj_c < SIZE):
            continue

        if board[adj_r][adj_c] != enemy:
            continue

        if not (0 <= behind_r < SIZE and 0 <= behind_c < SIZE):
            continue

        if (
            board[behind_r][behind_c] in friendly
            or (behind_r, behind_c) == THRONE_POS
            or (behind_r, behind_c) in CORNERS
        ):
            captured.append((adj_r, adj_c, board[adj_r][adj_c]))
            board[adj_r][adj_c] = EMPTY

    return captured


# ---------------- APPLY MOVE ----------------

def apply_move(board, player, r, c, nr, nc):
    valid, msg = is_valid_move(board, player, r, c, nr, nc)
    if not valid:
        print(msg)
        return False

    piece = board[r][c]

    if is_in_sandwich(board, nr, nc, piece):
        print("Cannot stop in sandwich!")
        return False

    board[nr][nc] = piece
    board[r][c] = EMPTY

    captured_pieces = check_capture(board, nr, nc)

    for cr, cc, piece_type in captured_pieces:
        if piece_type == ATTACKER:
            print(f"Attacker captured at ({cr}, {cc})!")
        elif piece_type == DEFENDER:
            print(f"Defender captured at ({cr}, {cc})!")

    return True


# ---------------- KING RULES ----------------
def king_escaped(board):
    for r, c in CORNERS:
        if board[r][c] == KING:
            return True
    return False

def is_king_captured(board):

    king_row = -1
    king_col = -1

    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == KING:
                king_row = r
                king_col = c
                break

        #--------------------    
        if king_row != -1:
            break 
        #-------------------       

    if king_row == -1:
        return True

    up_blocked = False
    down_blocked = False
    left_blocked = False
    right_blocked = False

    # UP
    if not (0 <= king_row-1 < SIZE):
        up_blocked = True
    elif board[king_row-1][king_col] == ATTACKER:
        up_blocked = True
    elif (king_row-1, king_col) == THRONE_POS:
        up_blocked = True
    elif (king_row-1, king_col) in CORNERS:
        up_blocked = True

    # DOWN
    if not (0 <= king_row+1 < SIZE):
        down_blocked = True
    elif board[king_row+1][king_col] == ATTACKER:
        down_blocked = True
    elif (king_row+1, king_col) == THRONE_POS:
        down_blocked = True
    elif (king_row+1, king_col) in CORNERS:
        down_blocked = True

    # LEFT
    if not (0 <= king_col-1 < SIZE):
        left_blocked = True
    elif board[king_row][king_col-1] == ATTACKER:
        left_blocked = True
    elif (king_row, king_col-1) == THRONE_POS:
        left_blocked = True
    elif (king_row, king_col-1) in CORNERS:
        left_blocked = True

    # RIGHT
    if not (0 <= king_col+1 < SIZE):
        right_blocked = True
    elif board[king_row][king_col+1] == ATTACKER:
        right_blocked = True
    elif (king_row, king_col+1) == THRONE_POS:
        right_blocked = True
    elif (king_row, king_col+1) in CORNERS:
        right_blocked = True

    closed = 0
    if up_blocked: closed += 1
    if down_blocked: closed += 1
    if left_blocked: closed += 1
    if right_blocked: closed += 1

    if (king_row, king_col) in CORNERS:
        required = 2
    elif king_row == 0 or king_row == SIZE-1 or king_col == 0 or king_col == SIZE-1:
        required = 3
    else:
        required = 4

    return closed >= required

# ---------------- GAME CONTROLLER ----------------
def Game_Controller():
    board = create_board()
    turn = ATTACKER

    while True:
        print_board(board)

        print(f"\n--- {'Attacker' if turn == ATTACKER else 'Defender'}'s Turn ---")

        try:
            r = int(input("Start row: "))
            c = int(input("Start col: "))
            nr = int(input("End row: "))
            nc = int(input("End col: "))
        except:
            print("Invalid input!")
            continue

        if not apply_move(board, turn, r, c, nr, nc):
            continue

        if king_escaped(board):
            print_board(board)
            print("King Wins! Defenders Win!")
            break

        if is_king_captured(board):
            print_board(board)
            print("Attackers Win!")
            break

        turn = DEFENDER if turn == ATTACKER else ATTACKER



# ---------------- RUN ----------------
if __name__ == "__main__":
    Game_Controller()
