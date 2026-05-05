import pygame
import copy
import os

from part1_2_3 import (
    create_board,
    apply_move,
    is_valid_move,
    king_escaped,
    is_king_captured,
    HnefataflAI,
    ATTACKER,
    DEFENDER,
    KING,
    SIZE,
    CORNERS,
    THRONE_POS,
    DIFFICULTY_EASY,
    DIFFICULTY_MEDIUM,
    DIFFICULTY_HARD
)

CELL = 60
GAP = 1
MARGIN = 25
BOTTOM_PANEL = 100

WIDTH = SIZE * CELL + MARGIN * 2
HEIGHT = SIZE * CELL + MARGIN * 2 + BOTTOM_PANEL

ASSET_DIR = "assets"

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hnefatafl")

title_font = pygame.font.SysFont("Georgia", 42, bold=True)
font = pygame.font.SysFont("Segoe UI", 26, bold=True)
small_font = pygame.font.SysFont("Segoe UI", 20)

BG = (22, 22, 22)
BOARD_BG = (220, 200, 165)
PANEL = (35, 35, 40)
GOLD = (214, 170, 96)
WHITE = (245, 245, 245)
GREEN = (70, 210, 120)



def load_img(name):
    path = os.path.join(ASSET_DIR, name)
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.smoothscale(img, (CELL - GAP, CELL - GAP))


tile_img = load_img("basic_tile_plain.png")
special_img = load_img("special_tile.png")
attacker_pattern_img = load_img("attacker_pattern_tile.png")
defender_pattern_img = load_img("defender_pattern_tile.png")

attacker_img = load_img("attacker_piece.png")
defender_img = load_img("defender_piece.png")
king_img = load_img("king_piece.png")

START_BOARD = create_board()


def switch_turn(turn):
    return DEFENDER if turn == ATTACKER else ATTACKER


def check_winner(board):
    if king_escaped(board):
        return "Defenders win!"

    if is_king_captured(board):
        return "Attackers win!"

    return None


def mouse_to_cell(pos):
    x, y = pos
    col = (x - MARGIN) // CELL
    row = (y - MARGIN) // CELL

    if 0 <= row < SIZE and 0 <= col < SIZE:
        return int(row), int(col)

    return None


def draw_text(text, x, y, color=WHITE, small=False, title=False):
    used_font = title_font if title else (small_font if small else font)
    label = used_font.render(text, True, color)
    screen.blit(label, (x, y))


def draw_button(text, rect, color=(70, 75, 90)):
    mouse_pos = pygame.mouse.get_pos()

    if rect.collidepoint(mouse_pos):
        color = (95, 105, 125)

    pygame.draw.rect(screen, color, rect, border_radius=14)
    pygame.draw.rect(screen, GOLD, rect, 2, border_radius=14)

    label = font.render(text, True, WHITE)
    screen.blit(label, label.get_rect(center=rect.center))


