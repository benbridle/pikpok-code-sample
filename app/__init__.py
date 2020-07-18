from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

from app import models

db.create_all()

# These imports import from this module to get database
# access, so they're kept at the bottom of the module to
# prevent cyclic imports.
from app.routes.api import api
from app.routes.website import website

app.register_blueprint(api, url_prefix="/api")
app.register_blueprint(website, url_prefix="/")
