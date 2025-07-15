import socket
import threading
import json

# Player score tracking
player_scores = {}


# Add a new player to the lobby with score 0
def add_player(new_player_id):
    player_scores[new_player_id] = 0
    print(f"Player {new_player_id} added to lobby with score 0")

# TCP network setup
SERVER_HOST = input("Enter server IP: ")
SERVER_PORT = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER_HOST, SERVER_PORT))
sock.setblocking(True)

# Server will assign a player id to keep track of every client
player_id = None


# TO BE IMPLEMENTED
# Should remove the coin from interface and increment winning_player's score
def remove_coin(x, y, winning_player):
    print(f"Coin at ({x}, {y}) taken by player {winning_player}")


# When player clicks a coin, send the player_id and coin's coordinates to server
# Won't increment or do anything until it receives info from the server below,
# Since it could be the case that someone got the coin lock first
def handle_coin_click(x, y):
    msg = {"type": "click", "x": x, "y": y, "player_id": player_id}
    sock.sendall((json.dumps(msg) + '\n').encode())


# Listening to server thread
def listen_to_server():
    global player_id
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
                # Initializing connection message
                if msg["type"] == "init":
                    player_id = msg["player_id"]
                # Someone claimed a coin message
                elif msg["type"] == "coin_claimed":
                    x, y = msg["x"], msg["y"]
                    winner = msg["player_id"]
                    remove_coin(x, y, winner)
                # New player joined the lobby
                elif msg["type"] == "add_player":
                    new_id = msg["player_id"]
                    add_player(new_id)
        except:
            break


threading.Thread(target=listen_to_server, daemon=True).start()

