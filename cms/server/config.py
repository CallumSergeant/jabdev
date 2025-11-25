import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 3001))
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'server/db/jabchem.db')
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    GITHUB_REPO = os.getenv('GITHUB_REPO')
    GITHUB_BRANCH = os.getenv('GITHUB_BRANCH', 'main')
    GIT_USER_NAME = os.getenv('GIT_USER_NAME', 'CMS Bot')
    GIT_USER_EMAIL = os.getenv('GIT_USER_EMAIL', 'cms@example.com')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    UPLOAD_FOLDER = '..'
