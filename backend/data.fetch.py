import requests
from nba_api.stats.static import players
import boto3

def write_players_to_dynamodb(players_list):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('NBAPlayers')
    with table.batch_writer() as batch:
        for player in players_list:
            batch.put_item(Item=player)

def fetch_and_save_players():
    all_players = players.get_players()
    write_players_to_dynamodb(all_players)

if __name__ == '__main__':
    fetch_and_save_players()