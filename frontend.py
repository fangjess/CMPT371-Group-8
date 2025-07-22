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

def run_game(send_click, player_id):
    global send_click_fn, local_player_id
    send_click_fn = send_click
    local_player_id = player_id

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                gx, gy = mx // CELL_SIZE, my // CELL_SIZE
                if (gx, gy) in coins and send_click_fn:
                    send_click_fn(gx, gy)

        screen.fill((30, 30, 30))

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

        pygame.display.flip()

    pygame.quit()
