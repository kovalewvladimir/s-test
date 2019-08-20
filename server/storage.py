import os

import mongoengine

from config import MAX_CONNECT_COUNT
from model import ConnectionApplication


def mongoengine_сonnect():
    from main import app

    db = os.environ.get('MONGODB_DB', 'test')
    host = os.environ.get('MONGODB_HOST', 'localhost')
    port = int(os.environ.get('MONGODB_PORT', '27017'))
    auth_source = os.environ.get('MONGODB_AUTH_SOURCE', 'admin')
    username = os.environ.get('MONGODB_USERNAME', 'root')
    password = os.environ.get('MONGODB_PASSWORD', 'example')

    mongoengine_connect = mongoengine.connect(
        db,
        host=host,
        port=port,
        username=username,
        password=password,
        authentication_source=auth_source
    )

    ca = ConnectionApplication()

    is_connect = False
    connect_count = 1
    while not is_connect:
        try:
            ca.save()
            is_connect = True
        except Exception as e:
            app.logger.warning('Warning connecting to the database. %d of %d' % (connect_count, MAX_CONNECT_COUNT))
            app.logger.warning(str(e))
            connect_count += 1
            if connect_count > MAX_CONNECT_COUNT:
                app.logger.error('Error connecting to the database')
                raise SystemExit(1)

    return mongoengine_connect
