import unittest
import base64
from mock import patch
from flask import Flask, session
import requests
from dotenv import load_dotenv
# Assuming these imports are available
from app import app
import service

class TestFlaskRoutes(unittest.TestCase):
    def setUp(self):
        # Setup the Flask test client and other initial configurations
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.app.secret_key = 'test_secret'

    def test_login(self):
        # Test the login redirection to Spotify's authorization URL
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 302)
        self.assertTrue("accounts.spotify.com" in response.headers['Location'])

    @patch('requests.post')
    def test_callback(self, mock_post):
        # Mocking requests.post to simulate Spotify's token exchange
        mock_post.return_value.json.return_value = {
            'access_token': 'dummy_access_token'
        }
        with self.app.session_transaction() as sess:
            sess['user_id'] = 'test_user'

        response = self.app.get('/callback?code=dummy_code')
        self.assertEqual(response.status_code, 302)
        self.assertIn('map?token=', response.headers['Location'])

    @patch('requests.get')
    def test_user(self, mock_get):
        # Mocking requests.get to simulate fetching user data from Spotify
        mock_get.return_value.json.return_value = {
            'id': 'test_id',
            'email': 'test@example.com'
        }
        response = self.app.post('/user', json={'token': 'dummy_token'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['id'], 'test_id')

    def test_google_key(self):
        # Test the Google API key endpoint
        with app.app_context():
            app.config['GOOGLE_API_KEY'] = 'dummy_google_key'
        response = self.app.get('/googlekey')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['google_api_key'], 'dummy_google_key')


    def test_app_initialization(self):
        """Test application setup and configuration."""
        self.assertIsNotNone(app.config['SECRET_KEY'])
        self.assertTrue(app.config['TESTING'])
        self.assertEqual(app.config['CORS_HEADERS'], 'Content-Type')


    def test_spotify_oauth_setup(self):
        """Test the initialization of SpotifyOAuth with correct parameters."""
        oauth = SpotifyOAuth(client_id='your_client_id', client_secret='your_client_secret', redirect_uri='your_redirect_uri')
        self.assertIsNotNone(oauth)

    def test_session_management(self):
        """Test that session variables are set correctly after login."""
        with self.app as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 'test_user_id'
                response = client.get('/some_route')
        # Verify session is retained across requests
                self.assertEqual(session.get('user_id'), 'test_user_id')

    @patch('database.setup_db')
    def test_database_setup(self, mock_setup_db):
        """Test database setup call."""
        mock_setup_db.return_value = True
        response = self.app.get('/init_db')
        self.assertTrue(mock_setup_db.called)
        self.assertEqual(response.status_code, 200)

    def test_error_handling(self):
        """Test application error handling behavior."""
        response = self.app.get('/route_that_fails')
        self.assertEqual(response.status_code, 500)
        self.assertIn('error', response.get_json())

    @patch('service.spotify_api_call')
    def test_invalid_spotify_token(self, mock_spotify_api):
        """Test handling of expired or invalid Spotify tokens."""
        mock_spotify_api.side_effect = Exception('Token expired')
        response = self.app.get('/user_profile')
        self.assertEqual(response.status_code, 401)  


if __name__ == '__main__':
    unittest.main()
