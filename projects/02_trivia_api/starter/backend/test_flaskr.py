import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db

DB_HOST = os.getenv('DB_HOST', '127.0.0.1:5432')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
DB_NAME = os.getenv('DB_NAME', 'trivia_test')
DB_PATH = 'postgresql+psycopg2://{}:{}@{}/{}'.format(DB_USER,
                                                     DB_PASSWORD,
                                                     DB_HOST,
                                                     DB_NAME)


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = DB_NAME
        self.database_path = DB_PATH
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for
    expected errors.
    """

    def test_get_paginated_questions(self):
        """Test pagination for questions"""
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data["categories"]))

    def test_404_sent_requesting_beyond_valid_page(self):
        """Test pagination for questions larger than page size returns 404"""
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_questions(self):
        """Test deletion of questions based on given id"""
        res = self.client().delete('/questions/9')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 9)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_422_for_question_does_not_exist(self):
        """Test deletion of invalid questions based on given id"""
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_get_all_categories(self):
        """Test retrieving questions"""
        response = self.client().get('/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_create_new_question(self):
        """Test creating questions"""
        mock_question = {
            'question': 'longest river in the world mock question ',
            'answer': 'Nile - this is a mock answer',
            'difficulty': 2,
            'category': 1
        }
        res = self.client().post('/questions', json=mock_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422_valid_new_question(self):
        """Test creating questions"""

        res = self.client().post('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_get_questions_search_with_results(self):
        """Test Search questions"""

        res = self.client().post('/questions/search',
                                 json={'searchTerm': 'earned'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_get_questions_search_without_results(self):
        """Test empty Search questions"""

        res = self.client().post('/questions/search',
                                 json={'searchTerm': 'applejacks'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_get_questions_search_term(self):
        """Test empty Search questions"""

        res = self.client().post('/questions/search', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_get_questions_by_category(self):
        """Test get questions by category"""

        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_422_get_questions_by_category(self):
        """Test get questions by category"""
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)

    def test_get_question_for_quiz(self):
        """Test get question by quiz"""
        mock_data = {
            'previous_questions': [],
            'quiz_category': {
                'type': 'Geography',
                'id': 3
            }
        }
        res = self.client().post('/quizzes', json=mock_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    def test_400_get_question_for_quiz(self):
        """Test get question by quiz that is not valid"""
        mock_data = {
            'previous_questions': []
        }
        res = self.client().post('/quizzes', json=mock_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data['message'], 'bad request')

    def test_422_post_play_quiz(self):
        """Test get question by quiz that is not valid"""
        mock_data = {
            'previous_questions': [],
            'quiz_category': {
                'type': 'test',
                'id': 88
            }
        }
        res = self.client().post('/quizzes', json=mock_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
