import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # Set up CORS. Allow '*' for origins.
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,  PUT, POST, DELETE, OPTIONS')
        return response

    @app.route('/categories')
    def retrieve_categories():
        """ Get for all available categories
        returns 404 if categories are not found
        """
        categories = list(map(Category.format, Category.query.all()))
        if len(categories) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'categories': categories
        })

    @app.route('/questions')
    def retrieve_questions():
        """ Get for all available questions returns 404
        if questions are not found
        """
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        categories = list(map(Category.format, Category.query.all()))
        if len(current_questions) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'categories': categories,
            'current_category': None
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        """ Delete a question given id returns 422 if the operation fails
        """
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
            if not question:
                abort(422)
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'total_questions': len(selection)
            })
        except Exception:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def create_question():
        """ Create a question given id
        returns 422 if the operation fails
        """
        body = request.get_json()
        try:
            question = Question(
                question=body.get('question', None),
                answer=body.get('answer', None),
                category=body.get('category', None),
                difficulty=body.get('difficulty', None)
            )
            question.insert()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            return jsonify({
                'success': True,
                'created': question.id,
                'questions': current_questions,
                'total_questions': len(selection)
            })
        except Exception:
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_question():
        """ Search a question by searchTerm returns 404
         if the operation fails to signify missing resource
        """
        body = request.get_json()
        search_term = body.get('searchTerm', '')
        if not search_term:
            abort(422)
        try:
            selection = Question.query.order_by(Question.id).filter(
                Question.question.ilike(f'%{search_term}%')
            ).all()
            if not selection:
                abort(404)
            current_questions = paginate_questions(request, selection)
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(selection),
                'current_category': None
            })
        except Exception:
            abort(404)

    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        """ Search a question given category_id returns 422
        if the operation fails
        """
        category = Category.query.filter_by(id=category_id).one_or_none()
        if not category:
            abort(422)
        try:
            selection = Question.query.filter_by(category=category_id).all()
            if not selection:
                abort(422)
            current_questions = paginate_questions(request, selection)
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(selection),
                'current_category': category.type
            })
        except Exception:
            abort(422)

    @app.route('/quizzes', methods=['POST'])
    def get_question_for_quiz():
        """ Get a question for a quiz return 400 if fails"""
        body = request.get_json()
        previous_questions = body.get('previous_questions', None)
        quiz_category = body.get('quiz_category', None)
        if previous_questions is None or quiz_category is None:
            abort(400)
        query = Question.query
        if quiz_category['id'] != 0:
            query = query.filter(~Question.id.in_(previous_questions)) \
                .filter_by(category=quiz_category['id'])
        else:
            query = query.filter(~Question.id.in_(previous_questions))
        questions = query.all()

        if questions:
            next_question = random.choice(questions)
            return jsonify({
                'success': True,
                'question': Question.format(next_question)
            })
        else:
            abort(404)

    '''
  Create error handlers for all expected errors
  including 404 and 422.
  '''
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal server error"
        }), 500

    return app
