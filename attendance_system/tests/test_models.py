from .base import BaseTestCase
from attendance_system.app.models import User, Class, Student, Attendance, db
from datetime import date

class ModelTestCase(BaseTestCase):
    def test_create_user(self):
        """Test creating a User model instance."""
        u = User(username="john_doe")
        u.set_password("secure_password")
        db.session.add(u)
        db.session.commit()

        user_from_db = User.query.filter_by(username="john_doe").first()
        self.assertIsNotNone(user_from_db)
        self.assertEqual(user_from_db.username, "john_doe")
        self.assertTrue(user_from_db.check_password("secure_password"))
        self.assertFalse(user_from_db.check_password("wrong_password"))
        self.assertFalse(user_from_db.is_admin) # Default

    def test_create_class(self):
        """Test creating a Class model instance."""
        c = Class(name="Math 101", teacher_name="Mr. Pythagoras")
        db.session.add(c)
        db.session.commit()

        class_from_db = Class.query.filter_by(name="Math 101").first()
        self.assertIsNotNone(class_from_db)
        self.assertEqual(class_from_db.name, "Math 101")
        self.assertEqual(class_from_db.teacher_name, "Mr. Pythagoras")

    def test_create_student(self):
        """Test creating a Student model instance and relationship with Class."""
        # First, create a class
        c = Class(name="Science A")
        db.session.add(c)
        db.session.commit()

        s = Student(first_name="Alice", last_name="Smith", class_id=c.id)
        # Or using relationship: s.class_assigned = c
        db.session.add(s)
        db.session.commit()

        student_from_db = Student.query.filter_by(first_name="Alice").first()
        self.assertIsNotNone(student_from_db)
        self.assertEqual(student_from_db.last_name, "Smith")
        self.assertIsNotNone(student_from_db.class_assigned)
        self.assertEqual(student_from_db.class_assigned.name, "Science A")
        self.assertEqual(student_from_db.class_id, c.id)
        self.assertIn(student_from_db, c.students)

    def test_create_attendance_record(self):
        """Test creating an Attendance model instance."""
        # Create a class and a student
        c = Class(name="History B")
        db.session.add(c)
        db.session.commit()

        s = Student(first_name="Bob", last_name="Brown", class_assigned=c)
        db.session.add(s)
        db.session.commit()

        today = date.today()
        att = Attendance(student_id=s.id, class_id=c.id, date=today, is_present=True)
        db.session.add(att)
        db.session.commit()

        att_from_db = Attendance.query.filter_by(student_id=s.id, date=today).first()
        self.assertIsNotNone(att_from_db)
        self.assertTrue(att_from_db.is_present)
        self.assertEqual(att_from_db.class_id, c.id)
        self.assertEqual(att_from_db.student.first_name, "Bob")
        self.assertEqual(att_from_db.class_attended.name, "History B")

    def test_student_attendance_cascade_delete(self):
        """Test that deleting a student cascades to their attendance records."""
        c = Class(name="Art C")
        db.session.add(c)
        db.session.commit()
        s = Student(first_name="Charlie", last_name="Davis", class_assigned=c)
        db.session.add(s)
        db.session.commit()
        att = Attendance(student_id=s.id, class_id=c.id, date=date.today(), is_present=False)
        db.session.add(att)
        db.session.commit()

        self.assertEqual(Attendance.query.count(), 1)

        db.session.delete(s)
        db.session.commit()

        self.assertEqual(Student.query.count(), 0)
        self.assertEqual(Attendance.query.count(), 0) # Cascade delete should work

    def test_class_attendance_no_cascade_on_class_delete(self):
        """Test that deleting a class does not automatically delete attendance if not configured.
           Note: Current model for Attendance has class_id, not a direct cascade from Class.
           If Class deletion should delete Attendance, that needs specific model/DB setup.
           For now, we test that records remain if only class is deleted (foreign key might become null or prevent deletion based on DB).
           Current Attendance model: class_id = db.Column(Integer, ForeignKey('class.id'), nullable=False)
           This implies that deleting a Class referenced by Attendance records would typically cause a ForeignKeyConstraint error
           unless the records are handled (e.g. set class_id to NULL if allowed, or delete them).
           Let's test the constraint behavior.
        """
        c = Class(name="Music D")
        db.session.add(c)
        db.session.commit()
        s = Student(first_name="Diana", last_name="Evan", class_assigned=c)
        db.session.add(s)
        db.session.commit()
        att = Attendance(student_id=s.id, class_id=c.id, date=date.today(), is_present=True)
        db.session.add(att)
        db.session.commit()

        self.assertEqual(Attendance.query.count(), 1)

        # Attempt to delete the class
        try:
            db.session.delete(c)
            db.session.commit()
            # If we reach here, the DB allowed it (e.g. if FK constraint was deferred or ON DELETE SET NULL)
            # This would depend on specific SQLite foreign_keys pragma or other DB behavior.
            # For SQLite default, with nullable=False on Attendance.class_id, this commit should fail.
            # However, SQLAlchemy might not raise the error until flush/commit and behavior can vary.
        except Exception as e: # Catching a broad exception as specific IntegrityError might vary
            db.session.rollback() # Rollback failed transaction
            self.assertIsInstance(e, Exception) # Or more specific sqlalchemy.exc.IntegrityError

        # After potential error and rollback, record should still exist
        self.assertEqual(Attendance.query.count(), 1)
        self.assertIsNotNone(Class.query.get(c.id)) # Class should still exist if commit failed

        # To properly delete a class with attendance, attendance records must be handled first.
        # For example, delete attendance records, then the class.
        db.session.delete(att)
        db.session.commit()
        db.session.delete(c)
        db.session.commit()
        self.assertEqual(Class.query.count(), 0)
        self.assertEqual(Attendance.query.count(), 0)
