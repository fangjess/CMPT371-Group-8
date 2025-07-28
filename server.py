import socket
import threading
import json
import random
import time

# Server config
HOST = '0.0.0.0'  # Listens on all network interfaces
PORT = 5001
GRID_SIZE = 10

# Game state
clients = []
coins = set()
lock = threading.Lock()
player_map = {}  # conn: player_id
scores = {}      # player_id: score
game_started = False


# Broadcast message to all clients
def broadcast(message):
    data = (json.dumps(message) + '\n').encode()
    for client in clients:
        try:
            client.sendall(data)
        except Exception as e:
            print(f"Broadcast error: {e}")


def reset_game_state():
    global coins, scores, game_started
    coins = set()
    for pid in scores:
        scores[pid] = 0
    game_started = False
    broadcast({"type": "coin_list", "coins": [{"x": x, "y": y} for x, y in coins]})
    player_list = [{"player_id": pid, "score": scores[pid]} for pid in scores]
    broadcast({"type": "player_list", "players": player_list})


# spawn coins at random empty positions
def coin_spawner():
    while True:
        time.sleep(1)
        with lock:
            if game_started and len(coins) < GRID_SIZE * GRID_SIZE:
                available_positions = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE) if (x, y) not in coins]
                if available_positions:
                    new_coin = random.choice(available_positions)
                    coins.add(new_coin)
                    coin_list = [{"x": x, "y": y} for x, y in coins]
                    broadcast({"type": "coin_list", "coins": coin_list})


# Handle a connecting client
def handle_client(conn, addr):
    global game_started
    with conn:
        try:
            # Wait for the initial add_player message
            buffer = ""
            while True:
                data = conn.recv(4096).decode()
                if not data:
                    return
                buffer += data
                if '\n' in buffer:
                    msg_str, buffer = buffer.split('\n', 1)
                    msg = json.loads(msg_str)
                    if msg["type"] == "add_player":
                        player_id = msg["player_id"]
                        break

            with lock:  # Initial client connecting config
                clients.append(conn)
                player_map[conn] = player_id
                scores[player_id] = 0
                print(f"{player_id} connected from {addr}")

                # Send new player to other clients
                broadcast({"type": "add_player", "player_id": player_id})

                # Send full player list to the new player
                player_list = [{"player_id": pid, "score": score} for pid, score in scores.items()]
                conn.sendall((json.dumps({"type": "player_list", "players": player_list}) + '\n').encode())

                # Send current coins to the new player
                coin_list = [{"x": x, "y": y} for x, y in coins]
                conn.sendall((json.dumps({"type": "coin_list", "coins": coin_list}) + '\n').encode())
                
                # Send game state to client
                conn.sendall((json.dumps({"type": "game_state", "in_lobby": not game_started}) + '\n').encode())

            while True:
                data = conn.recv(4096).decode()
                if not data:
                    break
                buffer += data
                while '\n' in buffer:
                    msg_str, buffer = buffer.split('\n', 1)
                    msg = json.loads(msg_str)
                    if msg["type"] == "click":
                        x, y = msg["x"], msg["y"]
                        with lock:  # Lock the board and remove the coin for the winner
                            if (x, y) in coins:
                                coins.remove((x, y))
                                scores[player_id] += 1
                                broadcast({"type": "coin_claimed", "x": x, "y": y, "player_id": player_id})
                                if scores[player_id] >= 10: #win check
                                    broadcast({"type": "game_won", "player_id": player_id})
                                    
                    elif msg["type"] == "ready":
                        with lock:
                            if game_started:
                                reset_game_state()
                            game_started = True
                            broadcast({"type": "start_game"})
                            
        except Exception as e:
            print("Initial handshake failed:", e)
            return
        
        finally:
            with lock:  # Remove disconnecting client from game
                if conn in clients:
                    clients.remove(conn)
                if conn in player_map:
                    pid = player_map.pop(conn)
                    scores.pop(pid, None)
                    broadcast({"type": "remove_player", "player_id": pid})
                    print(f"{pid} disconnected.")


# Accept clients and create threads for them
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # for port re-use
    server_sock.bind((HOST, PORT))
    server_sock.listen()
    print(f"Server listening on {HOST}:{PORT}")
    threading.Thread(target=coin_spawner, daemon=True).start()  # New thread to constantly spawn coins
    while True:
        conn, addr = server_sock.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()