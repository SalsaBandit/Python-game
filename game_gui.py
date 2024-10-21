import tkinter as tk
from PIL import Image, ImageTk
import random
import os

class SixCardGolfGame:
    def __init__(self, players, card_images_folder='cards'):
        self.players = players
        self.current_player_index = 0  # Track whose turn it is
        self.window = tk.Tk()
        self.window.title('Six Card Golf')
        self.card_images_folder = card_images_folder
        self.shuffled_deck = self.shuffle_deck()  # Shuffled deck from 52 cards
        self.stock_pile = self.shuffled_deck[6 * len(self.players):]  # Remaining cards form the stock pile
        self.discard_pile = []  # Initially empty
        self.player_cards = {player: self.shuffled_deck[i * 6:(i + 1) * 6] for i, player in enumerate(self.players)}
        self.create_widgets()

    def shuffle_deck(self):
        """Create a shuffled deck of 52 cards."""
        card_images = []
        for file in os.listdir(self.card_images_folder):
            if file.endswith('.png'):
                card_images.append(os.path.join(self.card_images_folder, file))
        random.shuffle(card_images)  # Shuffle the deck
        return card_images[:52]  # Ensure it's only the first 52 cards

    def create_widgets(self):
        """Create the GUI widgets for the game."""
        self.player_labels = []
        self.card_labels = []
        for i, player in enumerate(self.players):
            label = tk.Label(self.window, text=f'Player: {player}', font=("Helvetica", 16))
            label.grid(row=i, column=0)

            cards_frame = tk.Frame(self.window)
            cards_frame.grid(row=i, column=1, padx=5, pady=5)
            self.card_labels.append([])

            for j in range(6):
                img = Image.open(self.player_cards[player][j])
                img = img.resize((100, 150))
                img = ImageTk.PhotoImage(img)
                card_label = tk.Label(cards_frame, image=img)
                card_label.image = img  # Keep a reference!
                card_label.grid(row=0, column=j)
                self.card_labels[i].append(card_label)

        self.status_label = tk.Label(self.window, text=f"It's {self.players[self.current_player_index]}'s turn", font=("Helvetica", 16))
        self.status_label.grid(row=len(self.players), column=0, columnspan=2)

        draw_button = tk.Button(self.window, text='Draw Card', command=self.draw_card)
        draw_button.grid(row=len(self.players) + 1, column=0, pady=10)

        swap_button = tk.Button(self.window, text='Swap Card', command=self.swap_card)
        swap_button.grid(row=len(self.players) + 1, column=1, pady=10)

        turn_button = tk.Button(self.window, text='Turn Face-up', command=self.turn_faceup)
        turn_button.grid(row=len(self.players) + 2, column=0, pady=10)

    def turn_faceup(self):
        """Allow each player to turn two cards face-up at the start."""
        current_player = self.players[self.current_player_index]
        faceup_indices = random.sample(range(6), 2)  # Randomly choose two cards to turn face-up
        for idx in faceup_indices:
            img = Image.open(self.player_cards[current_player][idx])
            img = img.resize((100, 150))
            img = ImageTk.PhotoImage(img)
            self.card_labels[self.current_player_index][idx].config(image=img)
            self.card_labels[self.current_player_index][idx].image = img  # Keep reference!
        print(f"{current_player} turned two cards face-up.")

    def draw_card(self):
        """Simulate drawing a card either from the stock or discard pile."""
        current_player = self.players[self.current_player_index]
        if self.stock_pile:
            new_card = self.stock_pile.pop()  # Draw from the stock
        else:
            new_card = random.choice([card for card in self.all_card_images if card not in self.player_cards[current_player]])

        card_index = random.randint(0, 5)  # Replace one of the 6 cards randomly
        self.player_cards[current_player][card_index] = new_card

        # Update the card image in the GUI
        img = Image.open(new_card)
        img = img.resize((100, 150))
        img = ImageTk.PhotoImage(img)
        self.card_labels[self.current_player_index][card_index].config(image=img)
        self.card_labels[self.current_player_index][card_index].image = img  # Keep reference!

        print(f"{current_player} drew a new card at position {card_index + 1}.")

    def swap_card(self):
        """Simulate swapping two cards for the current player."""
        idx1, idx2 = random.sample(range(6), 2)  # Choose two different indices to swap
        current_player = self.players[self.current_player_index]
        self.player_cards[current_player][idx1], self.player_cards[current_player][idx2] = self.player_cards[current_player][idx2], self.player_cards[current_player][idx1]

        # Update the images in the GUI
        img1 = Image.open(self.player_cards[current_player][idx1])
        img1 = img1.resize((100, 150))
        img1 = ImageTk.PhotoImage(img1)
        self.card_labels[self.current_player_index][idx1].config(image=img1)
        self.card_labels[self.current_player_index][idx1].image = img1  # Keep reference!

        img2 = Image.open(self.player_cards[current_player][idx2])
        img2 = img2.resize((100, 150))
        img2 = ImageTk.PhotoImage(img2)
        self.card_labels[self.current_player_index][idx2].config(image=img2)
        self.card_labels[self.current_player_index][idx2].image = img2  # Keep reference!

        print(f"{current_player} swapped card {idx1 + 1} with card {idx2 + 1}.")
        self.current_player_index = (self.current_player_index + 1) % len(self.players)  # Move to the next player
        self.status_label.config(text=f"It's {self.players[self.current_player_index]}'s turn")

    def run(self):
        """Start the game loop."""
        self.window.mainloop()

if __name__ == '__main__':
    players = ['Archit', 'Abhinav', 'Aman']  # Placeholder for actual registered players
    game = SixCardGolfGame(players, 'cards')
    game.run()
