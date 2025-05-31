from .base import BaseTestCase
from attendance_system.app.models import User, db
from flask import get_flashed_messages, url_for

class AuthTestCase(BaseTestCase):

    def test_registration_page_loads(self):
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)

    def test_login_page_loads(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_successful_registration(self):
        response = self.register_user(username="newuser", password="newpassword")
        self.assertEqual(response.status_code, 200) # After redirect to login
        self.assertIn(b'Your account has been created!', response.data) # Check flashed message

        user = User.query.filter_by(username="newuser").first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password("newpassword"))

    def test_registration_existing_username(self):
        # First, register a user
        self.register_user(username="existinguser", password="password")

        # Try to register again with the same username
        response = self.client.post('/register', data=dict(
            username="existinguser",
            password="anotherpassword",
            confirm_password="anotherpassword"
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200) # Stays on registration page or shows error
        self.assertIn(b'That username is already taken.', response.data) # Check form validation error

        # Check that no new user with "existinguser" and "anotherpassword" was created
        # Assuming the first registration was successful and user exists with "password"
        user = User.query.filter_by(username="existinguser").first()
        self.assertTrue(user.check_password("password"))
        self.assertFalse(user.check_password("anotherpassword"))

    def test_successful_login_logout(self):
        # Register user first
        self.register_user(username="loginlogoutuser", password="testpassword")

        # Test login
        response_login = self.login_user(username="loginlogoutuser", password="testpassword")
        self.assertEqual(response_login.status_code, 200) # Redirects to home
        self.assertIn(b'Welcome, loginlogoutuser!', response_login.data) # Assuming home page shows username
        self.assertIn(b'Login Successful!', response_login.data) # Check flashed message

        # Test accessing a protected page (e.g. home)
        response_home = self.client.get('/home')
        self.assertEqual(response_home.status_code, 200)
        self.assertIn(b'Welcome, loginlogoutuser!', response_home.data)

        # Test logout
        response_logout = self.logout_user()
        self.assertEqual(response_logout.status_code, 200) # Redirects to login
        self.assertIn(b'You have been logged out.', response_logout.data) # Check flashed message
        self.assertIn(b'Login', response_logout.data) # Should be back on login page

        # Test accessing protected page after logout
        response_home_after_logout = self.client.get('/home', follow_redirects=True)
        self.assertEqual(response_home_after_logout.status_code, 200) # Redirects to login
        self.assertIn(b'Please log in to access this page.', response_home_after_logout.data) # Flashed message by login_manager
        self.assertIn(b'Login', response_home_after_logout.data) # On login page

    def test_login_invalid_username(self):
        self.register_user(username="realuser", password="realpassword")
        response = self.login_user(username="fakeuser", password="realpassword")
        self.assertEqual(response.status_code, 200) # Stays on login page
        self.assertIn(b'Login Unsuccessful. Please check username and password.', response.data)

    def test_login_invalid_password(self):
        self.register_user(username="anotheruser", password="correctpassword")
        response = self.login_user(username="anotheruser", password="wrongpassword")
        self.assertEqual(response.status_code, 200) # Stays on login page
        self.assertIn(b'Login Unsuccessful. Please check username and password.', response.data)

    def test_login_required_routes_redirect(self):
        # Test /home
        response_home = self.client.get('/home')
        self.assertEqual(response_home.status_code, 302) # Redirect
        self.assertTrue(response_home.location.endswith(url_for('login')))

        # Test /classes (assuming it's login_required)
        response_classes = self.client.get('/classes')
        self.assertEqual(response_classes.status_code, 302)
        self.assertTrue(response_classes.location.endswith(url_for('login')))

        # Test /students (assuming it's login_required)
        response_students = self.client.get('/students')
        self.assertEqual(response_students.status_code, 302)
        self.assertTrue(response_students.location.endswith(url_for('login')))

        # Test /attendance/take (assuming it's login_required)
        response_att_take = self.client.get('/attendance/take')
        self.assertEqual(response_att_take.status_code, 302)
        self.assertTrue(response_att_take.location.endswith(url_for('login')))

        # Test /attendance/view (assuming it's login_required)
        response_att_view = self.client.get('/attendance/view')
        self.assertEqual(response_att_view.status_code, 302)
        self.assertTrue(response_att_view.location.endswith(url_for('login')))

    def test_access_home_after_login(self):
        self.register_user("homeaccessuser", "password")
        self.login_user("homeaccessuser", "password")
        response = self.client.get('/home')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome, homeaccessuser!', response.data)
