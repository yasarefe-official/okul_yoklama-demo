from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, HiddenField
from wtforms.fields.html5 import DateField # For better browser date picker support
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Optional
from wtforms_sqlalchemy.fields import QuerySelectField
from .models import User, Class
from datetime import date

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ClassForm(FlaskForm):
    name = StringField('Class Name',
                       validators=[DataRequired(), Length(min=2, max=100)])
    teacher_name = StringField('Teacher Name',
                               validators=[Optional(), Length(max=100)]) # Optional validator allows empty field
    submit = SubmitField('Save Class')

    def validate_name(self, name_field):
        current_name = None
        # self.obj is populated by Flask-WTF when form is created with an object (e.g., form = ClassForm(obj=class_instance))
        if hasattr(self, 'obj') and self.obj:
            current_name = self.obj.name

        if name_field.data == current_name:
            return # Name hasn't changed

        existing_class = Class.query.filter(Class.name == name_field.data).first()
        if existing_class:
            raise ValidationError('A class with this name already exists. Please use a different name.')

# Helper function for QuerySelectField to get all classes
def get_all_classes():
    return Class.query.order_by(Class.name).all()

def get_class_label(class_obj):
    return class_obj.name

class StudentForm(FlaskForm):
    first_name = StringField('First Name',
                             validators=[DataRequired(), Length(min=1, max=100)])
    last_name = StringField('Last Name',
                            validators=[DataRequired(), Length(min=1, max=100)])
    # class_id field will be representing the 'class_assigned' relationship
    # QuerySelectField handles fetching the Class object directly
    class_assigned = QuerySelectField('Assign to Class',
                                query_factory=get_all_classes,
                                get_label=get_class_label,
                                allow_blank=True,
                                blank_text='-- Not Assigned --',
                                validators=[Optional()])
    submit = SubmitField('Save Student')

class AttendanceSelectionForm(FlaskForm):
    class_id = QuerySelectField('Select Class',
                                query_factory=get_all_classes, # Re-use existing helper
                                get_label=get_class_label,     # Re-use existing helper
                                validators=[DataRequired()])
    date = DateField('Select Date',
                     validators=[DataRequired()],
                     default=date.today)
    submit_select = SubmitField('Load Students')

# AttendanceRecordForm is conceptual, no changes needed to it.

class AttendanceViewSelectionForm(FlaskForm):
    class_id = QuerySelectField('Filter by Class (Optional)',
                                query_factory=get_all_classes,
                                get_label=get_class_label,
                                allow_blank=True,
                                blank_text='-- All Classes --',
                                validators=[Optional()])
    date = DateField('Filter by Date (Optional)',
                     validators=[Optional()]) # DateField will be None if not filled
    submit_view = SubmitField('View Attendance')
