# NBA-dle Game Backend

This is the backend API for a daily NBA player guessing game, similar to LoLdle. It is built with Python and the Flask framework.

## Features

* **Daily Player Selection:** Automatically selects a random active NBA player once per day.

* **Clue Generation:** Provides clues for the daily player (Team, Position, Jersey Number) without revealing their name.

* **Guess Validation:** Compares a user's guess against the correct player and provides detailed feedback on a per-clue basis.

## Setup and Installation

### 1. Prerequisites

Make sure you have Python 3.8 or higher installed.

### 2. Clone the Repository

git clone

cd nba-game/backend

### 3. Install Dependencies

Use the `requirements.txt` file to install all necessary Python packages. It is recommended to do this in a virtual environment.

pip install -r requirements.txt

### 4. Get Player Data

The backend relies on a local JSON file for a list of all NBA players. You will need to create this file by running a script to fetch the data from a public NBA API. For this project, we used the `nba_api` library.

### 5. Run the Backend

Start the Flask development server.

flask run

The server will run on `http://127.0.0.1:5000` by default.

## API Endpoints

* **`GET /api/daily-player`**: Returns the clues (Team, Position, Jersey Number) for the daily player.

* **`POST /api/check-guess`**: Accepts a player name as a JSON body (`{"guess": "Player Name"}`) and returns feedback on the guess.