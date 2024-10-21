import socket
import threading
import logging
import sys
from game_gui import SixCardGolfGame

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Tracker:
    def __init__(self, host='0.0.0.0', port=27000):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server_socket.bind((host, port))
        except socket.error as e:
            logging.error(f"Failed to bind to {host}:{port} - {e}")
            sys.exit(1)
        self.server_socket.listen(5)
        self.players = []
        self.player_sockets = {}
        self.dealer = None
        self.game_state = 'waiting'  # Possible states: waiting, in_progress, ended

        logging.info(f"Tracker started on IP: {host}, Port: {port}")

    def handle_client(self, client_socket):
        player_name = None
        try:
            while True:
                message = client_socket.recv(1024).decode()
                if not message:
                    break
                logging.info(f'Received: {message}')

                if message.startswith('register'):
                    player_name = message.split()[1]
                    if player_name not in self.players:
                        self.players.append(player_name)
                        self.player_sockets[player_name] = client_socket
                        client_socket.send(b'Registration successful.')
                        logging.info(f'Player registered: {player_name}')
                    else:
                        client_socket.send(b'Player already registered.')
                        logging.warning(f'Registration failed for {player_name}: already registered.')

                elif message == 'query_players':
                    players_list = ', '.join(self.players)
                    response = f'Registered Players: {players_list}' if self.players else 'No registered players.'
                    client_socket.send(response.encode())
                    logging.info(f'Players queried: {response}')

                elif message == 'query_game':
                    response = f'Game is currently {self.game_state}.'
                    client_socket.send(response.encode())

                elif message.startswith('start_game'):
                    dealer_name = message.split()[1]
                    if dealer_name in self.players:
                        self.game_state = 'in_progress'
                        client_socket.send(b'Starting the game...')
                        logging.info(f'Starting game with dealer: {dealer_name}')
                        self.start_game(dealer_name)
                    else:
                        client_socket.send(b'Dealer not registered.')
                        logging.warning(f'Start game failed: dealer {dealer_name} not registered.')

                elif message.startswith('end'):
                    if self.game_state == 'in_progress':
                        self.game_state = 'ended'
                        client_socket.send(b'Game has been ended.')
                        logging.info('Game ended by request.')
                    else:
                        client_socket.send(b'No game is currently in progress.')
                        logging.warning('End game request denied: no game in progress.')

                elif message.startswith('deregister'):
                    if player_name in self.players:
                        self.players.remove(player_name)
                        del self.player_sockets[player_name]
                        client_socket.send(b'Player de-registered.')
                        logging.info(f'Player de-registered: {player_name}')
                        # If the dealer deregisters, end the game
                        if player_name == self.dealer:
                            self.game_state = 'ended'
                            logging.info('Dealer deregistered. Game ended.')
                    else:
                        client_socket.send(b'Player not found.')
                        logging.warning(f'Deregistration failed for {player_name}: not found.')

                else:
                    client_socket.send(b'Unknown command.')
                    logging.warning(f'Unknown command received: {message}')

        except Exception as e:
            logging.error(f"Error handling client {player_name}: {e}")

        finally:
            if player_name and player_name in self.players:
                self.players.remove(player_name)
                del self.player_sockets[player_name]
                logging.info(f"Player {player_name} disconnected and removed.")
            client_socket.close()

    def start_game(self, dealer_name):
        self.dealer = dealer_name
        logging.info("Game is starting with players: %s", self.players)
        
        # Prepare and send player info to dealer
        dealer_info = f'{dealer_name} {self.get_local_ip()} 5000'
        player_info = [f'{player} {self.get_local_ip()} 5001' for player in self.players if player != dealer_name]
        all_info = [dealer_info] + player_info
        dealer_socket = self.player_sockets[dealer_name]
        dealer_socket.send('\n'.join(all_info).encode())

        # Start the game GUI in a new thread
        game_thread = threading.Thread(target=self.run_game_gui, args=(dealer_name,))
        game_thread.start()

    def run_game_gui(self, dealer_name):
        try:
            game_gui = SixCardGolfGame(self.players, 'cards')  # Ensure the 'cards' folder has the card images
            game_gui.run()
            self.game_state = 'ended'
            logging.info('Game GUI has been closed.')
        except Exception as e:
            logging.error(f"Error running game GUI: {e}")
            self.game_state = 'ended'

    def get_local_ip(self):
        """Utility method to get the local IP address of the machine."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return '127.0.0.1'

    def run(self):
        logging.info(f'Tracker listening on {self.server_socket.getsockname()}')
        try:
            while True:
                client_socket, addr = self.server_socket.accept()
                logging.info(f'Connection accepted from {addr}')
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.start()
        except KeyboardInterrupt:
            logging.info('Tracker shutting down.')
        finally:
            self.server_socket.close()

if __name__ == '__main__':
    host_ip = input("Enter the tracker IP address (default is 0.0.0.0 for all interfaces): ") or '0.0.0.0'
    port_input = input("Enter the tracker port number (default is 27000): ").strip()
    try:
        port = int(port_input) if port_input else 27000
    except ValueError:
        logging.error("Invalid port number. Using default port 27000.")
        port = 27000

    tracker = Tracker(host=host_ip, port=port)
    tracker.run()
