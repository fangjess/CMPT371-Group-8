import socket
import threading
import json


import pygame

# Front end display config
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 10
CELL_SIZE = WIDTH // GRID_SIZE
FPS = 32

# Front end game state
coins = set()  # Empty until server loads them in
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Coin Clicker")
font = pygame.font.SysFont(None, 24)
clock = pygame.time.Clock()


# Player score tracking
player_scores = {}


# Add a new player to the lobby with score 0
def add_player(new_player_id):
    if new_player_id not in player_scores:
        player_scores[new_player_id] = 0
        print(f"Player {new_player_id} added to lobby with score 0")

# TCP network and new player setup
SERVER_HOST = input("Enter server IP: ")
player_id = input("Enter your player ID: ")  # user picks their own ID
SERVER_PORT = 5001

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER_HOST, SERVER_PORT))

# Send player ID to server upon connecting
sock.sendall((json.dumps({"type": "add_player", "player_id": player_id}) + '\n').encode())
sock.setblocking(True)


# Should remove the coin from interface and increment winning_player's score
def remove_coin(x, y, winning_player):
    coins.discard((x, y))
    player_scores[winning_player] = player_scores.get(winning_player, 0) + 1
    print(f"Coin at ({x}, {y}) taken by player {winning_player}")


# When player clicks a coin, send the player_id and coin's coordinates to server
# Won't increment or do anything until it receives info from the server below,
# Since it could be the case that someone got the coin lock first
def handle_coin_click(x, y):
    msg = {"type": "click", "x": x, "y": y, "player_id": player_id}
    sock.sendall((json.dumps(msg) + '\n').encode())


# Listening to server thread
def listen_to_server():
    buffer = ""
    while True:
        try:
            data = sock.recv(4096).decode()
            if not data:
                break
            buffer += data
            # \n is used as a seperator between messages
            while '\n' in buffer:
                # Isolate the message
                msg, buffer = buffer.split('\n', 1)
                msg = json.loads(msg)
                # Someone claimed a coin message
                if msg["type"] == "coin_claimed":
                    x, y = msg["x"], msg["y"]
                    winner = msg["player_id"]
                    remove_coin(x, y, winner)
                # New player joined the lobby
                elif msg["type"] == "add_player":
                    new_id = msg["player_id"]
                    add_player(new_id)
                # Load all current players and their scores upon connecting to server initially
                elif msg["type"] == "player_list":
                    player_scores.clear()
                    for entry in msg["players"]:
                        pid = entry["player_id"]
                        score = entry["score"]
                        player_scores[pid] = score
                # Receive a list of all coin positions from the server when connecting initially
                elif msg["type"] == "coin_list":
                    coins.clear()
                    for c in msg["coins"]:
                        coins.add((c["x"], c["y"]))
                # Remove player if they left the game
                elif msg["type"] == "remove_player":
                    pid = msg["player_id"]
                    if pid in player_scores:
                        del player_scores[pid]
                        print(f"Player {pid} has disconnected.")
        except:
            break


threading.Thread(target=listen_to_server, daemon=True).start()

### FRONT END LOOP ---------------------------------
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            gx, gy = mx // CELL_SIZE, my // CELL_SIZE
            if (gx, gy) in coins:
                handle_coin_click(gx, gy)

    screen.fill((30, 30, 30))

    # Draw grid
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, (50, 50, 50), rect, 1)

    # Draw coins
    for x, y in coins:
        rect = pygame.Rect(x * CELL_SIZE + 10, y * CELL_SIZE + 10, CELL_SIZE - 20, CELL_SIZE - 20)
        pygame.draw.ellipse(screen, (255, 215, 0), rect)

    # Draw scores
    y_offset = 5
    for pid, score in player_scores.items():
        color = (0, 255, 0) if pid == player_id else (255, 255, 255)
        text = font.render(f"{pid}: {score}", True, color)
        screen.blit(text, (5, y_offset))
        y_offset += 20

    pygame.display.flip()

pygame.quit()
sock.close()