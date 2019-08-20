from flask import Flask, jsonify, has_request_context, request, g
from flask_httpauth import HTTPBasicAuth
from flask_json_schema import JsonSchema, JsonValidationError
from pymongo.errors import PyMongoError
from werkzeug.exceptions import HTTPException

from route import init_route
from storage import mongoengine_сonnect

app = Flask(__name__)

schema = JsonSchema(app)

db = mongoengine_сonnect()

auth = HTTPBasicAuth()

init_route(app)


@app.after_request
def history(response):
    user = getattr(g, 'user', None)
    username = 'guest'
    user_id = 'guest'
    ip = ''

    if user is not None:
        username = user.username
        user_id = str(user.id)

    if has_request_context():
        ip = request.remote_addr

    app.logger.info('%s\t%s\t%s' % (username, user_id, ip))

    return response


@app.errorhandler(JsonValidationError)
def validation_error(e):
    content = jsonify({
        'error': '%s. %s' % (e.message, '. '.join(validation_error.message for validation_error in e.errors))
    })
    return content, 400


@app.errorhandler(HTTPException)
def http_error(e):
    return jsonify({'error': str(e)}), e.code


@app.errorhandler(PyMongoError)
def db_error(e):
    return jsonify({'error': 'DataBaseError: %s' % str(e)}), 500


# @app.errorhandler(Exception)
# def handler_error(e):
#     return jsonify({'error': str(e)}), 500
