import unittest
from app import create_app, db
from app.models import User
import json

class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_class='config.TestConfig')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_summarize_api(self):
        test_text = "Goal! Manchester United scores in the 45th minute. Amazing shot by Ronaldo!"
        
        response = self.client.post('/api/summarize-text',
                                   data=json.dumps({'text': test_text}),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('summary', data)
        self.assertIn('key_events', data)
    
    def test_user_registration(self):
        response = self.client.post('/auth/register',
                                   data={
                                       'username': 'testuser',
                                       'email': 'test@example.com',
                                       'password': 'password123',
                                       'confirm_password': 'password123'
                                   })
        
        self.assertEqual(response.status_code, 302)  # Redirect after registration
        
        # Check if user was created
        user = User.query.filter_by(email='test@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')

if __name__ == '__main__':
    unittest.main()