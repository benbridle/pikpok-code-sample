import os


class Config(object):
    SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://doctrine:doctrine@localhost/doctrine_game"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
