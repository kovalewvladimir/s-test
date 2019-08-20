import mongoengine as db
import requests
from flask import Blueprint, g, jsonify, abort, request
from werkzeug.debug.tbtools import Traceback

from auth import auth, schema

bp = Blueprint('joke', __name__, url_prefix='/api/v1.0/joke/')

json_schema = {
    'joke': {
        'required': ['joke'],
        'properties': {
            'joke': {'type': 'string'},
        }
    },
    'generate': {
        'required': ['save'],
        'properties': {
            'save': {'type': 'boolean'},
        }
    },
}


@bp.route('/list', methods=['GET'])
@auth.login_required
def get_list_joke():
    jokes_db = g.user.jokes
    jokes = []
    for joke in jokes_db:
        jokes.append({
            'id': str(joke.joke_id),
            'joke': joke.joke,
        })
    return jsonify(jokes)


@bp.route('/', methods=['POST'])
@schema.validate(json_schema['joke'])
@auth.login_required
def create_joke():
    joke = request.json.get('joke')
    jokes = g.user.jokes
    joke_db = jokes.create(joke=joke)
    jokes.save()
    return {'id': str(joke_db.joke_id), 'joke': joke_db.joke}


@bp.route('/generate', methods=['POST'])
@schema.validate(json_schema['generate'])
@auth.login_required
def generate_joke():
    is_save = request.json.get('save')
    response = requests.get('https://geek-jokes.sameerkumar.website/api')
    text_joke = response.text.replace('"', '')
    joke_id = ''
    if is_save:
        jokes = g.user.jokes
        joke_db = jokes.create(joke=text_joke)
        joke_id = str(joke_db.joke_id)
        jokes.save()
    return {'id': joke_id, 'joke': text_joke}


@bp.route('/<id>', methods=['GET'])
@auth.login_required
def get_joke(id):
    if len(id) != 24:
        abort(400, 'id must contain 24 characters')
    try:
        joke = g.user.jokes.get(joke_id=id)
    except db.queryset.DoesNotExist:
        abort(404, 'No joke found')
    return {'id': id, 'joke': joke.joke}


@bp.route('/<id>', methods=['PUT'])
@schema.validate(json_schema['joke'])
@auth.login_required
def change_joke(id):
    new_joke = request.json.get('joke')

    if len(id) != 24:
        abort(400, 'id length 24')

    joke = g.user.jokes.filter(joke_id=id)
    count_update = joke.update(joke=new_joke)
    if count_update == 1:
        joke.save()
    else:
        abort(404, 'No joke found')

    return {'id': id, 'joke': joke[0].joke}


@bp.route('/<id>', methods=['DELETE'])
@auth.login_required
def delete_joke(id):
    if len(id) != 24:
        abort(400, 'id length 24')

    joke = g.user.jokes.filter(joke_id=id)
    count_delete = joke.delete()
    if count_delete == 1:
        joke.save()
    else:
        abort(404, 'No joke found')
    return {'delete': True}
