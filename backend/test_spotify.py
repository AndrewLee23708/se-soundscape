import unittest
from flask import Flask, session, template_rendered
from spotify import app
from contextlib import contextmanager

# Utility to capture templates rendered
@contextmanager
def captured_templates(app):
    recorded = []
    def record(sender, template, context, **extra):
        recorded.append((template, context))
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)

class SpotifyTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    @patch('requests.post')
    def test_callback(self, mock_post):
        # Mock the post request used in the callback to simulate an access token response
        mock_post.return_value.json.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600
        }
        response = self.client.get('/callback?code=valid_code')
        self.assertIn('access_token', session)
        self.assertEqual(session['access_token'], 'new_access_token')
        self.assertRedirects(response, '/playlists')

    @patch('requests.get')
    def test_get_playlists(self, mock_get):
        # Simulate a valid session and a valid API response
        session['access_token'] = 'valid_access_token'
        session['expires_at'] = float('inf')
        mock_get.return_value.json.return_value = {
            "playlists": [
                {"name": "Playlist One", "id": "1"},
                {"name": "Playlist Two", "id": "2"}
            ]
        }
        response = self.client.get('/playlists')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Playlist One', response.data.decode())

    @patch('requests.post')
    def test_refresh_token(self, mock_post):
        # Simulate an expired access token and a successful refresh
        session['refresh_token'] = 'valid_refresh_token'
        session['expires_at'] = 0
        mock_post.return_value.json.return_value = {
            "access_token": "refreshed_access_token",
            "expires_in": 3600
        }
        response = self.client.get('/refresh-token')
        self.assertIn('access_token', session)
        self.assertEqual(session['access_token'], 'refreshed_access_token')
        self.assertRedirects(response, '/playlists')

if __name__ == '__main__':
    unittest.main()
