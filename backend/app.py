# app.py
import json
import random
import os
from datetime import date
from flask import Flask, jsonify, request
from flask_cors import CORS
from nba_api.stats.endpoints import commonplayerinfo
import boto3
from requests.exceptions import ReadTimeout
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def get_all_players():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('NBAPlayers')
    response = table.scan(
        FilterExpression='is_active = :active',
        ExpressionAttributeValues={':active': True}
    )
    return response['Items']


def fetch_common_player_info(player_id, max_attempts=3, timeout=60):
    """Fetch common player info from nba_api with retries and timeout.

    Returns the dictionary from common_player_info.get_dict() on success, or None on failure.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            info = commonplayerinfo.CommonPlayerInfo(player_id=player_id, timeout=timeout)
            return info.common_player_info.get_dict()
        except ReadTimeout:
            print(f"NBA API timeout fetching player {player_id} (attempt {attempt}/{max_attempts})")
            if attempt < max_attempts:
                time.sleep(2)
        except Exception as e:
            # Catch other network/parsing errors and retry a couple times
            print(f"Error fetching player {player_id} from NBA API: {e} (attempt {attempt}/{max_attempts})")
            if attempt < max_attempts:
                time.sleep(1)

    return None

# Simple dictionary to store the daily player info
daily_player = {}
# Keep a local cache/list to preserve compatibility with tests that patch `app.all_players`
all_players = []

def get_daily_player():
    """
    Selects a random player for the day and caches their info,
    including detailed clues from the NBA API.
    """
    global daily_player
    if 'date' not in daily_player or daily_player['date'] != str(date.today()):
        active_players = get_all_players()
        chosen_player = random.choice(active_players)
        
        # Use NBA API (with retries) to get more detailed player info
        player_data = fetch_common_player_info(chosen_player['id'])
        if player_data:
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
        else:
            # Fallback to DynamoDB-stored fields if NBA API fails
            full_name = chosen_player.get('full_name')
            team_city = chosen_player.get('team_city', '')
            team_name = chosen_player.get('team_name', '')
            jersey = chosen_player.get('jersey', '')
            position = chosen_player.get('position', '')

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

@app.route('/api/players', methods=['GET'])
def get_players():
    """Returns a list of all active NBA players for the autocomplete feature."""
    # Prefer the in-memory `all_players` if it's populated (tests may patch it). Otherwise query DynamoDB.
    active_players = all_players if all_players else get_all_players()
    return jsonify([{'full_name': p['full_name'], 'id': p['id']} for p in active_players])

@app.route('/api/check-guess', methods=['POST'])
def check_guess():
    data = request.json
    user_guess_name = data.get('guess', '').lower()

    # Get the correct daily player from the global cache
    daily_player_details = get_daily_player()
    correct_player_name = daily_player_details['full_name'].lower()
    
    # Check if the user's guess is the correct player
    if user_guess_name == correct_player_name:
        return jsonify({
            'correct': True,
            'message': 'You got it!',
            'feedback': {
                'guessed_player_name': daily_player_details['full_name'],
            }
        })

    # Find the guessed player from the in-memory list if available (tests patch app.all_players)
    guessed_player = next((p for p in all_players if p['full_name'].lower() == user_guess_name), None)
    if not guessed_player:
        # Query DynamoDB for guessed player
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('NBAPlayers')
        response = table.scan(
            FilterExpression='full_name = :name',
            ExpressionAttributeValues={':name': data.get('guess', '')}
        )
        guessed_players = response.get('Items', [])
        guessed_player = guessed_players[0] if guessed_players else None

    if not guessed_player:
        return jsonify({
            'correct': False,
            'message': 'Player not found.',
            'feedback': {}
        })

    # Fetch detailed info for the guessed player (with retries)
    guessed_player_data = fetch_common_player_info(guessed_player['id'])
    if guessed_player_data:
        headers = guessed_player_data['headers']
        row = guessed_player_data['data'][0]
        guessed_team_name = row[headers.index('TEAM_NAME')]
        guessed_position = row[headers.index('POSITION')]
        guessed_jersey = row[headers.index('JERSEY')]
    else:
        # Fallback to DynamoDB-stored fields (may be empty)
        guessed_team_name = guessed_player.get('team_name', '')
        guessed_position = guessed_player.get('position', '')
        guessed_jersey = guessed_player.get('jersey', '')
    
    # Get correct player info for comparison
    correct_team_name = daily_player_details['clues']['team_name']
    correct_position = daily_player_details['clues']['position']
    correct_jersey = daily_player_details['clues']['jersey']

    # Compare attributes and build feedback
    team_match = guessed_team_name.lower() == correct_team_name.lower()
    position_match = guessed_position.lower() == correct_position.lower()
    jersey_match = guessed_jersey == correct_jersey
    
    jersey_hint = None
    try:
        if not jersey_match:
            if int(guessed_jersey) > int(correct_jersey):
                jersey_hint = 'down'
            else:
                jersey_hint = 'up'
    except (ValueError, TypeError):
        jersey_hint = None # If jersey numbers are not integers, no hint is given
    
    return jsonify({
        'correct': False,
        'message': 'Try again!',
        'feedback': {
            'team_match': team_match,
            'position_match': position_match,
            'jersey_match': jersey_match,
            'guessed_player_name': guessed_player['full_name'],
            'guessed_team': guessed_team_name,
            'guessed_position': guessed_position,
            'guessed_jersey': guessed_jersey,
            'jersey_hint': jersey_hint
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
