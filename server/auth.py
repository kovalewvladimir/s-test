import mongoengine as db
from flask import Blueprint, abort, request, jsonify, g

from application import schema, auth
from model import User

bp = Blueprint('auth', __name__, url_prefix='/api/v1.0/auth/')

json_schema = {
    'registration': {
        'required': ['username', 'password'],
        'properties': {
            'username': {'type': 'string'},
            'password': {'type': 'string'},
        }
    },
}


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        try:
            user = User.objects.get(username=username_or_token)
        except db.queryset.DoesNotExist:
            user = None
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@bp.route('/registration', methods=['POST'])
@schema.validate(json_schema['registration'])
def registration():
    username = request.json.get('username')
    password = request.json.get('password')

    is_user_registered = len(User.objects(username=username)) != 0
    if is_user_registered:
        abort(409, 'existing user')

    user = User()
    user.username = username
    user.hash_password(password)
    user.save()

    return jsonify({'username': user.username}), 201


@bp.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})
