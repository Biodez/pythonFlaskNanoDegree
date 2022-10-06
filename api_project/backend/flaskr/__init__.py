from crypt import methods
import json
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate(request, all_questions):
    page = request.args.get('page', 1, type=int);
    start = (page - 1) * QUESTIONS_PER_PAGE;
    end = start + QUESTIONS_PER_PAGE;

    formatted_question = [question.format() for question in all_questions];
    current_question = formatted_question[start:end];
    return current_question;

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    # CORS(app)
    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PATCH,POST,DELETE,OPTIONS"
        )
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/api/categories')
    def get_all_available_categories():
        categories = Category.query.all()
        if len(categories) == 0:
            abort(404)
        else:
            all_category = {cat.id:cat.type for cat in categories}
            return jsonify({
                'success' : True,
                'categories' : all_category,
                'number_of_categories' : len(categories)
            })
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/api/questions')
    def get_questions():
        categories = Category.query.all()
        all_category = {cat.id:cat.type for cat in categories}
        all_questions = Question.query.all()
        current_question = paginate(request, all_questions)
        if len(current_question) == 0:
            abort(404)
        else:
            return jsonify({
                'success' : True,
                'questions' : current_question,
                'total_questions' : len(all_questions),
                'current_category' : None,
                'categories' : all_category
            })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/api/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none();
            if question is None:
                abort(404)
            question.delete()
            return jsonify({
                'success' : True,
                'message' : f'The question with the id {question_id} was deleted successfully!!!'
            })
        except:
            abort(422)
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/api/questions/search', methods=['POST'])
    def add_new_question():
        body = request.get_json()

        new_question = body.get('question', None);
        new_answer = body.get('answer', None);
        new_category = body.get('category', None);
        new_difficulty = body.get('difficulty', None);
        try:
            question = Question(question = new_question, answer = new_answer, category = new_category, difficulty = new_difficulty)
            question.insert()
        except:
            abort(422) 
        return jsonify({
            'success' : True,
            'added' : question.id
        })
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/api/questions', methods=['POST'])
    def search_question():
        body = request.get_json()
        search = body.get('searchTerm', None)
        print(search)
        try:
            all_question = Question.query.order_by(Question.id).filter(Question.question.ilike(f"%{search}%")).all()
            print(all_question)
            if len(all_question) == 0:
                abort(404)
            current_question = paginate(request, all_question)
            print(current_question)
            return jsonify({
                'success' : True,
                'questions' : current_question,
                'total_questions' : len(current_question),
                'current_category' : None
            })
        except:
            abort(422)
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/api/categories/<int:category_id>/questions')
    def get_question_based_on_category(category_id):
        curr_category = Category.query.get(category_id);
        # print(curr_category)

        if curr_category is None:
            abort(404);
        curr_category = curr_category.format();

        questions_based_on_category = Question.query.filter_by(category = str(category_id)).all()
        # print(questions_based_on_category)
        current_question = paginate(request, questions_based_on_category)

        return jsonify({
            'success' : True,
            'questions' : current_question,
            'total_questions' : len(current_question),
            'categories' : curr_category,
            'current_category' : category_id
        })
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/api/quizzes', methods=['POST'])
    def get_quiz_question():
            body = request.get_json()

            prev_questions = body.get('previous_questions', None)
            quiz_category = body.get('quiz_category', None)
            # print(quiz_category)
            quiz_id = quiz_category['id']
            if quiz_id == 0:
                questions = Question.query.all()
            else:
                questions = Question.query.filter_by(category = str(quiz_id)).all()
            questions = [question.format() for question in questions]
            question_category = []

            for qusn in questions:
                if qusn['id'] not in prev_questions:
                    question_category.append(qusn)

            if (len(question_category) == 0):
                return jsonify({
                    'success' : True
                })
            question = random.choice(question_category)

            return jsonify({
                'success' : True,
                'question' : question
            })
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def bad_request(error):
        return jsonify({
            "error": 404,
            "message": "Not found.",
            "success": False
        }), 400
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            "error": 422,
            "message": "Unprocessable.",
            "success": False
        }), 422

    return app

