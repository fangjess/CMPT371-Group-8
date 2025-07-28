import socket
import threading
import json
from frontend import run_game, update_coin_list, update_player_list, remove_coin_from_ui, add_player_to_ui, switch_to_game_screen, switch_to_win_screen

# TCP network setup
SERVER_HOST = input("Enter server IP: ")
player_id = input("Enter your player ID: ")
SERVER_PORT = 5001

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER_HOST, SERVER_PORT))
sock.setblocking(True)

# Send initial add_player message
sock.sendall((json.dumps({"type": "add_player", "player_id": player_id}) + '\n').encode())

# Send click message to server when a coin is clicked
def send_coin_click(x, y):
    msg = {"type": "click", "x": x, "y": y, "player_id": player_id}
    sock.sendall((json.dumps(msg) + '\n').encode())
    
def send_ready():
    msg = {"type": "ready", "player_id": player_id}
    sock.sendall((json.dumps(msg) + '\n').encode())


# Listen to server messages
def listen_to_server():
    buffer = ""
    while True:
        try:
            data = sock.recv(4096).decode()
            if not data:
                break
            buffer += data
            while '\n' in buffer:
                msg, buffer = buffer.split('\n', 1)
                msg = json.loads(msg)
                if msg["type"] == "coin_claimed":
                    x, y = msg["x"], msg["y"]
                    winner = msg["player_id"]
                    remove_coin_from_ui(x, y, winner)
                elif msg["type"] == "add_player":
                    new_id = msg["player_id"]
                    add_player_to_ui(new_id)
                elif msg["type"] == "player_list":
                    update_player_list(msg["players"])
                elif msg["type"] == "coin_list":
                    update_coin_list(msg["coins"])
                elif msg["type"] == "new_coin":
                    update_coin_list([{"x": msg["x"], "y": msg["y"]}])
                elif msg["type"] == "game_won":
                    switch_to_win_screen(msg["player_id"])
                elif msg["type"] == "start_game":
                    switch_to_game_screen()
                elif msg["type"] == "game_state":
                    if not msg["in_lobby"]:
                        switch_to_game_screen()
        except:
            break


# Start listening thread
threading.Thread(target=listen_to_server, daemon=True).start()

# Start game loop and UI
run_game(send_coin_click, player_id, send_ready)

sock.close()
