import unittest

from requests.auth import _basic_auth_str

from application import app, db
from model import User


class TestCase(unittest.TestCase):
    auth_user1_headers = {'Authorization': _basic_auth_str('username1', 'password1')}
    auth_user2_headers = {'Authorization': _basic_auth_str('username2', 'password2')}

    def setUp(self):
        self.app = app.test_client()
        db.drop_database('test')
        self._init_db()

    def tearDown(self):
        db.drop_database('test')

    def _init_db(self):
        joke1 = 'username1_joke1'
        joke2 = 'username2_joke1'

        user1 = User()
        user1.username = 'username1'
        user1.hash_password('password1')
        user1.jokes.create(joke=joke1)
        user1.save()
        self.user1 = {
            'id': str(user1.id),
            'joke_id': str(user1.jokes.get(joke=joke1).joke_id)
        }

        user2 = User()
        user2.username = 'username2'
        user2.hash_password('password2')
        user2.jokes.create(joke=joke2)
        user2.save()
        self.user2 = {
            'id': str(user2.id),
            'joke_id': str(user2.jokes.get(joke=joke2).joke_id)
        }

    def test_create_user(self):
        json = {'username': 'username3', 'password': '123'}
        r = self.app.post('/api/v1.0/auth/registration', json=json)
        assert b'{"username":"username3"}\n' == r.data

    def test_create_user_conflict(self):
        json = {'username': 'username1', 'password': '123'}
        r = self.app.post('/api/v1.0/auth/registration', json=json)
        assert b'Conflict' in r.data

    def test_token(self):
        r = self.app.get('/api/v1.0/auth/token', headers=self.auth_user1_headers)
        assert r.status_code == 200

    def test_create_joke(self):
        json = {
            'joke': 'joke1'
        }
        r = self.app.post('/api/v1.0/joke/', json=json, headers=self.auth_user1_headers)
        assert r.json.get('joke') == 'joke1'

    def test_get_joke1(self):
        r = self.app.get('/api/v1.0/joke/' + self.user1['joke_id'], headers=self.auth_user1_headers)
        assert r.json.get('id') == self.user1['joke_id']

    def test_get_joke2(self):
        r = self.app.get('/api/v1.0/joke/' + self.user1['joke_id'], headers=self.auth_user2_headers)
        assert r.status_code == 404

    def test_change_joke1(self):
        json = {
            'joke': 'change_joke'
        }
        r = self.app.put('/api/v1.0/joke/' + self.user1['joke_id'], json=json, headers=self.auth_user1_headers)
        user = User.objects.get(id=self.user1['id'])
        joke = user.jokes.get(joke_id=self.user1['joke_id']).joke
        assert joke == json['joke']

    def test_change_joke2(self):
        json = {
            'joke': 'change_joke'
        }
        r = self.app.put('/api/v1.0/joke/' + self.user2['joke_id'], json=json, headers=self.auth_user1_headers)
        assert r.status_code == 404

    def test_delete_joke1(self):
        r = self.app.delete('/api/v1.0/joke/' + self.user1['joke_id'], headers=self.auth_user1_headers)
        assert r.json.get('delete')

    def test_delete_joke2(self):
        r = self.app.delete('/api/v1.0/joke/' + self.user2['joke_id'], headers=self.auth_user1_headers)
        assert r.status_code == 404


if __name__ == '__main__':
    unittest.main()
