import socket
import threading
import json

# Server config
HOST = '0.0.0.0'  # Listens on all network interfaces
PORT = 5001
GRID_SIZE = 10

# Game state
clients = []
coins = set((x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE))
lock = threading.Lock()
player_map = {}  # conn: player_id
scores = {}      # player_id: score


# Broadcast message to all clients
def broadcast(message):
    data = (json.dumps(message) + '\n').encode()
    for client in clients:
        try:
            client.sendall(data)
        except:
            pass


# Handle a connecting client
def handle_client(conn, addr):
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
        except:
            pass
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
    while True:
        conn, addr = server_sock.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()