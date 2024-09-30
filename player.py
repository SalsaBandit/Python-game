import socket
import sys

class Player:
    def __init__(self, tracker_host, tracker_port, t_port, p_port, name):
        self.tracker_host = tracker_host
        self.tracker_port = tracker_port
        self.t_port = t_port
        self.p_port = p_port
        self.name = name

    def register(self):
        message = f"register {self.name} {self.tracker_host} {self.t_port} {self.p_port}\n"
        self.send_message(message)

    def query_players(self):
        self.send_message("query_players\n")

    def start_game(self, num_players, holes=9):
        message = f"start_game {self.name} {num_players} {holes}\n"
        self.send_message(message)

    def send_message(self, message):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.tracker_host, self.tracker_port))
            client_socket.send(message.encode())
            response = client_socket.recv(1024).decode()
            print(f"Response: {response}")

    def run(self):
        while True:
            command = input("Enter command (register/query/start): ")
            if command == "register":
                self.register()
            elif command == "query":
                self.query_players()
            elif command.startswith("start"):
                _, num_players = command.split()
                self.start_game(num_players)
            else:
                print("Invalid command")

if __name__ == "__main__":
    tracker_host = sys.argv[1]
    tracker_port = int(sys.argv[2])
    t_port = int(sys.argv[3])
    p_port = int(sys.argv[4])
    name = sys.argv[5]

    player = Player(tracker_host, tracker_port, t_port, p_port, name)
    player.run()
