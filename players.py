import socket
import sys

class Player:
    def __init__(self, name, tracker_host='127.0.0.1', tracker_port=27000):
        self.name = name
        self.tracker_host = tracker_host
        self.tracker_port = tracker_port
        self.client_socket = None  # Persistent socket connection

    def connect(self):
        """Establishes connection to the tracker."""
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.tracker_host, self.tracker_port))
            print("Connected to tracker.")
        except ConnectionRefusedError:
            print("Connection refused. Make sure the tracker is running.")
            sys.exit(1)

    def register(self):
        message = f'register {self.name}'
        self.send_message(message)

    def send_message(self, message):
        try:
            self.client_socket.send(message.encode('utf-8'))
            response = self.client_socket.recv(1024).decode('utf-8')
            print(f'Tracker Response: {response}')
        except Exception as e:
            print(f"Error sending message: {e}")

    def start_game(self):
        message = f'start_game {self.name}'  # Sending start game command with dealer's name
        self.send_message(message)

    def deregister(self):
        self.send_message(f'deregister {self.name}')

    def close_connection(self):
        """Closes the connection to the tracker."""
        self.deregister()  # Deregister before closing
        if self.client_socket:
            self.client_socket.close()

if __name__ == '__main__':
    player_name = input("Enter your name: ")
    tracker_ip = input("Enter the tracker's IP address (default: 127.0.0.1): ") or '127.0.0.1'
    tracker_port = input("Enter the tracker's port number (default: 27000): ").strip() or '27000'

    player = Player(player_name, tracker_host=tracker_ip, tracker_port=int(tracker_port))
    player.connect()
    player.register()

    try:
        while True:
            print("\nMenu:")
            print("1. Start Game")
            print("2. Query Players")
            print("3. Query Game")
            print("4. End Game")
            print("5. De-register")
            print("6. Exit")

            choice = input("Select an option: ").strip()

            if choice == '1':
                player.start_game()
            elif choice == '2':
                player.send_message('query_players')
            elif choice == '3':
                player.send_message('query_game')
            elif choice == '4':
                player.send_message('end')
            elif choice == '5':
                player.deregister()
            elif choice == '6':
                print("Exiting...")
                break
            else:
                print("Invalid option. Please try again.")
    finally:
        player.close_connection()  # Ensure the connection is closed when done
