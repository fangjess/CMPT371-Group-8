import pygame

WIDTH, HEIGHT = 800, 600
GRID_SIZE = 10
CELL_SIZE = 600 // GRID_SIZE
FPS = 32

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Coin Clicker")
font = pygame.font.SysFont(None, 24)
clock = pygame.time.Clock()

# UI state
coins = set()
player_scores = {}
local_player_id = None
send_click_fn = None

in_lobby = True #change to False if don't want to start in lobby screen
in_win_screen =False #change to true if want to test win screen
restart_clicked = False
winner_id = None #change winner_id if want to test the displayed name

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

    title = font.render("FIRST TO 10 WINS", True, (0, 0, 0))
    screen.blit(title, (610, 5))
    header = font.render("Players:", True, (0, 0, 0))
    screen.blit(header, (610, 30))
    y_offset = 60
    for pid, score in player_scores.items():
        color = (0, 0, 0)
        text = font.render(f"{pid}: {score}", True, color)
        screen.blit(text, (610, y_offset))
        y_offset += 20

def draw_lobby(ready_pressed):
    title = font.render("Lobby - Press Ready to start", True, (0, 0, 0))
    title_rect = title.get_rect(center=(WIDTH // 2, 50))
    screen.blit(title, title_rect)

    # Draw Ready Button
    if not ready_pressed:
        button_rect = pygame.Rect(WIDTH // 2 - 50, 300, 100, 40)
        pygame.draw.rect(screen, (0, 128, 255), button_rect)
        label = font.render("Ready", True, (0, 0, 0))
        label_rect = label.get_rect(center=button_rect.center)
        screen.blit(label, label_rect)
    else:
        text = font.render(f"Readied", True, (200, 200, 0))
        text_rect = text.get_rect(center=(WIDTH // 2, 310))
        screen.blit(text, text_rect)

def update_lobby_ui(ready_dict):
    global players_ready
    players_ready = ready_dict

def switch_to_game_screen():
    global in_lobby, in_win_screen
    in_lobby = False
    in_win_screen = False

def switch_to_win_screen(winner):
    global in_win_screen, in_lobby, winner_id, restart_clicked
    in_win_screen = True
    in_lobby = False
    restart_clicked = False
    winner_id = winner

def draw_win_screen():
    screen.fill((255, 255, 255))  # white background, like lobby

    if winner_id:
        text = font.render(f"Winner: {winner_id}", True, (0, 0, 0))
        text_rect = text.get_rect(center=(WIDTH // 2, 150))
        screen.blit(text, text_rect)

    # Restart Button
    restart_rect = pygame.Rect(0, 0, 100, 40)
    restart_rect.center = (WIDTH // 2 - 70, 300)

    if not restart_clicked:
        pygame.draw.rect(screen, (0, 128, 255), restart_rect)
        restart_label = font.render("Restart", True, (0, 0, 0))
        label_rect = restart_label.get_rect(center=restart_rect.center)
        screen.blit(restart_label, label_rect)
    else:
        text = font.render("Readied", True, (200, 200, 0))
        text_rect = text.get_rect(center=restart_rect.center)
        screen.blit(text, text_rect)

    # Exit Button
    exit_rect = pygame.Rect(0, 0, 100, 40)
    exit_rect.center = (WIDTH // 2 + 70, 300)

    pygame.draw.rect(screen, (128, 0, 0), exit_rect)
    exit_label = font.render("Exit", True, (255, 255, 255))
    exit_label_rect = exit_label.get_rect(center=exit_rect.center)
    screen.blit(exit_label, exit_label_rect)


def run_game(send_click, player_id, send_ready=None):
    global send_click_fn, local_player_id, in_lobby, in_win_screen, restart_clicked
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
                if not in_lobby and not in_win_screen:
                    gx, gy = mx // CELL_SIZE, my // CELL_SIZE
                    if (gx, gy) in coins and send_click_fn:
                        send_click_fn(gx, gy)

                elif in_win_screen:
                    # Restart Button Centered
                    restart_rect = pygame.Rect(0, 0, 100, 40)
                    restart_rect.center = (WIDTH // 2 - 70, 300)

                    # Exit Button Centered
                    exit_rect = pygame.Rect(0, 0, 100, 40)
                    exit_rect.center = (WIDTH // 2 + 70, 300)

                    if restart_rect.collidepoint(mx, my) and not restart_clicked:
                        restart_clicked = True
                        if send_ready:
                            send_ready()
                        print("Restart clicked")

                    elif exit_rect.collidepoint(mx, my):
                        pygame.quit()
                        return

                elif in_lobby and not ready_pressed:
                    # Check if Ready button is clicked
                    if WIDTH // 2 - 50 <= mx <= WIDTH // 2 + 50 and 300 <= my <= 340:
                        if send_ready:
                            send_ready() #start game
                        ready_pressed = True

        screen.fill((255, 255, 255))
        if in_lobby:
            draw_lobby(ready_pressed)
        elif in_win_screen:
            draw_win_screen()
        else:
            draw_game()

        pygame.display.flip()

    pygame.quit()
