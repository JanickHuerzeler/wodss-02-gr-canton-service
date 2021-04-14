from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from configManager import ConfigManager
import logging

app = Flask(__name__)

logging.basicConfig(filename='wodss-02-gr-canton-service.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % ConfigManager.get_instance().get_postgres_config()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db = SQLAlchemy(app)


def create_app():
    return app


def get_test_app():
    global db, app
    # app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    db = SQLAlchemy(app) # overwrite the postgresql settings, as db gets referenced by services
    return app
