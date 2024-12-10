import random
import telebot
from telebot import types

# Initialize the bot with your token
API_TOKEN = '7595196456:AAFfnXKES6K741L8qNKWy4M7mnfEe481BOg'  # Replace with your bot's actual token
bot = telebot.TeleBot(API_TOKEN)


class BlackjackGame:
    def __init__(self):
        self.money_to_gamble = 1000  # Starting money for the player
        self.cards = {
            'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
            'ten': 10, 'king': 10, 'queen': 10, 'jack': 10, 'ace': 11  # Ace as 11 initially
        }
        self.reset_game()

    def reset_game(self):
        """Resets the game to initial state, but keeps the player's money intact."""
        self.used_cards = []
        self.user_hand = []
        self.user_hand_split = []  # Track split hand
        self.dealer_hand = []
        self.user_score = 0
        self.user_score_split = 0  # Score for split hand
        self.dealer_score = 0
        self.bet_amount = 0
        self.game_state = False
        self.dealer_reveal = False
        self.double_down_allowed = False
        self.double_down_active = False
        self.split_active = False  # Track if split was used
        self.total_bet = 0

    def start_game(self, message):
        """Starts a new game session."""
        if self.game_state:
            bot.send_message(message.chat.id, "Game already in progress! Use /hit or /stand.")
            return

        self.reset_game()
        self.game_state = True
        self.send_balance(message)

        markup = types.InlineKeyboardMarkup()
        bet_button = types.InlineKeyboardButton("Place Bet", callback_data="bet_prompt")
        markup.add(bet_button)

        bot.send_message(message.chat.id, "Welcome to Blackjack! Place a bet to start.", reply_markup=markup)

    def send_balance(self, message):
        bot.send_message(message.chat.id, f"Your balance: ${self.money_to_gamble}")

    def place_bet(self, message, bet_amount):
        try:
            # Convert the bet amount to a float to allow decimal bets
            bet_amount = float(bet_amount)
        except ValueError:
            bot.send_message(message.chat.id, "Invalid bet amount. Please enter a valid number.")
            return

        if bet_amount < 0 or bet_amount > self.money_to_gamble:
            bot.send_message(message.chat.id, "Invalid bet amount. Please enter a valid bet within your balance.")
            return

        self.bet_amount = bet_amount
        self.money_to_gamble -= self.bet_amount
        self.send_balance(message)

        # Deal initial cards to the user and dealer
        self.dealer_score, self.user_score = self.shuffling_turn1()

        # Check for blackjack (score of 21 with exactly two cards)
        if self.user_score == 21 and len(self.user_hand) == 2:
            self.dealer_reveal = True  # Reveal dealer's cards
            self.send_game_status(message)  # Show both hands

            # After showing hands, give the blackjack payout
            payout = self.bet_amount * 1.5
            self.money_to_gamble += payout
            bot.send_message(message.chat.id, f"Blackjack! You win ${payout:.2f}!")
            self.end_game(message, 1)
            return

        # If no blackjack, proceed as usual
        self.send_game_status(message)

        # Allow the player to "Double Down" if possible
        self.double_down_allowed = True if self.bet_amount * 2 <= self.money_to_gamble else False
        self.send_action_buttons(message)

    def shuffling_turn1(self):
        # Deal two cards to the user
        user_card1, user_value1 = self.draw_card()
        user_card2, user_value2 = self.draw_card()

        self.user_hand.append((user_card1, user_value1))
        self.user_hand.append((user_card2, user_value2))

        # Deal two cards to the dealer
        dealer_card1, dealer_value1 = self.draw_card()
        dealer_card2, dealer_value2 = self.draw_card()

        self.dealer_hand.append((dealer_card1, dealer_value1))
        self.dealer_hand.append((dealer_card2, dealer_value2))

        # Calculate initial scores considering Aces
        self.dealer_score = self.calculate_score(self.dealer_hand)
        self.user_score = self.calculate_score(self.user_hand)

        return self.dealer_score, self.user_score

    def send_game_status(self, message):
        # Show only the first dealer card if the second card is hidden
        if self.dealer_reveal:
            dealer_cards_str = ', '.join([f"{card} (Value: {value})" for card, value in self.dealer_hand])
            dealer_total_str = f"Total: {self.dealer_score}"
        else:
            dealer_cards_str = f"{self.dealer_hand[0][0]} (Value: {self.dealer_hand[0][1]}), [Hidden Card]"
            dealer_total_str = f"Total: {self.dealer_hand[0][1]} + ?"

        user_cards_str = ', '.join([f"{card} (Value: {value})" for card, value in self.user_hand])

        bot.send_message(message.chat.id, f"Dealer's cards: {dealer_cards_str} | {dealer_total_str}")
        bot.send_message(message.chat.id, f"Your cards: {user_cards_str} | Total: {self.user_score}")

    def send_action_buttons(self, message):
        """Sends inline buttons for 'Hit', 'Stand', 'Double Down', and optionally 'Insurance'."""
        markup = types.InlineKeyboardMarkup()

        # Add Early Surrender button only if it's the first action
        if len(self.user_hand) == 2 and not self.double_down_active and not self.split_active:
            surrender_button = types.InlineKeyboardButton("Early Surrender", callback_data="early_surrender")
            markup.add(surrender_button)

        # Add Insurance button if the dealer's upcard is an Ace
        if self.dealer_hand and self.dealer_hand[0][1] == 11:
            insurance_button = types.InlineKeyboardButton("Insurance", callback_data="insurance")
            markup.add(insurance_button)

        # Add Double Down button if allowed
        if self.double_down_allowed and not self.double_down_active:
            double_down_button = types.InlineKeyboardButton("Double Down", callback_data="double_down")
            markup.add(double_down_button)

        # Add Hit and Stand buttons
        hit_button = types.InlineKeyboardButton("Hit", callback_data="hit")
        stand_button = types.InlineKeyboardButton("Stand", callback_data="stand")
        markup.add(hit_button, stand_button)

        bot.send_message(message.chat.id, "Choose your next action:", reply_markup=markup)

    def hit(self, message):
        if not self.game_state:
            bot.send_message(message.chat.id, "Please start a game first using /start.")
            return

        # Draw a new card for the user
        card_name, card_value = self.draw_card()
        self.user_hand.append((card_name, card_value))
        self.user_score = self.calculate_score(self.user_hand)
        self.send_game_status(message)

        if self.user_score > 21:
            bot.send_message(message.chat.id, "Bust! You lose.")
            self.end_game(message, -1)
        else:
            # Remove the "Double Down" button after hit
            self.double_down_allowed = False
            self.send_action_buttons(message)

    def stand(self, message):
        if not self.game_state:
            bot.send_message(message.chat.id, "Please start a game first using /start.")
            return

        # Reveal the dealer's hidden card
        self.dealer_reveal = True
        self.send_game_status(message)

        # Dealer takes a card only if the initial score is less than 17
        if self.dealer_score < 17:
            while self.dealer_score < 17:
                card_name, card_value = self.draw_card()
                self.dealer_hand.append((card_name, card_value))
                self.dealer_score = self.calculate_score(self.dealer_hand)
                bot.send_message(message.chat.id, f"Dealer drew: {card_name} (Value: {card_value})")
                bot.send_message(message.chat.id,
                                 f"Dealer's total score: {self.dealer_score}")  # Show dealer's total score

        self.send_game_status(message)
        self.check_winner(message)

    def double_down(self, message):
        """Handles the 'Double Down' functionality."""
        if not self.game_state:
            bot.send_message(message.chat.id, "Please start a game first using /start.")
            return

        # Check if the player has enough balance to double down
        if self.bet_amount > self.money_to_gamble:
            bot.send_message(message.chat.id, "You don't have enough money to double down.")
            return

        # Deduct an additional amount equal to the original bet for doubling down
        self.money_to_gamble -= self.bet_amount  # Subtract the original bet amount again
        self.total_bet = self.bet_amount * 2  # Store the doubled bet amount
        self.send_balance(message)
        self.double_down_active = True  # Mark Double Down as used

        # Draw exactly one more card for the user
        card_name, card_value = self.draw_card()
        self.user_hand.append((card_name, card_value))
        self.user_score = self.calculate_score(self.user_hand)

        # Check if the player busts after doubling down
        if self.user_score > 21:
            bot.send_message(message.chat.id,
                             f"You drew {card_name} and busted with a total of {self.user_score}. You lose.")
            self.end_game(message, -1)  # End the game with a loss if busting occurs
            return

        # Reveal dealer's hidden card if the player didn't bust
        self.dealer_reveal = True
        self.send_game_status(message)

        # Dealer continues to take cards if score is less than 17
        while self.dealer_score < 17:
            card_name, card_value = self.draw_card()
            self.dealer_hand.append((card_name, card_value))
            self.dealer_score = self.calculate_score(self.dealer_hand)
            bot.send_message(message.chat.id, f"Dealer drew: {card_name} (Value: {card_value})")
            bot.send_message(message.chat.id, f"Dealer's total score: {self.dealer_score}")  # Show dealer's total score

        self.check_winner(message)

    def split_hand(self, message):
        """Handles the 'Split' functionality, creating a second hand."""
        if not self.game_state or len(self.user_hand) != 2 or self.user_hand[0][1] != self.user_hand[1][1]:
            bot.send_message(message.chat.id, "Split not allowed.")
            return

        if self.bet_amount > self.money_to_gamble:
            bot.send_message(message.chat.id, "Not enough money to split.")
            return

        # Deduct additional bet for the split
        self.money_to_gamble -= self.bet_amount
        self.user_hand_split = [self.user_hand.pop()]  # Move one card to split hand
        self.split_active = True
        self.send_balance(message)

        # Draw an additional card for each hand
        card_name, card_value = self.draw_card()
        self.user_hand.append((card_name, card_value))
        card_name, card_value = self.draw_card()
        self.user_hand_split.append((card_name, card_value))

        # Calculate scores for both hands
        self.user_score = self.calculate_score(self.user_hand)
        self.user_score_split = self.calculate_score(self.user_hand_split)

        bot.send_message(message.chat.id, "You split your hand!")
        self.send_game_status(message)
        self.send_action_buttons(message)

    def early_surrender(self, message):
        """Handles the 'Early Surrender' functionality."""
        if not self.game_state or self.bet_amount <= 0:
            bot.send_message(message.chat.id, "Please start a game first and place a bet.")
            return

        # Calculate the refund as half of the initial bet
        refund = self.bet_amount / 2
        self.money_to_gamble += refund  # Add the refund to the already-deducted balance
        bot.send_message(message.chat.id, f"You surrendered! You receive half your bet back: ${refund:.2f}.")

        # Reset the bet amount to zero, as the round is ending
        self.bet_amount = 0
        # End the game and reset
        self.end_game(message, 0)  # Pass outcome 0 to reset the game without additional payouts

    def insurance(self, message):
        """Handles the 'Insurance' functionality when dealer's upcard is an Ace."""
        if not self.game_state or self.dealer_hand[0][1] != 11:
            bot.send_message(message.chat.id, "Insurance is not available.")
            return

        # Calculate the insurance bet (half of the original bet)
        insurance_bet = self.bet_amount / 2

        if insurance_bet > self.money_to_gamble:
            bot.send_message(message.chat.id, "You don't have enough balance for insurance.")
            return

        # Deduct insurance bet from player's balance
        self.money_to_gamble -= insurance_bet
        self.insurance_bet = insurance_bet  # Store insurance bet to handle payout later
        bot.send_message(message.chat.id, f"You've taken insurance for ${insurance_bet:.2f}.")

        # Check if dealer has blackjack
        dealer_has_blackjack = self.calculate_score(self.dealer_hand) == 21

        # Handle insurance outcome
        if dealer_has_blackjack:
            # Insurance wins (payout 2:1)
            insurance_payout = insurance_bet * 2
            self.money_to_gamble += insurance_payout
            bot.send_message(message.chat.id,
                             f"Dealer has blackjack! You win the insurance bet and receive ${insurance_payout:.2f}.")
        else:
            # Insurance loses
            bot.send_message(message.chat.id, "Dealer does not have blackjack. You lose the insurance bet.")

        # Proceed with revealing dealer's blackjack status or continuing the game
        if dealer_has_blackjack:
            # End game if dealer has blackjack
            self.end_game(message, -1)
        else:
            # Continue game as normal if dealer doesn't have blackjack
            self.send_game_status(message)
            self.send_action_buttons(message)

    def draw_card(self):
        """Draws a card from the deck and returns its name and value."""
        card = random.choice(list(self.cards.items()))
        while card in self.used_cards:
            card = random.choice(list(self.cards.items()))

        self.used_cards.append(card)
        return card

    def calculate_score(self, hand):
        """Calculates the total score of a given hand, adjusting for Aces."""
        score = sum([card[1] for card in hand])
        num_aces = sum([1 for card in hand if card[0] == 'ace'])
        while score > 21 and num_aces:
            score -= 10
            num_aces -= 1
        return score

    def check_winner(self, message):
        """Compares scores and determines the winner."""
        if self.dealer_score > 21 or self.user_score > self.dealer_score:
            bot.send_message(message.chat.id, "You win!")
            self.end_game(message, 1)  # Outcome 1 means the player wins
        elif self.user_score < self.dealer_score:
            bot.send_message(message.chat.id, "Dealer wins!")
            self.end_game(message, -1)  # Outcome -1 means the dealer wins
        else:
            bot.send_message(message.chat.id, "It's a tie!")
            self.end_game(message, 0)  # Outcome 0 means a tie

    def end_game(self, message, outcome):
        """Ends the current game and resets the game state."""
        if outcome == 1 and self.bet_amount > 0:  # Player wins
            # Payout is based on total_bet if double down was used, otherwise bet_amount
            payout = self.total_bet if self.double_down_active else self.bet_amount
            self.money_to_gamble += 2 * payout  # Double the bet amount as the reward for winning
        elif outcome == 0 and self.bet_amount > 0:  # Tie
            # Refund the original bet amount or total bet amount if doubled down
            refund = self.total_bet if self.double_down_active else self.bet_amount
            self.money_to_gamble += refund

        self.send_balance(message)

        # Reset game state
        self.reset_game()

        # Offer a "Start New Game" button
        markup = types.InlineKeyboardMarkup()
        new_game_button = types.InlineKeyboardButton("Start New Game", callback_data="start_game")
        markup.add(new_game_button)

        bot.send_message(message.chat.id, "Game over! Start a new game below.", reply_markup=markup)


