from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# This 'db' object will be initialized in app/__init__.py
db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(Integer, primary_key=True)
    username = db.Column(String(80), unique=True, nullable=False)
    password_hash = db.Column(String(256), nullable=False) # Increased length for longer hashes
    is_admin = db.Column(Boolean, default=False, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Class(db.Model):
    __tablename__ = 'class'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), unique=True, nullable=False)
    teacher_name = db.Column(String(100), nullable=True)

    # Relationship to Student model
    students = relationship('Student', backref='class_assigned', lazy=True)

    def __repr__(self):
        return f'<Class {self.name}>'

class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(Integer, primary_key=True)
    first_name = db.Column(String(50), nullable=False)
    last_name = db.Column(String(50), nullable=False)
    class_id = db.Column(Integer, ForeignKey('class.id'), nullable=True)

    # Relationship to Attendance model
    attendance_records = relationship('Attendance', backref='student', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Student {self.first_name} {self.last_name}>'

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(Integer, primary_key=True)
    date = db.Column(Date, nullable=False)
    is_present = db.Column(Boolean, nullable=False, default=True)
    student_id = db.Column(Integer, ForeignKey('student.id'), nullable=False)
    class_id = db.Column(Integer, ForeignKey('class.id'), nullable=False)

    # Add relationship to Class model to easily query attendance by class
    class_attended = relationship('Class', backref='attendance_records', lazy=True)


    def __repr__(self):
        return f'<Attendance {self.student_id} on {self.date}>'
