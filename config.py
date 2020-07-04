import os


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "secret-key"
    SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://doctrine:doctrine@localhost/doctrine_game"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
