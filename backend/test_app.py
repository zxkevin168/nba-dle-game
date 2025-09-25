import unittest
import json
from datetime import date
from unittest.mock import patch, MagicMock
from app import app, daily_player, get_daily_player

class NBA_dle_Tests(unittest.TestCase):
    """
    Test suite for the NBA-dle backend API.
    """

    def setUp(self):
        """
        Set up the Flask test client.
        """
        self.app = app.test_client()
        self.app.testing = True

    @patch('app.get_daily_player')
    def test_daily_player_endpoint(self, mock_get_daily_player):
        """
        Test the /api/daily-player endpoint to ensure it returns
        the correct clues and a 200 OK status.
        """
        # Mock the function call to control the daily player for the test
        mock_get_daily_player.return_value = {
            'date': str(date.today()),
            'id': 1628991, # Mock player ID (e.g., Luka Doncic)
            'full_name': 'Luka Doncic',
            'clues': {
                'team_city': 'Dallas',
                'team_name': 'Mavericks',
                'position': 'Guard-Forward',
                'jersey': '77'
            }
        }
        
        # Make a GET request to the endpoint
        response = self.app.get('/api/daily-player')
        data = json.loads(response.data)
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['team_name'], 'Mavericks')
        self.assertIn('position', data)
        self.assertIn('jersey', data)

    @patch('app.get_daily_player')
    @patch('app.commonplayerinfo.CommonPlayerInfo')
    @patch('app.all_players', new=[{'id': 1628991, 'full_name': 'Luka Doncic', 'is_active': True}])
    def test_check_guess_correct(self, mock_player_info, mock_get_daily_player):
        """
        Test the /api/check-guess endpoint with a correct guess.
        """
        # Mock the get_daily_player function to control the correct answer
        mock_get_daily_player.return_value = {
            'date': str(date.today()),
            'id': 1628991,
            'full_name': 'Luka Doncic',
            'clues': {
                'team_city': 'Dallas',
                'team_name': 'Mavericks',
                'position': 'Guard-Forward',
                'jersey': '77'
            }
        }

        # Mock the CommonPlayerInfo API call for the guess
        mock_player_info.return_value.common_player_info.get_dict.return_value = {
            "headers": ['DISPLAY_FIRST_LAST', 'TEAM_CITY', 'TEAM_NAME', 'POSITION', 'JERSEY', 'PLAYER_ID'],
            "data": [
                ['Luka Doncic', 'Dallas', 'Mavericks', 'Guard-Forward', '77', 1628991]
            ]
        }

        # Make a POST request with the correct guess
        response = self.app.post('/api/check-guess',
                                 data=json.dumps({'guess': 'Luka Doncic'}),
                                 content_type='application/json')
        data = json.loads(response.data)
        
        # Assertions based on the latest app.py response format
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['correct'])
        self.assertEqual(data['message'], 'You got it!')
        self.assertDictEqual(data['clue_feedback'], {
            'team_correct': True,
            'position_correct': True,
            'jersey_correct': True,
            'jersey_hint': ''
        })

    @patch('app.get_daily_player')
    @patch('app.commonplayerinfo.CommonPlayerInfo')
    def test_check_guess_incorrect_with_feedback(self, mock_player_info, mock_get_daily_player):
        """
        Test the /api/check-guess endpoint with an incorrect guess
        and verify the returned feedback.
        """
        # Mock the get_daily_player function to control the correct answer
        mock_get_daily_player.return_value = {
            'date': str(date.today()),
            'id': 1628991,
            'full_name': 'Luka Doncic',
            'clues': {
                'team_city': 'Dallas',
                'team_name': 'Mavericks',
                'position': 'Guard-Forward',
                'jersey': '77'
            }
        }
        
        # Mock the CommonPlayerInfo API call for the incorrect guess
        mock_player_info.return_value.common_player_info.get_dict.return_value = {
            "headers": ['DISPLAY_FIRST_LAST', 'TEAM_CITY', 'TEAM_NAME', 'POSITION', 'JERSEY', 'PLAYER_ID'],
            "data": [
                ['Stephen Curry', 'Golden State', 'Warriors', 'Guard', '30', 201939]
            ]
        }
        
        # Make a POST request with an incorrect guess
        response = self.app.post('/api/check-guess',
                                 data=json.dumps({'guess': 'Stephen Curry'}),
                                 content_type='application/json')
        data = json.loads(response.data)

        # Assertions based on the latest app.py response format
        self.assertEqual(response.status_code, 200)
        self.assertFalse(data['correct'])
        self.assertEqual(data['message'], 'Try again!')
        self.assertEqual(data['guessed_player_name'], 'Stephen Curry')
        self.assertDictEqual(data['clue_feedback'], {
            'team_correct': False,
            'position_correct': False,
            'jersey_correct': False,
            'jersey_hint': 'up'
        })

if __name__ == '__main__':
    unittest.main()
