import unittest
from attendance_system.app import create_app, db
from attendance_system.app.models import User, Class, Student, Attendance # Added Attendance
from attendance_system.config import TestingConfig

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        """
        Called before every test.
        Set up the test environment.
        """
        self.app = create_app(TestingConfig)  # Pass the TestingConfig class itself
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

        # You can create initial common test data here if needed
        # For example, a default admin user or common classes

    def tearDown(self):
        """
        Called after every test.
        Clean up the test environment.
        """
        db.session.remove()  # Ensure session is closed
        db.drop_all()        # Drop all tables
        self.app_context.pop() # Pop the application context

    # Helper methods can be added here
    def register_user(self, username="testuser", password="password"):
        return self.client.post('/register', data=dict(
            username=username,
            password=password,
            confirm_password=password
        ), follow_redirects=True)

    def login_user(self, username="testuser", password="password"):
        # First, ensure user is registered if not using a pre-made one
        # For simplicity, assume user is registered or this helper is used after registration
        return self.client.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout_user(self):
        return self.client.get('/logout', follow_redirects=True)

    # Helper methods for creating common objects
    def create_class(self, name="Test Class", teacher_name="Mr. Test"):
        new_class = Class(name=name, teacher_name=teacher_name)
        db.session.add(new_class)
        db.session.commit()
        return new_class

    def create_student(self, first_name="Test", last_name="Student", class_obj=None):
        # If class_obj is provided, assign student to it
        # Ensure class_obj is committed if it's new
        student_data = {
            'first_name': first_name,
            'last_name': last_name
        }
        if class_obj:
            student_data['class_id'] = class_obj.id

        new_student = Student(**student_data)
        db.session.add(new_student)
        db.session.commit()
        return new_student

    def create_attendance_record(self, student_obj, class_obj, att_date, is_present=True):
        att = Attendance(student_id=student_obj.id, class_id=class_obj.id, date=att_date, is_present=is_present)
        db.session.add(att)
        db.session.commit()
        return att
