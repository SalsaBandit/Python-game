import socket
import threading

def get_inet():
    a = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    a.connect(('8.8.8.8', 80))
    hostname = a.getsockname()[0]
    a.close()
    return hostname


class Tracker:
    def __init__(self, host=get_inet(), port=27256):
        self.players = {}  
        self.games = {}    
        self.lock = threading.Lock()
        self.host = host
        self.port = port

    def handle_client(self, client_socket):
        try:
            while True:
                message = client_socket.recv(1024).decode()
                if not message:
                    break
                self.process_message(message, client_socket)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_socket.close()

    def process_message(self, message, client_socket):
        print(f"Received: {message}")
        tokens = message.split()
        command = tokens[0]

        if command == "register":
            self.register_player(tokens[1:], client_socket)
        elif command == "query_players":
            self.send_player_list(client_socket)
        elif command == "start_game":
            self.start_game(tokens[1:], client_socket)
        elif command == "end":
            self.end_game(tokens[1:], client_socket)
        elif command == "deregister":
            self.deregister_player(tokens[1:], client_socket)

    def register_player(self, params, client_socket):
        player_name, ip, t_port, p_port = params
        with self.lock:
            if player_name not in self.players:
                self.players[player_name] = (ip, t_port, p_port, "free")
                client_socket.send(b"SUCCESS: Player registered.\n")
            else:
                client_socket.send(b"FAILURE: Duplicate player.\n")

    def send_player_list(self, client_socket):
        with self.lock:
            players = [f"{name}: {info}" for name, info in self.players.items()]
            response = "\n".join(players).encode()
            client_socket.send(response + b"\n")

    def start_game(self, params, client_socket):
        dealer_name, num_players, holes = params
        num_players = int(num_players)
        holes = int(holes)
        
        with self.lock:
            available_players = [p for p, info in self.players.items() if info[3] == "free"]
            if len(available_players) < num_players:
                client_socket.send(b"FAILURE: Not enough free players.\n")
                return

            selected_players = available_players[:num_players]
            game_id = len(self.games) + 1
            self.games[game_id] = {"dealer": dealer_name, "players": selected_players}

            for player in selected_players:
                self.players[player] = (*self.players[player][:3], "in-play")

            response = f"SUCCESS: Game {game_id} started with players: {selected_players}\n"
            client_socket.send(response.encode())

    def end_game(self, params, client_socket):
        game_id, dealer = params
        game_id = int(game_id)

        with self.lock:
            if game_id in self.games and self.games[game_id]["dealer"] == dealer:
                players = self.games[game_id]["players"]
                for player in players:
                    self.players[player] = (*self.players[player][:3], "free")
                del self.games[game_id]
                client_socket.send(b"SUCCESS: Game ended.\n")
            else:
                client_socket.send(b"FAILURE: Invalid game or dealer.\n")

    def deregister_player(self, params, client_socket):
        player_name = params[0]

        with self.lock:
            if player_name in self.players:
                if self.players[player_name][3] == "free":
                    del self.players[player_name]
                    client_socket.send(b"SUCCESS: Player deregistered.\n")
                else:
                    client_socket.send(b"FAILURE: Player in ongoing game.\n")
            else:
                client_socket.send(b"FAILURE: Player not found.\n")

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)
        print(f"Tracker listening on {self.host}:{self.port}")

        while True:
            client_socket, addr = server.accept()
            print(f"Accepted connection from {addr}")
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

if __name__ == "__main__":
    tracker = Tracker()
    tracker.run()
