# app.py
import json
import random
from datetime import date
from flask import Flask, jsonify, request
from flask_cors import CORS
from nba_api.stats.endpoints import commonplayerinfo

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load player data once when the application starts
with open('nba_players_list.json', 'r') as f:
    all_players = json.load(f)

# Simple dictionary to store the daily player info
daily_player = {}

def get_daily_player():
    """
    Selects a random player for the day and caches their info,
    including detailed clues from the NBA API.
    """
    global daily_player
    if 'date' not in daily_player or daily_player['date'] != str(date.today()):
        active_players = [p for p in all_players if p['is_active']]
        chosen_player = random.choice(active_players)
        
        # Use nba_api to get more detailed player info
        player_info = commonplayerinfo.CommonPlayerInfo(player_id=chosen_player['id'])
        
        # Access the data directly as a dictionary
        player_data = player_info.common_player_info.get_dict()
        
        # Extract headers and data
        headers = player_data['headers']
        data = player_data['data'][0]
        
        # Find the index of each desired clue dynamically
        team_city_index = headers.index('TEAM_CITY')
        team_name_index = headers.index('TEAM_NAME')
        position_index = headers.index('POSITION')
        jersey_index = headers.index('JERSEY')
        full_name_index = headers.index('DISPLAY_FIRST_LAST')
        
        # Extract data using the found indices
        full_name = data[full_name_index]
        team_city = data[team_city_index]
        team_name = data[team_name_index]
        jersey = data[jersey_index]
        position = data[position_index]

        daily_player = {
            'date': str(date.today()),
            'id': chosen_player['id'],
            'full_name': full_name,
            'clues': {
                'team_city': team_city,
                'team_name': team_name,
                'position': position,
                'jersey': jersey
            }
        }
        print(f"Daily player selected: {daily_player['full_name']}")
    return daily_player

@app.route('/api/daily-player', methods=['GET'])
def get_daily_player_endpoint():
    player_details = get_daily_player()
    return jsonify(player_details['clues'])

@app.route('/api/check-guess', methods=['POST'])
def check_guess():
    data = request.json
    user_guess_name = data.get('guess', '').lower()

    daily_player_details = get_daily_player()
    correct_player_name = daily_player_details['full_name'].lower()
    correct_player_clues = daily_player_details['clues']

    # Find the guessed player's details from the full player list
    guessed_player_data = next((p for p in all_players if p['full_name'].lower() == user_guess_name), None)

    if not guessed_player_data:
        return jsonify({
            'correct': False,
            'message': 'Invalid player name. Please select from the dropdown.'
        })

    # Get detailed info for the guessed player using the NBA API
    guessed_player_info = commonplayerinfo.CommonPlayerInfo(player_id=guessed_player_data['id'])
    player_data = guessed_player_info.common_player_info.get_dict()
    headers = player_data['headers']
    data = player_data['data'][0]

    team_name_index = headers.index('TEAM_NAME')
    position_index = headers.index('POSITION')
    jersey_index = headers.index('JERSEY')

    guessed_team = data[team_name_index]
    guessed_position = data[position_index]
    guessed_jersey = data[jersey_index]
    
    # Compare with the correct player's clues
    is_correct = user_guess_name == correct_player_name

    feedback = {
        'correct': is_correct,
        'guessed_player_name': guessed_player_data['full_name'],
        'guessed_player_clues': {
            'team': guessed_team,
            'position': guessed_position,
            'jersey': guessed_jersey
        },
        'clue_feedback': {
            'team_correct': guessed_team == correct_player_clues['team_name'],
            'position_correct': guessed_position == correct_player_clues['position'],
            'jersey_correct': guessed_jersey == correct_player_clues['jersey'],
            'jersey_hint': ''
        }
    }
    
    if not is_correct:
        try:
            # Provide a hint if the jersey numbers are comparable
            if int(guessed_jersey) > int(correct_player_clues['jersey']):
                feedback['clue_feedback']['jersey_hint'] = 'down'
            elif int(guessed_jersey) < int(correct_player_clues['jersey']):
                feedback['clue_feedback']['jersey_hint'] = 'up'
        except (ValueError, TypeError):
            # Handle cases where jersey number is not a valid integer
            feedback['clue_feedback']['jersey_hint'] = ''

    if is_correct:
        feedback['message'] = 'You got it!'
    else:
        feedback['message'] = 'Try again!'

    return jsonify(feedback)

if __name__ == '__main__':
    app.run(debug=True)
