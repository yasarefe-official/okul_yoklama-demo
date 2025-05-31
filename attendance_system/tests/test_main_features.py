from .base import BaseTestCase
from attendance_system.app.models import User, Class, Student, Attendance, db
from datetime import date, timedelta
from flask import url_for

class MainFeaturesTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        # Register and log in a test user for authenticated routes
        self.TEST_USERNAME = "mainuser"
        self.TEST_PASSWORD = "mainpassword"
        self.register_user(username=self.TEST_USERNAME, password=self.TEST_PASSWORD)
        self.login_user(username=self.TEST_USERNAME, password=self.TEST_PASSWORD)

    # Class Management Tests
    def test_view_classes_page(self):
        response = self.client.get(url_for('classes_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Manage Classes', response.data)

    def test_add_class(self):
        response_get = self.client.get(url_for('add_class'))
        self.assertEqual(response_get.status_code, 200)
        self.assertIn(b'Add New Class', response_get.data)

        response_post = self.client.post(url_for('add_class'), data=dict(
            name="History 101",
            teacher_name="Dr. Jones"
        ), follow_redirects=True)
        self.assertEqual(response_post.status_code, 200) # Back to classes_list
        self.assertIn(b'Class "History 101" has been added successfully!', response_post.data)

        class_obj = Class.query.filter_by(name="History 101").first()
        self.assertIsNotNone(class_obj)
        self.assertEqual(class_obj.teacher_name, "Dr. Jones")

    def test_edit_class(self):
        class_obj = self.create_class(name="Old Math", teacher_name="Old Teacher")

        response_get = self.client.get(url_for('edit_class', class_id=class_obj.id))
        self.assertEqual(response_get.status_code, 200)
        self.assertIn(b'Edit Class', response_get.data)
        self.assertIn(b'Old Math', response_get.data)

        response_post = self.client.post(url_for('edit_class', class_id=class_obj.id), data=dict(
            name="New Math",
            teacher_name="New Teacher"
        ), follow_redirects=True)
        self.assertEqual(response_post.status_code, 200)
        self.assertIn(b'Class "New Math" has been updated successfully!', response_post.data)

        updated_class = Class.query.get(class_obj.id)
        self.assertEqual(updated_class.name, "New Math")
        self.assertEqual(updated_class.teacher_name, "New Teacher")

    def test_delete_class(self):
        class_obj = self.create_class(name="To Be Deleted")
        class_id = class_obj.id

        response_post = self.client.post(url_for('delete_class', class_id=class_id), follow_redirects=True)
        self.assertEqual(response_post.status_code, 200)
        self.assertIn(b'Class "To Be Deleted" has been deleted successfully!', response_post.data)
        self.assertIsNone(Class.query.get(class_id))

    def test_delete_class_with_students(self):
        class_obj = self.create_class(name="Class With Students")
        self.create_student(first_name="Student", last_name="InClass", class_obj=class_obj)

        response_post = self.client.post(url_for('delete_class', class_id=class_obj.id), follow_redirects=True)
        self.assertEqual(response_post.status_code, 200)
        self.assertIn(b'cannot be deleted because it has students assigned to it', response_post.data)
        self.assertIsNotNone(Class.query.get(class_obj.id)) # Class should still exist

    # Student Management Tests
    def test_view_students_page(self):
        response = self.client.get(url_for('students_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Manage Students', response.data)

    def test_add_student(self):
        class_obj = self.create_class(name="Homeroom A")

        response_get = self.client.get(url_for('add_student'))
        self.assertEqual(response_get.status_code, 200)
        self.assertIn(b'Add New Student', response_get.data)

        response_post = self.client.post(url_for('add_student'), data=dict(
            first_name="John",
            last_name="Doe",
            class_assigned=str(class_obj.id) # QuerySelectField expects the ID as string
        ), follow_redirects=True)
        self.assertEqual(response_post.status_code, 200)
        self.assertIn(b'Student "John Doe" has been added successfully!', response_post.data)

        student = Student.query.filter_by(first_name="John").first()
        self.assertIsNotNone(student)
        self.assertEqual(student.last_name, "Doe")
        self.assertEqual(student.class_id, class_obj.id)

    def test_edit_student(self):
        class1 = self.create_class(name="Class Alpha")
        class2 = self.create_class(name="Class Beta")
        student = self.create_student(first_name="Jane", last_name="Doe", class_obj=class1)

        response_get = self.client.get(url_for('edit_student', student_id=student.id))
        self.assertEqual(response_get.status_code, 200)
        self.assertIn(b'Edit Student', response_get.data)
        self.assertIn(b'Jane', response_get.data)

        response_post = self.client.post(url_for('edit_student', student_id=student.id), data=dict(
            first_name="Janet",
            last_name="Doer",
            class_assigned=str(class2.id)
        ), follow_redirects=True)
        self.assertEqual(response_post.status_code, 200)
        self.assertIn(b'Student "Janet Doer" has been updated successfully!', response_post.data)

        updated_student = Student.query.get(student.id)
        self.assertEqual(updated_student.first_name, "Janet")
        self.assertEqual(updated_student.class_id, class2.id)

    def test_delete_student(self):
        student = self.create_student(first_name="Delete", last_name="Me")
        student_id = student.id

        response_post = self.client.post(url_for('delete_student', student_id=student_id), follow_redirects=True)
        self.assertEqual(response_post.status_code, 200)
        self.assertIn(b'Student "Delete Me" and all associated attendance records have been deleted successfully!', response_post.data)
        self.assertIsNone(Student.query.get(student_id))

    # Attendance Recording Tests
    def test_take_attendance_page_loads(self):
        response = self.client.get(url_for('take_attendance'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Take/Edit Attendance', response.data)

    def test_take_attendance_load_students(self):
        class_obj = self.create_class(name="Attendance Class")
        student = self.create_student(first_name="Att", last_name="Ender", class_obj=class_obj)
        today_str = date.today().strftime('%Y-%m-%d')

        response = self.client.post(url_for('take_attendance'), data=dict(
            class_id=str(class_obj.id),
            date=today_str,
            submit_select='Load Students'
        ), follow_redirects=True) # Follow redirect if any, but expecting 200

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Attendance for Attendance Class on ' + today_str.encode(), response.data)
        self.assertIn(b'Att Ender', response.data) # Student name should be in the loaded list

    def test_submit_attendance_data(self):
        class_obj = self.create_class(name="Submit Att Class")
        student = self.create_student(first_name="Submit", last_name="Ter", class_obj=class_obj)
        today = date.today()
        today_str = today.strftime('%Y-%m-%d')

        # First, load students to simulate user flow (though not strictly necessary if session is managed by test client)
        self.client.post(url_for('take_attendance'), data=dict(
            class_id=str(class_obj.id),
            date=today_str,
            submit_select='Load Students'
        ))

        # Now submit the attendance data
        response_submit = self.client.post(url_for('take_attendance'), data=dict(
            hidden_class_id=str(class_obj.id),
            hidden_date=today_str,
            student_ids=[str(student.id)], # Ensure this matches how getlist expects it
            present_{student.id}='true', # Checkbox value
            submit_attendance='Submit Attendance'
        ), follow_redirects=True)

        self.assertEqual(response_submit.status_code, 200) # Redirects to take_attendance (GET)
        self.assertIn(f"Attendance for {class_obj.name} on {today_str} recorded successfully!".encode(), response_submit.data)

        att_record = Attendance.query.filter_by(student_id=student.id, class_id=class_obj.id, date=today).first()
        self.assertIsNotNone(att_record)
        self.assertTrue(att_record.is_present)

    # Attendance Viewing Tests
    def test_view_attendance_page_loads(self):
        response = self.client.get(url_for('view_attendance'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'View Attendance Records', response.data)

    def test_view_attendance_with_filters(self):
        class_obj = self.create_class(name="View Att Class")
        student = self.create_student(first_name="Viewer", last_name="Test", class_obj=class_obj)
        att_date = date.today() - timedelta(days=1) # Use a distinct date
        self.create_attendance_record(student, class_obj, att_date, is_present=False)

        response = self.client.post(url_for('view_attendance'), data=dict(
            class_id=str(class_obj.id),
            date=att_date.strftime('%Y-%m-%d'),
            submit_view='View Attendance'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Attendance Records', response.data)
        self.assertIn(b'Viewer Test', response.data) # Student name
        self.assertIn(b'View Att Class', response.data) # Class name
        self.assertIn(att_date.strftime('%Y-%m-%d').encode(), response.data) # Date
        self.assertIn(b'Absent', response.data) # Status

    def test_view_attendance_no_results(self):
        # Use a date far in the future or a non-existent class ID for QuerySelectField
        future_date = (date.today() + timedelta(days=365)).strftime('%Y-%m-%d')

        response = self.client.post(url_for('view_attendance'), data=dict(
            class_id="", # All classes
            date=future_date,
            submit_view='View Attendance'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No attendance records found for the selected criteria.', response.data)
