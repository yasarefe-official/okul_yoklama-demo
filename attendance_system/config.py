import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    # Adjust the path to be relative to the instance folder if using instance_relative_config=True
    # For now, create it in the root 'attendance_system' directory, one level above 'app'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True # Default, can be overridden by TestingConfig

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Use in-memory SQLite database for tests
    WTF_CSRF_ENABLED = False # Disable CSRF protection for simpler form testing in unit tests
    # LOGIN_DISABLED can be set here if needed, but Flask-Login's own testing utilities are often preferred
    # For example, by directly logging in a test user without going through the form.
    # SECRET_KEY is inherited from Config
