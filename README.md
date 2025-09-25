NBA-dle: The Daily NBA Player Guessing Game
===========================================

**NBA-dle** is a full-stack web application where players try to guess the daily mystery NBA player. The game's frontend, built with React, communicates with a Python-based backend that provides player data and validates guesses.

Features
--------

-   **Interactive Clues:** After each guess, receive feedback on the player's team, position, and jersey number.

-   **Intuitive Feedback:** A green box indicates a correct match, while a red box means the information is incorrect. For jersey numbers, you'll also get an up or down arrow hint to guide your next guess.

-   **Player Autocomplete:** An intelligent search feature that provides real-time player name suggestions as you type.

-   **Winning & Losing States:** The game correctly identifies when you have won or run out of guesses, and provides a "Play Again" option.

Technologies
------------

-   **Frontend:** React, Vite, Tailwind CSS

-   **Backend:** Flask, Flask-CORS, `nba-api` Python library

Getting Started
---------------

To run the complete application, you must start both the backend and the frontend.

### Running the Backend

1.  Make sure you have Python 3 and `pip` installed.

2.  Navigate to your backend directory in the terminal.

3.  (Optional but Recommended) Create and activate a virtual environment:

    ```
    python3 -m venv venv
    source venv/bin/activate

    ```

4.  Install the required Python packages:

    ```
    pip install -r requirements.txt

    ```

5.  Start the Flask server:

    ```
    flask run

    ```

    The backend will now be running and listening for requests.

### Running the Frontend

1.  Make sure you have Node.js and npm installed.

2.  Navigate to your frontend directory in a separate terminal window.

3.  Install the required npm packages:

    ```
    npm install

    ```

4.  Start the development server:

    ```
    npm run dev

    ```

5.  Open your web browser and navigate to the URL provided in the terminal (usually `http://localhost:5173`).

Enjoy the game!