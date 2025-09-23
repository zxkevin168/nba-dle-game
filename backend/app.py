# app.py
import json
import random
from datetime import date, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load player data once when the application starts
with open('nba_players_list.json', 'r') as f:
    all_players = json.load(f)

# Simple dictionary to store the daily player info
daily_player = {}

def get_daily_player():
    """
    Selects a random player for the day and caches their info.
    This function would ideally run once per day via a scheduler.
    """
    global daily_player
    # Check if the daily player has already been selected for today
    if 'date' not in daily_player or daily_player['date'] != str(date.today()):
        # Select a random active player
        active_players = [p for p in all_players if p['is_active']]
        chosen_player = random.choice(active_players)

        daily_player = {
            'date': str(date.today()),
            'id': chosen_player['id'],
            'full_name': chosen_player['full_name'],
            'first_name': chosen_player['first_name'],
            'last_name': chosen_player['last_name'],
            'clues': chosen_player # Store the entire player object for future clues
            # For now, we won't serve the full name, just the ID
        }
        print(f"Daily player selected: {daily_player['full_name']}")
    return daily_player

# This is our first endpoint
@app.route('/api/daily-player', methods=['GET'])
def get_daily_player_endpoint():
    # This endpoint will get the daily player's ID and serve it to the frontend.
    # The frontend will use this ID to make a guess.
    player_details = get_daily_player()
    clues = {
        'first_name_initial': player_details['first_name'][0].upper(),
        'last_name_initial': player_details['last_name'][0].upper()
    }
    return jsonify(clues)

# This is our second endpoint
@app.route('/api/check-guess', methods=['POST'])
def check_guess():
    # The frontend will send a user's guess to this endpoint
    data = request.json
    user_guess = data.get('guess', '').lower()

    # Get the actual daily player's full name from our data source using the ID
    daily_player_details = get_daily_player()
    correct_player_name = daily_player_details['full_name'].lower()

    if user_guess == correct_player_name:
        return jsonify({'correct': True, 'message': 'You got it!'})
    else:
        return jsonify({'correct': False, 'message': 'Try again!'})

if __name__ == '__main__':
    app.run(debug=True)