from crypt import methods
import os
from turtle import title
from flask import Flask, request, jsonify, abort
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} 
        where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def get_all_drinks():
    try:
        drinks = Drink.query.all()
        # returning it as a list of drink.short() data representation
        drinks = [drink.short() for drink in drinks]

        return jsonify({
            'success' : True,
            'drinks' : drinks
        })
    except Exception as e:
        print(f'error with exception {e}')
        abort(500)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} 
        where drinks is the list of drinks or appropriate status 
        code indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drink_detail(jwt):
    try:
        drinks = Drink.query.all()
        # returning it as a list of drink.long() data representation
        drinks = [drink.long() for drink in drinks]

        return jsonify({
            'success' : True,
            'drinks' : drinks
        })
    except Exception as e:
        print(f'error with exception {e}')
        abort(401)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} 
        where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(jwt):
    body = request.get_json()
    # print(body)

    if 'title' not in body.keys() and 'recipe' not in body.keys():
        abort(422)

    drink_title = body['title']
    print(drink_title)
    drink_recipe = body['recipe']
    print(drink_recipe)

    if not isinstance(drink_recipe, list):
        abort(422)
    for ingridient in drink_recipe:
        if 'name' not in ingridient and 'color' not in ingridient and 'parts' not in ingridient:
            abort(422)
    drink_recipe = json.dumps(drink_recipe)
    try:
        drink = Drink(title=drink_title, recipe=drink_recipe)
        drink.insert()
    except Exception as e:
        print(f'error with exception {e}')
        print(f'unable to post drink with recipe {drink_recipe}')
        abort(422)
    return jsonify({
        'success' : True,
        'drink' : [drink.long()]
    })


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} 
        where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(jwt, drink_id):
    drink = Drink.query.get(drink_id)
    if not drink:
        abort(404)
    body = request.get_json()

    if 'title' not in body.keys() and 'recipe' not in body.keys():
        abort(422)
    
    if 'title' in body:
        drink.title = body['title']
    if 'recipe' in body:
        drink_recipe = body['recipe']
        if not isinstance(drink_recipe, list):
            abort(422)
        for ingridient in drink_recipe:
            if 'name' not in ingridient and 'color' not in ingridient and 'parts' not in ingridient:
                abort(422)
        drink_recipe = json.dumps(drink_recipe)
        drink.recipe = drink_recipe

    try:
        drink.update()
    except Exception as e:
        print(f'An error occured while updating the drink with id {drink_id} with {e}')
        abort(422)
    return jsonify({
        'success' : True,
        'drinks' : [drink.long()]
    })


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} 
        where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    drink = Drink.query.get(drink_id)
    if not drink:
        abort(404)
    try:
        drink.delete()
    except Exception as e:
        print(f'exception occured while deleting the drink with id {drink_id} with {e}')
        abort(422)
    return jsonify({
        'success' : True,
        'delete' : drink_id
    })


# Error Handling
'''
Example error handling for unprocessable entity
'''

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def handle_auth_error(e):
    return jsonify({
        'success' : False,
        'error' : e.status_code,
        'message' : e.error
    }), e.status_code
