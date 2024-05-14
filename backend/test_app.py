import unittest
from app import create_app, db

class AppTestCase(unittest.TestCase):

    def setUp(self):
        # Setup a test client
        self.app = create_app('testing')  # This assumes you have a testing config
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        # Set up your database or mock database here
        db.create_all()

    def tearDown(self):
        # Teardown the database to ensure a clean state
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        # Test home page access
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Welcome', response.data.decode('utf-8'))

if __name__ == '__main__':
    unittest.main()
