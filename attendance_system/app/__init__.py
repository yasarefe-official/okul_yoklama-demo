from flask import Flask
from config import Config # Assuming attendance_system is in PYTHONPATH
from .models import db, User # Import db and User model
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_view = 'login' # Adjusted as per instruction, will be routes.login
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app) # Initialize db with the app
    login_manager.init_app(app) # Initialize login_manager with the app

    from . import routes # Import routes module

    # Register routes from the routes module
    app.add_url_rule('/', 'home', routes.home)
    # app.add_url_rule('/home', 'home_alt', routes.home) # 'home' endpoint covers both / and /home via routes.py logic if desired, or keep separate
    app.add_url_rule('/home', 'home', routes.home)
    app.add_url_rule('/register', 'register', routes.register, methods=['GET', 'POST'])
    app.add_url_rule('/login', 'login', routes.login, methods=['GET', 'POST'])
    app.add_url_rule('/logout', 'logout', routes.logout)

    # Class management routes
    app.add_url_rule('/classes', 'classes_list', routes.classes_list)
    app.add_url_rule('/add_class', 'add_class', routes.add_class, methods=['GET', 'POST'])
    app.add_url_rule('/edit_class/<int:class_id>', 'edit_class', routes.edit_class, methods=['GET', 'POST'])
    app.add_url_rule('/delete_class/<int:class_id>', 'delete_class', routes.delete_class, methods=['POST'])

    # Student management routes
    app.add_url_rule('/students', 'students_list', routes.students_list)
    app.add_url_rule('/add_student', 'add_student', routes.add_student, methods=['GET', 'POST'])
    app.add_url_rule('/edit_student/<int:student_id>', 'edit_student', routes.edit_student, methods=['GET', 'POST'])
    app.add_url_rule('/delete_student/<int:student_id>', 'delete_student', routes.delete_student, methods=['POST'])

    # Attendance route
    app.add_url_rule('/attendance/take', 'take_attendance', routes.take_attendance, methods=['GET', 'POST'])
    app.add_url_rule('/attendance/view', 'view_attendance', routes.view_attendance, methods=['GET', 'POST'])

    # The login_manager.login_view = 'login' set earlier will use the 'login' endpoint defined above.
    # current_user will be available in templates due to login_manager.

    return app

def create_db(app_instance):
    with app_instance.app_context():
        db.create_all()
