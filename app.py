from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from configManager import ConfigManager
import logging
import logging.config
from os import path

app = Flask(__name__)

log_file_path = path.join(path.dirname(path.abspath(__file__)), 'log.conf')
logging.config.fileConfig(log_file_path)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % ConfigManager.get_instance().get_postgres_config()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.config['JSON_SORT_KEYS'] = False

db = SQLAlchemy(app)


def create_app():
    return app


def get_test_app():
    global db, app
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    # overwrite the postgresql settings, as db gets referenced by services
    db = SQLAlchemy(app)
    return app
