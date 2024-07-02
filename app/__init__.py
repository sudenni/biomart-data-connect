from flask import Flask

from app.config import Config
from app import pages

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(pages.app)
    return app
