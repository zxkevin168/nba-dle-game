import json
from nba_api.stats.static import players

def get_all_nba_players_data():
    """
    Fetches all active and inactive NBA players using nba_api and saves them to a JSON file.
    """
    # Get all players (active and inactive)
    nba_players = players.get_players()

    player_list = []
    for player in nba_players:
        player_list.append({
            'id': player['id'],
            'full_name': player['full_name'],
            'first_name': player['first_name'],
            'last_name': player['last_name'],
            'is_active': player['is_active']
        })

    output_filename = 'nba_players_list.json'
    with open(output_filename, 'w') as f:
        json.dump(player_list, f, indent=4)
    print(f"Successfully fetched {len(player_list)} players and saved to {output_filename}")

if __name__ == '__main__':
    get_all_nba_players_data()