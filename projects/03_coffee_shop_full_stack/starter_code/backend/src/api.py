import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import sys

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()


# ROUTES
@app.route('/drinks')
def get_drinks():
    """
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where
    drinks is the list of drinks
    or appropriate status code indicating reason for failure
    """
    try:
        drinks = list(map(Drink.short, Drink.query.all()))
        return jsonify({
            'success': True,
            'drinks': drinks,
        }), 200

    except Exception:
        print(sys.exc_info())
        abort(500)


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(token):
    """
    GET /drinks-detail
    it should require the 'get:drinks-detail' permission
    it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
     where drinks is the list of drinks
    or appropriate status code indicating reason for failure
    """
    try:
        drinks = list(map(Drink.long, Drink.query.all()))
        return jsonify({
            'success': True,
            'drinks': drinks,
        }), 200

    except Exception:
        abort(500)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(jwt):
    """
        POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where
    drink an array containing only the newly created
     drink or appropriate status code indicating reason for failure
    """
    try:
        data = request.get_json()

        recipe = data.get('recipe') if type(data.get('recipe')) == str \
            else json.dumps(data.get('recipe'))

        drink = Drink(title=data.get('title', None),
                      recipe=recipe)
        drink.insert()
        drinks = list(map(Drink.long, Drink.query.all()))
        return jsonify({
            'success': True,
            'drinks': drinks,
        }), 200
    except Exception:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(jwt, drink_id):
    """updates a drink in database"""

    data = request.get_json()
    drink = Drink.query.filter_by(id=drink_id).one_or_none()
    # handle invalid drink_id
    if not drink:
        abort(404)
    # bad request for empty title
    if not data.get('title', None):
        abort(400)
    try:
        drink.title = data.get('title', None)
        drink.update()
        drinks = list(map(Drink.long, Drink.query.all()))
        return jsonify({
            'success': True,
            'drinks': drinks,
        })
    except Exception:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    """
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
     where id is the id of the deleted record
        or appropriate status code indicating reason for failure
    """
    drink = Drink.query.filter_by(id=drink_id).one_or_none()
    if not drink:
        abort(404)
    try:
        drink.delete()
        return jsonify({
            'success': True,
            'delete': drink_id,
        })
    except Exception:
        abort(422)

# Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
           "success": False,
           "error": 404,
           "message": "resource not found"
           }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal server error"
    }), 500


@app.errorhandler(AuthError)
def handle_auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['code']
    }), error.status_code
