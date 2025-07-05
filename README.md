# Witch's Poison Game

Witch's Poison is a simple, real-time multiplayer game for two players. Each player secretly chooses one snack to be their "poison." Players then take turns picking snacks. If a player picks a snack poisoned by their opponent, they lose! If all snacks are eaten before any poison is found, the game is a draw.

## Features

*   **Real-time Multiplayer:** Play with a friend in real-time.
*   **Spectator Mode:** Others can join to watch ongoing games.
*   **Secret Poison Choice:** Each player secretly designates a poison.
*   **Turn-Based Gameplay:** Players take turns choosing snacks.
*   **Game Log:** A running log shows game events, including who ate which snack.
*   **Dynamic UI:** The interface updates instantly based on game state.

## How to Run

1.  **Prerequisites:**
    *   Python 3.x
    *   pip (Python package installer)

2.  **Clone the Repository (if you haven't already):**
    ```bash
    git clone <repository-url>
    cd WitchPoison
    ```

3.  **Install Dependencies:**
    ```bash
    pip install Flask Flask-SocketIO eventlet
    ```

4.  **Run the Application:**
    ```bash
    python app.py
    ```

5.  **Play the Game:**
    *   Open a web browser and go to `http://127.0.0.1:5000` (or the address shown in your terminal, typically including your local IP if you want others on your network to connect).
    *   The first two people to connect will be Player 1 and Player 2. Subsequent connections will be spectators.
    *   Players will be prompted to choose a snack number as their poison. Click on a snack to select it.
    *   Once both players have chosen their poison, the game begins.
    *   Players take turns clicking on snacks to "eat" them.
    *   If a player clicks the snack their opponent poisoned, they lose, and the opponent wins.
    *   If all snacks are eaten and no poison is found, the game is a draw.
    *   Click the "重新开始" (Restart) button to reset the game at any time (players will keep their roles and need to choose poisons again).

## Game Logic

*   The game is played with 20 snacks, numbered 1 to 20.
*   Each player (P1 and P2) secretly selects one snack number as their poison.
*   P1 goes first.
*   If a player selects a snack that was chosen as poison by the *other* player, they lose.
*   The game log displays the last 5 actions.
*   If a player disconnects, the game resets.

## Future Enhancements (Planned)

*   Sound effects for game events.
*   Visual animation when poison is consumed.

---

Enjoy the game!
