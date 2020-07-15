from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# These imports import from this module to get database
# access, so they're kept at the bottom of the module to
# prevent cyclic imports.
from app import models
from app.routes.api import api

# Generate database tables
db.create_all()
app.register_blueprint(api, url_prefix="/api")
