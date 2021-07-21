import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent


class Config:
    ASANA_CLIENT_ID = os.getenv('ASANA_CLIENT_ID')
    ASANA_SECRET = os.getenv('ASANA_SECRET')
    ASANA_REDIRECT_URL = 'https://6945844d186b.ngrok.io/api/v1/oauth/asana/callback'
    SQLALCHEMY_DATABASE_URI = 'postgresql:///data'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('APP_SECRET_KEY')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    pass


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
