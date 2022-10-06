import os
from random import random
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('trivia', 'trivia','localhost:5432', self.database_name)
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
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_all_available_categories(self):
        """A get request to the /api/categories endpoint should return all available categories"""

        endpoint = '/api/categories'
        response_object = self.client().get(endpoint)
        response = json.loads(response_object.get_data())

        self.assertEqual(response_object.status_code, 200)
        self.assertTrue(response['success'])
        self.assertEqual(type(response['categories']), dict)
        self.assertEqual(type(response['number_of_categories']), int)

    def test_get_questions(self):
        """A get request to the /api/questions endpoint should return a list of questions, total_questions, current_category, categories."""

        endpoint = '/api/questions'
        response_object = self.client().get(endpoint)
        response = json.loads(response_object.get_data())

        self.assertEqual(response_object.status_code, 200)
        self.assertTrue(response['success'])

        self.assertEqual(type(response['questions']), list)

        self.assertEqual(type(response['total_questions']), int)

        self.assertEqual(type(response['categories']), dict)
        pass

    def test_404_get_questions(self):
        """A request for a question that does not exist should return a 404"""

        endpoint = '/api/questions?page=20000'
        response_object = self.client().get(endpoint)
        response = json.loads(response_object.get_data())

        self.assertEqual(response_object.status_code, 404)
        pass
    
    def test_delete_question(self):
        """A request to delete a specific question with the specified id should return a 200 status code and should delete the given question id from the database"""

        question_id = Question.query.first().format()['id']
        endpoint = f"/api/questions/{question_id}"

        response_object = self.client().delete(endpoint)
        response_data = json.loads(response_object.get_data())

        data_from_db = Question.query.get(question_id)

        self.assertEqual(response_object.status_code, 200)
        self.assertEqual(data_from_db, None)
        pass

    
    def test_404_delete_non_existent_question(self):
        """A request to delete a question with a id that does not exist should return a 404 status code"""
        question_id = 3000;
        endpoint = f"/api/questions/{question_id}"

        response_object = self.client().delete(endpoint)
        response = json.loads(response_object.get_data())

        self.assertEqual(response_object.status_code, 404)
        pass

    def test_add_new_question(self):
        """A request to post a new question with all required parameters should return a 200 status code"""

        endpoint = '/api/questions'
        payload = {"question": "'experimental method of 1EXR?'", "answer": "x-ray diffusion", "category": 1, "difficulty": 5}

        response_object = self.client().post(endpoint, json=payload)
        response_data = json.loads(response_object.get_data())

        self.assertEqual(response_object.status_code, 200)
        pass

    def test_get_question_based_on_category(self):
        """A request to this endpoint should return only questions which fall within that specific category."""

        categories = Category.query.all()
        curr_categories = [category.format() for category in categories]

        for cat in curr_categories:
            cat_id = cat['id']
            cat_type = cat['type']
            endpoint = f"/api/categories/{cat_id}/questions"
            response_object = self.client().get(endpoint)
            response = json.loads(response_object.get_data())
            self.assertEqual(response_object.status_code, 200)
            self.assertEqual(response['current_category'], cat_type)
            self.assertEqual(response['success'], True)
            questions = response['questions']
            for question in questions:
                self.assertEqual(question['category'], cat_id)
            self.assertEqual(type(response['total_questions']), int)
        pass

    def test_search_question(self):
        """A request to get questions by search term should return all questions which contain the search term as a substring"""
        qusn = Question.query.first()
        search = ""

        if qusn is not None:
            first_qusn = qusn.format()['question']
            question = first_qusn.split()
            search = question[random.randint(
                0, len(question)-1)]

        payload = {"searchTerm": search}
        endpoint = "/api/questions/search"

        response_object = self.client().post(endpoint, json=payload)
        response = json.loads(response_object.get_data())

        self.assertEqual(type(response['questions']), list)
        self.assertEqual(response_object.status_code, 200)
        pass

    def test_get_quiz_question(self):
        categories = Category.query.all()
        all_cat = [category.format() for category in categories]
        category = all_cat[random.randint(0, len(all_cat) - 1)]
        questions = Question.query.filter_by(category = str(category['id'])).limit(2).all()
        prev_qusn = [question.format()['id'] for question in questions]

        payload = {
            'previous_questions' : prev_qusn,
            'quiz_category' : category
        }

        endpoint = '/api/quizzes'
        response_object = self.client().post(endpoint, json=payload)
        response = json.loads(response_object.get_data())

        self.assertEqual(response_object.status_code, 200)
        question_gotten = response['question']

        for qustion in prev_qusn:
            self.assertNotEqual(qustion, question_gotten['id'])
        self.assertEqual(category['id'], question_gotten['category'])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()