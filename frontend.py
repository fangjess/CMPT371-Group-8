import pygame

WIDTH, HEIGHT = 800, 600
GRID_SIZE = 10
CELL_SIZE = 600 // GRID_SIZE
FPS = 32

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Coin Clicker")
font = pygame.font.SysFont(None, 32)
clock = pygame.time.Clock()

# UI state
coins = set()
player_scores = {}
local_player_id = None
send_click_fn = None

in_lobby = False #change to False if want to start in game screen
players_ready = {}
countdown_time = None

def update_coin_list(coin_data):
    coins.clear()
    for c in coin_data:
        coins.add((c["x"], c["y"]))

def update_player_list(player_data):
    player_scores.clear()
    for entry in player_data:
        player_scores[entry["player_id"]] = entry["score"]

def remove_coin_from_ui(x, y, player_id):
    coins.discard((x, y))
    player_scores[player_id] = player_scores.get(player_id, 0) + 1
    print(f"Coin at ({x}, {y}) taken by {player_id}")

def add_player_to_ui(player_id):
    if player_id not in player_scores:
        player_scores[player_id] = 0
        print(f"Player {player_id} joined.")

def draw_game():
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, (50, 50, 50), rect, 1)

    for x, y in coins:
        rect = pygame.Rect(x * CELL_SIZE + 10, y * CELL_SIZE + 10, CELL_SIZE - 20, CELL_SIZE - 20)
        pygame.draw.ellipse(screen, (255, 215, 0), rect)

    header = font.render("Players:", True, (0, 0, 0))
    screen.blit(header, (610, 5))
    y_offset = 5 + 30
    for pid, score in player_scores.items():
        color = (0, 0, 0)
        text = font.render(f"{pid}: {score}", True, color)
        screen.blit(text, (610, y_offset))
        y_offset += 20

def draw_lobby(ready_pressed):
    title = font.render("Lobby - Waiting for Players", True, (0, 0, 0))
    title_rect = title.get_rect(center=(WIDTH // 2, 50))
    screen.blit(title, title_rect)

    y = 100
    for pid, is_ready in players_ready.items():
        color = (0, 255, 0) if is_ready else (200, 0, 0)
        text = font.render(f"{pid} - {'Ready' if is_ready else 'Not Ready'}", True, color)
        text_rect = text.get_rect(center=(WIDTH // 2, y))
        screen.blit(text, text_rect)
        y += 30

    # Draw Ready Button
    if not ready_pressed:
        button_rect = pygame.Rect(WIDTH // 2 - 50, 300, 100, 40)
        pygame.draw.rect(screen, (0, 128, 255), button_rect)
        label = font.render("Ready", True, (0, 0, 0))
        label_rect = label.get_rect(center=button_rect.center)
        screen.blit(label, label_rect)
    elif countdown_time:
        text = font.render(f"Game starts in: {countdown_time}s", True, (200, 200, 0))
        text_rect = text.get_rect(center=(WIDTH // 2, 310))
        screen.blit(text, text_rect)

def update_lobby_ui(ready_dict):
    global players_ready
    players_ready = ready_dict

def start_countdown(seconds):
    global countdown_time
    countdown_time = seconds

def switch_to_game_screen():
    global in_lobby
    in_lobby = False


def run_game(send_click, player_id):
    global send_click_fn, local_player_id, in_lobby
    send_click_fn = send_click
    local_player_id = player_id
    ready_pressed = False

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if not in_lobby:
                    gx, gy = mx // CELL_SIZE, my // CELL_SIZE
                    if (gx, gy) in coins and send_click_fn:
                        send_click_fn(gx, gy)
                elif in_lobby and not ready_pressed:
                    # Check if Ready button is clicked
                    if WIDTH // 2 - 50 <= mx <= WIDTH // 2 + 50 and 300 <= my <= 340:
                        # send_ready() #Uncomment when send ready is implemented in client
                        ready_pressed = True

        screen.fill((255, 255, 255))
        if not in_lobby:
            draw_game()
        else:
            draw_lobby(ready_pressed)

        pygame.display.flip()

    pygame.quit()
