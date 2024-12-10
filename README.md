# 21ace-bot


This project is a Blackjack game bot built with Python and the [Telebot library](https://github.com/eternnoir/pyTelegramBotAPI). It allows users to play Blackjack directly in Telegram, complete with betting, splitting, double downs, and insurance options.

## Features

- Classic Blackjack Rules: Play against the dealer using standard rules.
- Betting System: Start with a balance of $1000, place bets, and manage your funds.
- Advanced Gameplay:
  - Double Down
  - Splitting hands
  - Insurance
  - Early Surrender
- Interactive Buttons: Use inline buttons for actions like Hit, Stand, and others.
- Real-time Gameplay: Dealer draws cards automatically based on game rules.

## Prerequisites

Before you begin, ensure you have the following:

1. A [Telegram bot token](https://core.telegram.org/bots#botfather).
2. Python 3.7 or higher installed on your system.

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/Ktsarvi/blackjack-telegram-bot.git
    cd blackjack-telegram-bot
    ```

2. Install the required dependencies:
    ```bash
    pip install pyTelegramBotAPI
    ```

3. Replace `YOUR_TOKEN` in the code with your bot's token:
    ```python
    API_TOKEN = 'YOUR_TOKEN'
    ```

4. Run the bot:
    ```bash
    python blackjack_bot.py
    ```

## Commands

- `/start` - Start a new game of Blackjack.
- `/bet <amount>` - Place your bet to start the game.
- `/balance` - Check your current balance.

## Gameplay Overview

- At the start of a game, players place a bet.
- The bot deals two cards to both the player and the dealer.
- Players can choose to:
  - `Hit`: Draw another card.
  - `Stand`: End their turn.
  - `Double Down`: Double the bet and draw only one additional card.
  - `Split`: Split into two hands if the first two cards have the same value.
  - `Insurance`: Take insurance if the dealer's visible card is an Ace.
  - `Early Surrender`: Forfeit the game and recover half the bet.
- The dealer reveals their cards and plays until they reach a score of 17 or higher.
- The winner is determined based on scores, with the goal being closer to 21 than the dealer without exceeding it.


## Future Improvements

- Add support for multiplayer games.
- Implement persistent balance storage using a database.
- Add support for additional Blackjack variations.

## Contributing

Contributions are welcome! Please fork the repository, make changes, and submit a pull request.


---

Have fun and may the odds be in your favor! 