def choose_menu():
    mode = None
    human_player = ATTACKER
    difficulty = DIFFICULTY_MEDIUM

    step = "mode"
    running_menu = True

    while running_menu:
        screen.fill(BG)

        draw_text("Hnefatafl", 275, 70, GOLD, title=True)
        draw_text("Viking Chess Game", 285, 120, WHITE, small=True)

        if step == "mode":
            draw_text("Choose Game Mode", 245, 170)

            btn_hvh = pygame.Rect(220, 250, 320, 60)
            btn_hvai = pygame.Rect(220, 330, 320, 60)

            draw_button("Human vs Human", btn_hvh)
            draw_button("Human vs AI", btn_hvai)

        elif step == "side":
            draw_text("Choose Your Side", 250, 170)

            btn_attacker = pygame.Rect(220, 250, 320, 60)
            btn_defender = pygame.Rect(220, 330, 320, 60)

            draw_button("Play as Attacker", btn_attacker)
            draw_button("Play as Defender", btn_defender)

        elif step == "difficulty":
            draw_text("Choose AI Difficulty", 235, 160)

            btn_easy = pygame.Rect(220, 240, 320, 55)
            btn_medium = pygame.Rect(220, 310, 320, 55)
            btn_hard = pygame.Rect(220, 380, 320, 55)

            draw_button("Easy", btn_easy)
            draw_button("Medium", btn_medium)
            draw_button("Hard", btn_hard)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos

                if step == "mode":
                    if btn_hvh.collidepoint(pos):
                        mode = "hvh"
                        running_menu = False
                    elif btn_hvai.collidepoint(pos):
                        mode = "hvai"
                        step = "side"

                elif step == "side":
                    if btn_attacker.collidepoint(pos):
                        human_player = ATTACKER
                        step = "difficulty"
                    elif btn_defender.collidepoint(pos):
                        human_player = DEFENDER
                        step = "difficulty"

                elif step == "difficulty":
                    if btn_easy.collidepoint(pos):
                        difficulty = DIFFICULTY_EASY
                        running_menu = False
                    elif btn_medium.collidepoint(pos):
                        difficulty = DIFFICULTY_MEDIUM
                        running_menu = False
                    elif btn_hard.collidepoint(pos):
                        difficulty = DIFFICULTY_HARD
                        running_menu = False

    return mode, human_player, difficulty


def get_piece_image(piece):
    if piece == ATTACKER:
        return attacker_img
    elif piece == DEFENDER:
        return defender_img
    elif piece == KING:
        return king_img
    return None


def animate_move(board, piece, start_cell, end_cell):
    piece_img = get_piece_image(piece)

    if piece_img is None:
        return

    sr, sc = start_cell
    er, ec = end_cell

    
    original_piece = board[sr][sc]
    board[sr][sc] = '.'

    start_x = MARGIN + sc * CELL + GAP // 2
    start_y = MARGIN + sr * CELL + GAP // 2

    end_x = MARGIN + ec * CELL + GAP // 2
    end_y = MARGIN + er * CELL + GAP // 2

    steps = 15

    for i in range(steps + 1):
        t = i / steps
        x = start_x + (end_x - start_x) * t
        y = start_y + (end_y - start_y) * t

        draw_board(board, selected=None, valid_moves=[], turn=turn,
                   winner=None, mode=mode, human_player=human_player)

        screen.blit(piece_img, (x, y))
        pygame.display.flip()
        pygame.time.delay(15)

    
    board[sr][sc] = original_piece
        


def is_piece_for_player(piece, player):
    if player == ATTACKER:
        return piece == ATTACKER

    if player == DEFENDER:
        return piece == DEFENDER or piece == KING

    return False


def get_valid_destinations(board, player, r, c):
    valid_cells = []

    for nr in range(SIZE):
        for nc in range(SIZE):
            valid, _ = is_valid_move(board, player, r, c, nr, nc)

            if valid:
                valid_cells.append((nr, nc))

    return valid_cells


def get_base_tile_image(r, c):
    if (r, c) in CORNERS or (r, c) == THRONE_POS:
        return special_img

    start_piece = START_BOARD[r][c]

    if start_piece == ATTACKER:
        return attacker_pattern_img

    if start_piece == DEFENDER or start_piece == KING:
        return defender_pattern_img

    return tile_img


