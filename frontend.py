import pygame

WIDTH, HEIGHT = 600, 600
GRID_SIZE = 10
CELL_SIZE = WIDTH // GRID_SIZE
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

in_lobby = False #change to False if don't want to start in lobby screen
players_ready = {} #list of player in lobby
countdown_time = None
in_win_screen = False #change to True if want to test win screen
winner_id = "jojo" #winner displayed in win screen
restart_clicked = False

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

    y_offset = 5
    for pid, score in player_scores.items():
        color = (0, 255, 0) if pid == local_player_id else (255, 255, 255)
        text = font.render(f"{pid}: {score}", True, color)
        screen.blit(text, (5, y_offset))
        y_offset += 20

def draw_lobby(ready_pressed):
    title = font.render("Lobby - Waiting for Players", True, (255, 255, 255))
    screen.blit(title, (180, 50))

    y = 100
    for pid, is_ready in players_ready.items():
        color = (0, 255, 0) if is_ready else (255, 0, 0)
        text = font.render(f"{pid} - {'Ready' if is_ready else 'Not Ready'}", True, color)
        screen.blit(text, (200, y))
        y += 30

    # Draw Ready Button
    if not ready_pressed:
        pygame.draw.rect(screen, (0, 128, 255), (250, 300, 100, 40))
        label = font.render("Ready", True, (255, 255, 255))
        screen.blit(label, (270, 310))
    elif countdown_time:
        text = font.render(f"Game starts in: {countdown_time}s", True, (255, 255, 0))
        screen.blit(text, (230, 310))

def update_lobby_ui(ready_dict):
    global players_ready
    players_ready = ready_dict

def start_countdown(seconds):
    global countdown_time
    countdown_time = seconds

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
    screen.fill((0, 0, 0))
    if winner_id:
        text = font.render(f"🏆 Winner: {winner_id}", True, (255, 255, 0))
        screen.blit(text, (200, 150))

    # Restart Button
    if restart_clicked == False:
        pygame.draw.rect(screen, (0, 128, 0), (200, 300, 100, 40))
        restart_label = font.render("Restart", True, (255, 255, 255))
        screen.blit(restart_label, (215, 310))
    else:
        pygame.draw.rect(screen, (0, 128, 0), (200, 300, 100, 40))
        restart_label = font.render("Readied", True, (255, 255, 255))
        screen.blit(restart_label, (215, 310))

    # Exit Button
    pygame.draw.rect(screen, (128, 0, 0), (320, 300, 100, 40))
    exit_label = font.render("Exit", True, (255, 255, 255))
    screen.blit(exit_label, (355, 310))



def run_game(send_click, player_id):
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
                    if 200 <= mx <= 300 and 300 <= my <= 340 and restart_clicked == False:
                        # Restart clicked
                        restart_clicked = True
                        # send_restart()  # <-- you implement in client later
                        print("Restart clicked")
                    elif 320 <= mx <= 420 and 300 <= my <= 340:
                        pygame.quit()
                        return
                elif in_lobby and not ready_pressed:
                    # Check if Ready button is clicked
                    if 250 <= mx <= 350 and 300 <= my <= 340:
                        # send_ready() #Uncomment when send ready is implemented in client
                        ready_pressed = True

        screen.fill((30, 30, 30))
        if in_lobby:
            draw_lobby(ready_pressed)
        elif in_win_screen:
            draw_win_screen()
        else:
            draw_game()

        pygame.display.flip()

    pygame.quit()