# Initialize the game object
game = BlackjackGame()


# Command to start the game
@bot.message_handler(commands=['start'])
def start(message):
    game.start_game(message)


# Callback handler for button actions
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "bet_prompt":
        bot.send_message(call.message.chat.id, "Please enter a bet amount (e.g., /bet 10).")
    elif call.data == "hit":
        game.hit(call.message)
    elif call.data == "stand":
        game.stand(call.message)
    elif call.data == "start_game":
        game.start_game(call.message)
    elif call.data == "double_down":
        game.double_down(call.message)
    elif call.data == "insurance":
        game.insurance(call.message)
    elif call.data == "early_surrender":
        game.early_surrender(call.message)


# Command to place a bet
@bot.message_handler(commands=['bet'])
def bet(message):
    try:
        # Extract the bet amount and convert to a float
        bet_amount = float(message.text.split()[1])
        game.place_bet(message, bet_amount)
    except IndexError:
        bot.send_message(message.chat.id, "Please provide a bet amount after the /bet command, e.g., /bet 10.5.")
    except ValueError:
        bot.send_message(message.chat.id, "Invalid bet amount. Please enter a valid number after /bet.")


# Command to check the balance
@bot.message_handler(commands=['balance'])
def balance(message):
    game.send_balance(message)


# Polling the bot with infinity_polling to handle errors gracefully
bot.infinity_polling()