def draw_tile_image(image, rect):
    rounded_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

    pygame.draw.rect(
        rounded_surface,
        (255, 255, 255, 255),
        pygame.Rect(0, 0, rect.width, rect.height),
        border_radius=8
    )

    img = pygame.transform.smoothscale(image, (rect.width, rect.height))

    img_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    img_surface.blit(img, (0, 0))
    img_surface.blit(rounded_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    screen.blit(img_surface, rect)

def get_hover_cell():
    mouse_pos = pygame.mouse.get_pos()
    return mouse_to_cell(mouse_pos)


def draw_hover_shade(rect):
    shade = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    shade.fill((255, 255, 255, 35))  # shading فاتح خفيف
    screen.blit(shade, rect)


def draw_board(board, selected, valid_moves, turn, winner, mode, human_player, message=""):
    screen.fill(BG)
    hover_cell = get_hover_cell()

    board_panel = pygame.Rect(
        MARGIN - 10,
        MARGIN - 10,
        SIZE * CELL + 20,
        SIZE * CELL + 20
    )

    pygame.draw.rect(screen, BOARD_BG, board_panel, border_radius=8)

    for r in range(SIZE):
        for c in range(SIZE):
            rect = pygame.Rect(
                MARGIN + c * CELL + GAP // 2,
                MARGIN + r * CELL + GAP // 2,
                CELL - GAP,
                CELL - GAP
            )

            draw_tile_image(get_base_tile_image(r, c), rect)
            
            hover_cell = get_hover_cell()
            if hover_cell == (r, c):
                draw_hover_shade(rect)

            if (r, c) in valid_moves:
                pygame.draw.rect(screen, (160, 105, 55), rect, 4, border_radius=8)

            if selected == (r, c):
                pygame.draw.rect(screen, GOLD, rect, 5, border_radius=8)

            piece = board[r][c]

            if piece == ATTACKER:
                screen.blit(attacker_img, rect)

            elif piece == DEFENDER:
                screen.blit(defender_img, rect)

            elif piece == KING:
                screen.blit(king_img, rect)

    info_y = MARGIN + SIZE * CELL + 22

    pygame.draw.rect(
        screen,
        PANEL,
        pygame.Rect(MARGIN, info_y - 10, WIDTH - MARGIN * 2, 70),
        border_radius=14
    )

    if winner:
        main_text = winner.upper()
    elif message:
        main_text = message
    else:
        if turn == ATTACKER:
            main_text = "ATTACKER'S TURN"
        else:
            main_text = "DEFENDER'S TURN"

    label = font.render(main_text, True, GOLD)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, info_y + 22)))

   
    pygame.display.flip()


mode, human_player, difficulty = choose_menu()

board = create_board()
turn = ATTACKER
selected = None
valid_moves = []
winner = None
message = ""
message_timer = 0

ai = None
ai_player = None

if mode == "hvai":
    ai_player = switch_turn(human_player)
    ai = HnefataflAI(difficulty)

clock = pygame.time.Clock()
running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and winner is None:

            if mode == "hvh" or turn == human_player:

                cell = mouse_to_cell(event.pos)

                if cell:
                    row, col = cell
                    piece = board[row][col]

                    if selected is None:
                        if is_piece_for_player(piece, turn):
                            selected = (row, col)
                            valid_moves = get_valid_destinations(board, turn, row, col)

                    else:
                        r, c = selected
                        nr, nc = cell

                        if (nr, nc) in valid_moves:

                            moving_piece = board[r][c]
                            animate_move(board, moving_piece, (r, c), (nr, nc))

                            success, captured = apply_move(board, turn, r, c, nr, nc, silent=True)

                            if captured:
                                message = "CAPTURED!"
                                message_timer = 30

                            if success:
                                winner = check_winner(board)

                                if winner is None:
                                    turn = switch_turn(turn)

                        selected = None
                        valid_moves = []

    if mode == "hvai" and turn == ai_player and winner is None:
        pygame.time.delay(300)

        move = ai.get_best_move(copy.deepcopy(board), ai_player)

        if move:
            r, c, nr, nc = move

            moving_piece = board[r][c]

            animate_move(board, moving_piece, (r, c), (nr, nc))

            success, captured = apply_move(board, ai_player, r, c, nr, nc, silent=True)

            if captured:
                message = "CAPTURED!"
                message_timer = 30

            if success:
                winner = check_winner(board)

                if winner is None:
                    turn = switch_turn(turn)

    if message_timer > 0:
        message_timer -= 1
    else:
        message = ""

    draw_board(board, selected, valid_moves, turn, winner, mode, human_player,message)

    clock.tick(30)




pygame.quit()