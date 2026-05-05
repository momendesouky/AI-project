import copy
from typing import Tuple, List, Optional

EMPTY = '.'
ATTACKER = 'A'
DEFENDER = 'D'
KING = 'K'
CORNER = 'X'

SIZE = 11
THRONE_POS = (SIZE // 2, SIZE // 2)
CORNERS = [(0, 0), (0, SIZE - 1), (SIZE - 1, 0), (SIZE - 1, SIZE - 1)]

DIFFICULTY_EASY = 1
DIFFICULTY_MEDIUM = 2
DIFFICULTY_HARD = 3

TT_EXACT = 0
TT_LOWER = 1
TT_UPPER = 2


def create_board():
    board = [[EMPTY] * SIZE for _ in range(SIZE)]
    mid = SIZE // 2

    board[mid][mid] = KING

    defenders = [
        (mid - 1, mid), (mid + 1, mid), (mid, mid - 1), (mid, mid + 1),
        (mid - 2, mid), (mid + 2, mid), (mid, mid - 2), (mid, mid + 2),
        (mid - 1, mid - 1), (mid - 1, mid + 1),
        (mid + 1, mid - 1), (mid + 1, mid + 1),
    ]
    for r, c in defenders:
        board[r][c] = DEFENDER

    attackers = [

        (0, mid - 2), (0, mid - 1), (0, mid), (0, mid + 1), (0, mid + 2),
        (1, mid),

        (SIZE - 1, mid - 2), (SIZE - 1, mid - 1), (SIZE - 1, mid), (SIZE - 1, mid + 1), (SIZE - 1, mid + 2),
        (SIZE - 2, mid),

        (mid - 2, 0), (mid - 1, 0), (mid, 0), (mid + 1, 0), (mid + 2, 0),
        (mid, 1),

        (mid - 2, SIZE - 1), (mid - 1, SIZE - 1), (mid, SIZE - 1), (mid + 1, SIZE - 1), (mid + 2, SIZE - 1),
        (mid, SIZE - 2)
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
    # Check bounds
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


def is_in_sandwich(board, row, col, piece):
    if piece == ATTACKER:
        enemy = [DEFENDER, KING]
    elif piece == DEFENDER:
        enemy = [ATTACKER]
    else:
        return False

    if 0 <= col - 1 < SIZE and 0 <= col + 1 < SIZE:
        if board[row][col - 1] in enemy and board[row][col + 1] in enemy:
            return True

    if 0 <= row - 1 < SIZE and 0 <= row + 1 < SIZE:
        if board[row - 1][col] in enemy and board[row + 1][col] in enemy:
            return True

    return False


def check_capture(board, row, col):
    current = board[row][col]
    captured = []

    if current == ATTACKER:
        enemy = DEFENDER
        friendly = [ATTACKER]
    elif current == DEFENDER:
        enemy = ATTACKER
        friendly = [DEFENDER]
    elif current == KING:
        enemy = ATTACKER
        friendly = []    
    else:
        return captured

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

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

        if board[adj_r][adj_c] == KING:
            continue

        if (
                board[behind_r][behind_c] in friendly
                or (behind_r, behind_c) == THRONE_POS
                or (behind_r, behind_c) in CORNERS
        ):
            captured.append((adj_r, adj_c, board[adj_r][adj_c]))
            board[adj_r][adj_c] = EMPTY

    return captured


def apply_move(board, player, r, c, nr, nc, silent=False):
    valid, msg = is_valid_move(board, player, r, c, nr, nc)
    if not valid:
        if not silent:
            print(f"  Invalid: {msg}")
        return False, []

    piece = board[r][c]

    if is_in_sandwich(board, nr, nc, piece):
        if not silent:
            print("  Cannot stop in sandwich!")
        return False, []

    board[nr][nc] = piece
    board[r][c] = EMPTY

    captured_pieces = check_capture(board, nr, nc)

    if not silent:
        for cr, cc, piece_type in captured_pieces:
            if piece_type == ATTACKER:
                print(f"   Attacker captured at ({cr}, {cc})!")
            elif piece_type == DEFENDER:
                print(f"   Defender captured at ({cr}, {cc})!")

    return True, captured_pieces

def king_escaped(board):
    for r, c in CORNERS:
        if board[r][c] == KING:
            return True
    return False



def is_king_captured(board):
    king_pos = None

    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == KING:
                king_pos = (r, c)
                break
        if king_pos:
            break

    if not king_pos:
        return True

    r, c = king_pos

    directions = [(-1,0),(1,0),(0,-1),(0,1)]

    block_count = 0

    for dr, dc in directions:
        nr, nc = r + dr, c + dc

        if 0 <= nr < SIZE and 0 <= nc < SIZE:

            if board[nr][nc] == ATTACKER:
                block_count += 1

            elif (nr, nc) in CORNERS:
                block_count += 1

    if (r, c) in CORNERS:
        required = 2
    elif r == 0 or r == SIZE-1 or c == 0 or c == SIZE-1:
        required = 3
    else:
        required = 4

    return block_count >= required

def evaluate_position(board: List[List[str]], player: str) -> float:
    attacker_count = 0
    defender_count = 0
    king_pos = None

    for r in range(SIZE):
        for c in range(SIZE):
            piece = board[r][c]

            if piece == ATTACKER:
                attacker_count += 1
            elif piece == DEFENDER:
                defender_count += 1
            elif piece == KING:
                king_pos = (r, c)

    if is_king_captured(board):
        return 10000 if player == ATTACKER else -10000

    if king_escaped(board):
        return 10000 if player == DEFENDER else -10000

    if king_pos is None:
        return 10000 if player == ATTACKER else -10000

    kr, kc = king_pos

    min_corner_distance = min(
        abs(kr - cr) + abs(kc - cc)
        for cr, cc in CORNERS
    )
    king_escape_score = -min_corner_distance * 40

    adjacent_attackers = 0
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dr, dc in directions:
        nr, nc = kr + dr, kc + dc
        if 0 <= nr < SIZE and 0 <= nc < SIZE:
            if board[nr][nc] == ATTACKER:
                adjacent_attackers += 1

    encirclement_score = adjacent_attackers * 250

    sandwich_score = 0

    for r in range(SIZE):
        for c in range(SIZE):
            piece = board[r][c]

            if piece == EMPTY:
                continue
            if (r, c) in CORNERS:
                continue

            if is_in_sandwich(board, r, c, piece):
                if piece == ATTACKER:
                    sandwich_score -= 40
                elif piece in (DEFENDER, KING):
                    sandwich_score += 40

    throne_score = 0

    if abs(kr - THRONE_POS[0]) + abs(kc - THRONE_POS[1]) <= 1:
        throne_score -= 30

    if (kr, kc) in CORNERS:
        throne_score += 500

    total_score = (
            king_escape_score * 1.2 +
            encirclement_score * 2.0 +
            sandwich_score * 1.5 +
            throne_score * 1.0
    )

    if player == DEFENDER:
        total_score *= -1

    return total_score


from typing import List, Tuple, Dict

Piece = Tuple[int, int]


def build_piece_lists(board: List[List[str]]):
    attackers = []
    defenders = []
    king = None

    for r in range(SIZE):
        for c in range(SIZE):
            piece = board[r][c]

            if piece == ATTACKER:
                attackers.append((r, c))

            elif piece == DEFENDER:
                defenders.append((r, c))

            elif piece == KING:
                king = (r, c)

    return attackers, defenders, king


def get_all_moves(
        board: List[List[str]],
        player: str,
        pieces: List[Tuple[int, int]]
) -> List[Tuple[int, int, int, int]]:
    moves = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for r, c in pieces:
        piece = board[r][c]

        if player == ATTACKER and piece != ATTACKER:
            continue
        if player == DEFENDER and piece not in (DEFENDER, KING):
            continue

        for dr, dc in directions:
            nr, nc = r + dr, c + dc

            while 0 <= nr < SIZE and 0 <= nc < SIZE:
                # Normal pieces can move only to EMPTY cells.
                # The KING can also move to CORNER cells to escape.
                if board[nr][nc] == EMPTY:
                    moves.append((r, c, nr, nc))
                elif piece == KING and (nr, nc) in CORNERS:
                    moves.append((r, c, nr, nc))
                    break
                else:
                    break

                nr += dr
                nc += dc

    return moves


def _board_to_hash(board: List[List[str]]) -> int:
    return hash(tuple(tuple(row) for row in board))


def undo_move(board, r, c, nr, nc, captured_pieces, silent=True):
    piece = board[nr][nc]

    board[r][c] = piece

    # If the destination was a corner, restore it as CORNER after undo.
    # Otherwise it becomes EMPTY.
    if (nr, nc) in CORNERS:
        board[nr][nc] = CORNER
    else:
        board[nr][nc] = EMPTY

    for cr, cc, piece_type in captured_pieces:
        board[cr][cc] = piece_type

        if not silent:
            if piece_type == ATTACKER:
                print(f"  ✓ Attacker restored at ({cr}, {cc})!")
            elif piece_type == DEFENDER:
                print(f"  ✓ Defender restored at ({cr}, {cc})!")


class HnefataflAI:

    def __init__(self, difficulty: int = DIFFICULTY_MEDIUM):
        self.difficulty = difficulty
        self.nodes_evaluated = 0
        self.nodes_pruned = 0
        self.transposition_table = {}
        self.tt_hits = 0

    def get_best_move(self, board, player):
        self.nodes_evaluated = 0
        self.nodes_pruned = 0
        self.transposition_table.clear()
        self.tt_hits = 0

        attackers, defenders, king = build_piece_lists(board)
        pieces = (
            attackers if player == ATTACKER
            else defenders + ([king] if king else [])
        )

        valid_moves = get_all_moves(board, player, pieces)
        if not valid_moves:
            return None

        best_move = None
        best_value = float('-inf')
        opponent = DEFENDER if player == ATTACKER else ATTACKER

        for move in valid_moves:
            from_r, from_c, to_r, to_c = move

            success, captured_pieces = apply_move(
                board, player, from_r, from_c, to_r, to_c,
            silent=True)
            if not success:
                continue

            value = self._alpha_beta(
                board,
                self.difficulty - 1,
                float('-inf'),
                float('inf'),
                is_maximizing=False,
                current_player=opponent,
                root_player=player
            )

            undo_move(board, from_r, from_c, to_r, to_c, captured_pieces)

            if value > best_value:
                best_value = value
                best_move = move

        return best_move

    def _alpha_beta(
            self,
            board: List[List[str]],
            depth: int,
            alpha: float,
            beta: float,
            is_maximizing: bool,
            current_player: str,
            root_player: str
    ) -> float:

        board_hash = _board_to_hash(board)

        if board_hash in self.transposition_table:
            cached_depth, cached_value, cached_flag = self.transposition_table[board_hash]
            if cached_depth >= depth:
                self.tt_hits += 1
                if cached_flag == TT_EXACT:
                    return cached_value
                elif cached_flag == TT_LOWER:
                    alpha = max(alpha, cached_value)
                elif cached_flag == TT_UPPER:
                    beta = min(beta, cached_value)
                if alpha >= beta:
                    return cached_value

        self.nodes_evaluated += 1

        if depth == 0:
            result = evaluate_position(board, root_player)
            self.transposition_table[board_hash] = (depth, result, TT_EXACT)
            return result

        opponent = DEFENDER if current_player == ATTACKER else ATTACKER

        attackers, defenders, king = build_piece_lists(board)
        pieces = (
            attackers if current_player == ATTACKER
            else defenders + ([king] if king else [])
        )

        if is_maximizing:
            max_eval = float('-inf')
            original_alpha = alpha

            # BUG 5 FIX: pass pieces list instead of opponent string
            moves = get_all_moves(board, current_player, pieces)

            if not moves:
                # BUG 8 FIX: use root_player not current_player
                result = evaluate_position(board, root_player)
                self.transposition_table[board_hash] = (depth, result, TT_EXACT)
                return result

            for move in moves:
                from_r, from_c, to_r, to_c = move

                # BUG 6 FIX: use apply_move with correct signature
                success, captured_pieces = apply_move(
                    board, current_player, from_r, from_c, to_r, to_c,
                silent=True)
                if not success:
                    continue

                eval_value = self._alpha_beta(
                    board, depth - 1, alpha, beta,
                    is_maximizing=False,
                    current_player=opponent,
                    root_player=root_player
                )

                # BUG 7 FIX: pass captured_pieces not old captured
                undo_move(board, from_r, from_c, to_r, to_c, captured_pieces)

                max_eval = max(max_eval, eval_value)
                alpha = max(alpha, eval_value)

                if alpha >= beta:
                    self.nodes_pruned += 1
                    break

            # BUG 9 FIX: store with correct flag
            flag = TT_EXACT if max_eval > original_alpha else TT_UPPER
            self.transposition_table[board_hash] = (depth, max_eval, flag)
            return max_eval

        else:
            min_eval = float('inf')
            original_beta = beta

            # BUG 10 FIX: pass pieces list to get_all_moves
            moves = get_all_moves(board, current_player, pieces)

            if not moves:
                result = evaluate_position(board, root_player)
                # BUG 13 FIX: store with flag
                self.transposition_table[board_hash] = (depth, result, TT_EXACT)
                return result

            for move in moves:
                from_r, from_c, to_r, to_c = move

                # BUG 11 FIX: use current_player not undefined player
                success, captured_pieces = apply_move(
                    board, current_player, from_r, from_c, to_r, to_c,silent=True
                )
                if not success:
                    continue

                eval_value = self._alpha_beta(
                    board, depth - 1, alpha, beta,
                    is_maximizing=True,
                    current_player=opponent,
                    root_player=root_player
                )

                undo_move(board, from_r, from_c, to_r, to_c, captured_pieces)

                min_eval = min(min_eval, eval_value)
                beta = min(beta, eval_value)

                if alpha >= beta:
                    self.nodes_pruned += 1
                    break

            # BUG 14 FIX: store with correct flag
            flag = TT_EXACT if min_eval < original_beta else TT_LOWER
            self.transposition_table[board_hash] = (depth, min_eval, flag)
            return min_eval


    # for testing purpose ana saybaha 4waya
    def get_statistics(self) -> dict:
        return {
            "nodes_evaluated": self.nodes_evaluated,
            "nodes_pruned": self.nodes_pruned,
            "transposition_hits": self.tt_hits,
            "transposition_table_size": len(self.transposition_table),
            "pruning_efficiency": (
                self.nodes_pruned / self.nodes_evaluated
                if self.nodes_evaluated > 0 else 0
            )
        }


def Game_Controller():
    """
    Original human vs human game mode.
    """
    board = create_board()
    turn = ATTACKER

    print("\n" + "=" * 60)
    print("HNEFATAFL: Human vs Human")
    print("=" * 60 + "\n")

    while True:
        print_board(board)

        print(f"\n--- {('Attacker (Black)' if turn == ATTACKER else 'Defender (White)')} Turn ---")

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
            print("\n" + "=" * 60)
            print(" Defenders Win! King Escaped!")
            print("=" * 60)
            break

        if is_king_captured(board):
            print_board(board)
            print("\n" + "=" * 60)
            print(" Attackers Win! King Captured!")
            print("=" * 60)
            break

        turn = DEFENDER if turn == ATTACKER else ATTACKER


def Game_Controller_With_AI(ai_player: str = ATTACKER, difficulty: int = DIFFICULTY_MEDIUM):
    """
    Human vs AI game mode.

    Args:
        ai_player: ATTACKER or DEFENDER (which side AI plays)
        difficulty: DIFFICULTY_EASY (1), DIFFICULTY_MEDIUM (3), or DIFFICULTY_HARD (5)
    """
    board = create_board()
    turn = ATTACKER

    # Initialize AI with chosen difficulty
    ai = HnefataflAI(difficulty=difficulty)

    difficulty_name = {
        DIFFICULTY_EASY: "Easy",
        DIFFICULTY_MEDIUM: "Medium",
        DIFFICULTY_HARD: "Hard"
    }

    player_name = "Attacker (Black)" if ai_player == ATTACKER else "Defender (White)"
    human_name = "Defender (White)" if ai_player == ATTACKER else "Attacker (Black)"

    print("\n" + "=" * 60)
    print(f"HNEFATAFL: Human vs AI ({difficulty_name[difficulty]})")
    print(f"AI playing as: {player_name}")
    print(f"You playing as: {human_name}")
    print("=" * 60 + "\n")

    while True:
        print_board(board)

        # Check win conditions
        if king_escaped(board):
            print("\n" + "=" * 60)
            print(" Defenders Win! King Escaped!")
            print("=" * 60)
            break

        if is_king_captured(board):
            print("\n" + "=" * 60)
            print(" Attackers Win! King Captured!")
            print("=" * 60)
            break

        print(f"\n--- {('Attacker (Black)' if turn == ATTACKER else 'Defender (White)')} Turn ---")

        # Determine if AI or human turn
        if turn == ai_player:
            # AI Turn
            print("AI is thinking...")
            move = ai.get_best_move(board, turn)

            if move is None:
                print("No valid moves available!")
                turn = DEFENDER if turn == ATTACKER else ATTACKER
                continue

            from_r, from_c, to_r, to_c = move
            print(f"AI moves from ({from_r}, {from_c}) to ({to_r}, {to_c})")

            apply_move(board, turn, from_r, from_c, to_r, to_c)

        else:
            try:
                r = int(input("Start row: "))
                c = int(input("Start col: "))
                nr = int(input("End row: "))
                nc = int(input("End col: "))
            except:
                print("Invalid input!")
                continue

            success, _ = apply_move(board, turn, r, c, nr, nc)
            if not success:
                continue


        turn = DEFENDER if turn == ATTACKER else ATTACKER


# ============================================================================
# MAIN MENU & ENTRY POINT
# ============================================================================

def main():
    """Main menu for game mode selection."""
    print("\n" + "=" * 60)
    print("HNEFATAFL: Viking Chess with AI")
    print("=" * 60)
    print("\nGame Modes:")
    print("1. Human vs Human")
    print("2. Human vs AI (you play as Attacker)")
    print("3. Human vs AI (you play as Defender)")

    choice = input("\nSelect mode (1-3): ").strip()

    if choice == "1":
        Game_Controller()

    elif choice == "2":
        difficulty_input = input("AI Difficulty (1=Easy, 3=Medium, 5=Hard): ").strip()
        difficulty = int(difficulty_input) if difficulty_input in ['1', '3', '5'] else DIFFICULTY_MEDIUM
        Game_Controller_With_AI(ai_player=ATTACKER, difficulty=difficulty)

    elif choice == "3":
        difficulty_input = input("AI Difficulty (1=Easy, 3=Medium, 5=Hard): ").strip()
        difficulty = int(difficulty_input) if difficulty_input in ['1', '3', '5'] else DIFFICULTY_MEDIUM
        Game_Controller_With_AI(ai_player=DEFENDER, difficulty=difficulty)

    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()
