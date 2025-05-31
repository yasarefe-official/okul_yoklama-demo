from flask import render_template, url_for, flash, redirect, request, current_app
from flask_login import current_user, login_user, logout_user, login_required
from . import db # Assuming db is accessible from app package context
from .models import User
from .forms import RegistrationForm, LoginForm

# Helper to get the app object, not strictly needed if using current_app or if routes are part of app directly
# from . import create_app # This would be circular if app is not passed around
# app_obj = create_app() # This creates a new app instance, not good.

# Routes will be registered on the app instance created in __init__.py
# For db operations, we use the 'db' object imported.
# For app context (like config), we can use current_app.

@login_required
def home():
    return render_template('home.html', title='Home')

def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login Successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password.', 'danger')
    return render_template('login.html', title='Login', form=form)

def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Need to actually register these routes with the app.
# This is typically done in __init__.py using app.route or via Blueprints.
# For now, I will assume these functions will be decorated with @app.route(...)
# in __init__.py or a routes setup function.

# Let's adjust app/__init__.py to register these routes.
# The import `from . import routes` in `__init__.py` makes these functions available.
# We need to call app.add_url_rule or app.route in __init__.py after routes module is imported.

# A better way for now, without blueprints, is to define routes with app.route decorator
# This requires access to 'app' object.
# Let's modify __init__.py to pass 'app' to routes, or use a blueprint.

# Simplest for now: Define routes directly in __init__.py or make app object global (not ideal)
# Or, define a function in routes.py that takes app and registers them.

# Let's assume that in app/__init__.py, after `from . import routes`, we will have:
# app.add_url_rule('/', 'home', routes.home)
# app.add_url_rule('/home', 'home_explicit', routes.home) # alias for home
# app.add_url_rule('/register', 'register', routes.register, methods=['GET', 'POST'])
# app.add_url_rule('/login', 'login', routes.login, methods=['GET', 'POST'])
# app.add_url_rule('/logout', 'logout', routes.logout)

# For the @login_required on home(), it needs the app context, which should be fine.
# The url_for calls also need app context.
# The `login_manager.login_view = 'login'` in `__init__.py` refers to the function name 'login'.
# This should work if `app.add_url_rule('/login', 'login', routes.login)` is used.

# Let's write the routes in a way they can be registered.
# The current structure of routes.py is fine for functions.
# The registration will happen in __init__.py
# I need to make sure the routes are actually registered.
# The current task is to "Modify attendance_system/app/routes.py"
# So, I will write the routes here, and the registration will be implicitly handled by
# the `from . import routes` and then subsequent `app.route` calls or blueprint registration
# in `app/__init__.py`.

# The current `app/routes.py` does not define how these functions become routes.
# I will add the decorators directly here, which means `app` must be importable.
# This leads to circular dependency issues if `app` is in `__init__.py`.
# The standard way is to use Blueprints or to pass `app` to a function that defines routes.

# Given the current structure and to avoid immediate refactoring to Blueprints,
# I will modify `app/__init__.py` to register these routes after importing them.
# This means `routes.py` just defines the view functions.
# The task description implies modifying `routes.py` to "implement their respective routes".
# This usually means adding the @app.route decorator.

# Let's try to define a blueprint here. This is cleaner.
# Create a 'main' blueprint.

from flask import Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/home')
@login_required
def home_bp(): # Renamed to avoid clash if not using blueprint initially
    return render_template('home.html', title='Home')

@main_bp.route('/register', methods=['GET', 'POST'])
def register_bp(): # Renamed
    if current_user.is_authenticated:
        return redirect(url_for('main.home_bp'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('main.login_bp'))
    return render_template('register.html', title='Register', form=form)

@main_bp.route('/login', methods=['GET', 'POST'])
def login_bp(): # Renamed
    if current_user.is_authenticated:
        return redirect(url_for('main.home_bp'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login Successful!', 'success')
            # Ensure next_page is safe
            if next_page and not (next_page.startswith('/') or next_page.startswith(request.host_url)):
                next_page = None
            return redirect(next_page) if next_page else redirect(url_for('main.home_bp'))
        else:
            flash('Login Unsuccessful. Please check username and password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@main_bp.route('/logout')
@login_required
def logout_bp(): # Renamed
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login_bp'))

# The login_manager.login_view in __init__.py needs to be 'main.login_bp' now.
# And current_user will be available in templates if login_manager is set up.
# The layout.html uses url_for('home'), url_for('login') etc. These need to be url_for('main.home_bp'), etc.
# This is a significant change. I should update layout.html as well.
# And __init__.py for login_view and blueprint registration.

# For now, sticking to the subtask, I will create routes.py with the blueprint.
# Then I will update __init__.py and layout.html in subsequent steps if allowed, or make a note.

# The subtask says: "For login_manager.login_view, let's assume for now it will be routes.login ... So, set login_manager.login_view = 'login'."
# This implies NOT using a blueprint initially for that part.
# If I use a blueprint 'main', login_view becomes 'main.login_bp'.

# Let's revert routes.py to not use a blueprint for now, and handle registration in __init__.py
# This will keep changes localized as per the current step's focus.
# The view function names will be 'login', 'register', 'home', 'logout'.

# Final decision for routes.py: Define functions, assume registration in __init__.py
# This means flask_login.login_view = 'login' will map to the 'login' function below.
# The `home` route in `layout.html` `url_for('home')` will map to the `home` function.

# Re-writing app/routes.py without blueprint for now.
# The functions need to be registered with an app object.
# This can be done in __init__.py by e.g. app.route('/home')(routes.home)

# Content of routes.py:
from flask import render_template, url_for, flash, redirect, request # current_app removed for now
from flask_login import current_user, login_user, logout_user, login_required
# Assuming db is imported in __init__ and available in app context for models
from .models import User, db # Explicitly import db for operations
from .forms import RegistrationForm, LoginForm

# These functions will be registered with app.route in __init__.py
# Or, if we modify __init__.py to pass `app` to a setup_routes function here.

def home():
    return render_template('home.html', title='Home')

def register():
    if current_user.is_authenticated:
        return redirect(url_for('home')) # Assumes 'home' is the endpoint name for home route
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('login')) # Assumes 'login' is the endpoint name
    return render_template('register.html', title='Register', form=form)

def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            # Security: Ensure next_page is internal
            if next_page and not (next_page.startswith('/') or (request.host_url and next_page.startswith(request.host_url))):
                flash('Invalid redirect URL.', 'warning')
                next_page = None

            flash('Login Successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password.', 'danger')
    return render_template('login.html', title='Login', form=form)

def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login')) # Redirect to login after logout

# Note: These routes are not yet active. They need to be registered with the Flask app instance.
# This will be done in app/__init__.py by adding app.route decorators or app.add_url_rule.
# For example, in app/__init__.py:
# from . import routes
# app.add_url_rule('/', 'home', routes.home)
# app.add_url_rule('/home', 'home_alt', routes.home) # if needed
# app.route('/register', methods=['GET', 'POST'])(routes.register)
# etc.
# The login_manager.login_view = 'login' in __init__.py will then correctly point to the `login` function's endpoint.
# The url_for('home') in layout.html will point to the 'home' endpoint.

# I also need to add @login_required to home()
# from flask_login import login_required
# @login_required before def home():

# Corrected home function:
# def home():
#     return render_template('home.html', title='Home')
# should be:
# @login_required
# def home():
#     return render_template('home.html', title='Home')
# This was missed in the re-write.

# Final proposed content for routes.py:
from flask import render_template, url_for, flash, redirect, request, abort, session
from flask_login import current_user, login_user, logout_user, login_required
from .models import User, Class, Student, Attendance, db
from .forms import RegistrationForm, LoginForm, ClassForm, StudentForm, AttendanceSelectionForm, AttendanceViewSelectionForm
from sqlalchemy.orm import joinedload
from datetime import datetime, date

@login_required
def home():
    return render_template('home.html', title='Home')

def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page and not (next_page.startswith('/') or (request.host_url and next_page.startswith(request.host_url))):
                flash('Invalid redirect value for next page.', 'warning')
                next_page = None # Clear unsafe next_page
            flash('Login Successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@login_required # It's good practice to require login for logout, though often not strictly necessary if it only clears session
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Class Management Routes
@login_required
def classes_list():
    classes = Class.query.order_by(Class.name).all()
    return render_template('classes.html', title='Manage Classes', classes=classes)

@login_required
def add_class():
    form = ClassForm()
    if form.validate_on_submit():
        new_class = Class(name=form.name.data, teacher_name=form.teacher_name.data)
        db.session.add(new_class)
        db.session.commit()
        flash(f'Class "{new_class.name}" has been added successfully!', 'success')
        return redirect(url_for('classes_list'))
    return render_template('add_edit_class.html', title='Add New Class', form=form)

@login_required
def edit_class(class_id):
    class_to_edit = Class.query.get_or_404(class_id)
    form = ClassForm(obj=class_to_edit) # Pass existing object to pre-fill form

    # Custom logic for validate_name during edit
    original_name = class_to_edit.name
    if form.validate_on_submit():
        # Check if name changed and if new name conflicts
        if form.name.data != original_name:
            existing_class = Class.query.filter(Class.name == form.name.data).first()
            if existing_class:
                form.name.errors.append('A class with this name already exists.') # Manual error
                return render_template('add_edit_class.html', title='Edit Class', form=form, class_id=class_id)

        class_to_edit.name = form.name.data
        class_to_edit.teacher_name = form.teacher_name.data
        db.session.commit()
        flash(f'Class "{class_to_edit.name}" has been updated successfully!', 'success')
        return redirect(url_for('classes_list'))

    # For GET request, populate form with existing data
    form.name.data = class_to_edit.name
    form.teacher_name.data = class_to_edit.teacher_name
    return render_template('add_edit_class.html', title='Edit Class', form=form, class_id=class_id)

@login_required
def delete_class(class_id):
    class_to_delete = Class.query.get_or_404(class_id)
    # Optional: Check for students in the class before deleting
    if class_to_delete.students:
        flash(f'Class "{class_to_delete.name}" cannot be deleted because it has students assigned to it. Please reassign students first.', 'danger')
        return redirect(url_for('classes_list'))

    db.session.delete(class_to_delete)
    db.session.commit()
    flash(f'Class "{class_to_delete.name}" has been deleted successfully!', 'success')
    return redirect(url_for('classes_list'))

# Student Management Routes
@login_required
def students_list():
    # Eager load class information to prevent N+1 queries in template
    students = Student.query.options(joinedload(Student.class_assigned)).order_by(Student.last_name, Student.first_name).all()
    return render_template('students.html', title='Manage Students', students=students)

@login_required
def add_student():
    form = StudentForm()
    # QuerySelectField in StudentForm (class_assigned) handles choices automatically
    if form.validate_on_submit():
        # The form.class_assigned.data will be a Class object or None
        new_student = Student(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            class_assigned=form.class_assigned.data # Directly assign the Class object
        )
        db.session.add(new_student)
        db.session.commit()
        flash(f'Student "{new_student.first_name} {new_student.last_name}" has been added successfully!', 'success')
        return redirect(url_for('students_list'))
    return render_template('add_edit_student.html', title='Add New Student', form=form)

@login_required
def edit_student(student_id):
    student_to_edit = Student.query.get_or_404(student_id)
    form = StudentForm(obj=student_to_edit) # Pass existing student object to pre-fill form

    if form.validate_on_submit():
        student_to_edit.first_name = form.first_name.data
        student_to_edit.last_name = form.last_name.data
        student_to_edit.class_assigned = form.class_assigned.data # Assign Class object or None
        db.session.commit()
        flash(f'Student "{student_to_edit.first_name} {student_to_edit.last_name}" has been updated successfully!', 'success')
        return redirect(url_for('students_list'))

    # For GET request, WTForms populates from obj, but ensure class_assigned is correctly set if needed
    # form.class_assigned.data = student_to_edit.class_assigned # Usually handled by obj=
    return render_template('add_edit_student.html', title='Edit Student', form=form, student_id=student_id)

@login_required
def delete_student(student_id):
    student_to_delete = Student.query.get_or_404(student_id)

    # Attendance records will be cascade deleted due to model definition
    # (cascade="all, delete-orphan" on Student.attendance_records)

    student_name = f"{student_to_delete.first_name} {student_to_delete.last_name}"
    db.session.delete(student_to_delete)
    db.session.commit()
    flash(f'Student "{student_name}" and all associated attendance records have been deleted successfully!', 'success')
    return redirect(url_for('students_list'))

# Attendance Routes
@login_required
def take_attendance():
    selection_form = AttendanceSelectionForm()

    # Data to pass to template
    students_with_attendance = [] # List of (student, {'is_present': bool}) tuples
    class_selection_form_submitted = False
    selected_class_obj = None
    selected_date_obj = None

    if request.method == 'POST':
        # Determine which form was submitted
        if selection_form.submit_select.data and selection_form.validate_on_submit():
            # Class and Date Selection Submitted
            class_selection_form_submitted = True
            selected_class_obj = selection_form.class_id.data
            selected_date_obj = selection_form.date.data

            # Store in session for retrieval if the second form submission has validation errors
            # and needs to re-render with the student list.
            session['attendance_class_id'] = selected_class_obj.id
            session['attendance_date_str'] = selected_date_obj.strftime('%Y-%m-%d')

            students_in_class = Student.query.filter_by(class_id=selected_class_obj.id).order_by(Student.last_name, Student.first_name).all()
            if not students_in_class:
                flash(f"No students found in class '{selected_class_obj.name}'. Please add students to this class.", "warning")

            for student in students_in_class:
                attendance_record = Attendance.query.filter_by(
                    student_id=student.id,
                    class_id=selected_class_obj.id,
                    date=selected_date_obj
                ).first()
                students_with_attendance.append(
                    (student, {'is_present': attendance_record.is_present if attendance_record else True})
                )

        elif 'submit_attendance' in request.form:
            # Attendance Data Submitted
            class_selection_form_submitted = True # Keep showing student list section
            hidden_class_id = request.form.get('hidden_class_id', type=int)
            hidden_date_str = request.form.get('hidden_date')

            if not hidden_class_id or not hidden_date_str:
                flash("Error: Missing class or date information for attendance submission.", "danger")
                return redirect(url_for('take_attendance'))

            selected_class_obj = Class.query.get(hidden_class_id)
            try:
                selected_date_obj = datetime.strptime(hidden_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash("Error: Invalid date format for attendance submission.", "danger")
                return redirect(url_for('take_attendance'))

            processed_student_ids = request.form.getlist('student_ids')
            if not processed_student_ids: # Repopulate if something went wrong
                 students_in_class = Student.query.filter_by(class_id=selected_class_obj.id).order_by(Student.last_name, Student.first_name).all()
                 for student in students_in_class:
                    # This logic might be complex if we need to show errors alongside student list
                    # For now, assume this path is mostly for successful processing or major errors
                    attendance_record = Attendance.query.filter_by(student_id=student.id, class_id=selected_class_obj.id, date=selected_date_obj).first()
                    students_with_attendance.append((student, {'is_present': attendance_record.is_present if attendance_record else True}))
                 flash("No student attendance data received. Please try again.", "warning")

            else:
                for student_id_str in processed_student_ids:
                    student_id = int(student_id_str)
                    is_present = request.form.get(f'present_{student_id}') == 'true'

                    attendance_record = Attendance.query.filter_by(
                        student_id=student_id,
                        class_id=selected_class_obj.id,
                        date=selected_date_obj
                    ).first()

                    if attendance_record:
                        attendance_record.is_present = is_present
                    else:
                        attendance_record = Attendance(
                            student_id=student_id,
                            class_id=selected_class_obj.id,
                            date=selected_date_obj,
                            is_present=is_present
                        )
                        db.session.add(attendance_record)

                db.session.commit()
                flash(f"Attendance for {selected_class_obj.name} on {selected_date_obj.strftime('%Y-%m-%d')} recorded successfully!", "success")
                # Clear session keys after successful submission
                session.pop('attendance_class_id', None)
                session.pop('attendance_date_str', None)
                return redirect(url_for('take_attendance')) # Redirect to clear form, or to a view page

        else: # E.g. validation error on selection_form on initial POST
            # If selection_form had errors, it will re-render with those errors.
            # We need to ensure that if the user was trying to submit attendance data,
            # and that somehow failed before this point (e.g. missing hidden fields),
            # we try to reconstruct the student list if possible.
            if session.get('attendance_class_id') and session.get('attendance_date_str'):
                class_selection_form_submitted = True
                selected_class_obj = Class.query.get(session.get('attendance_class_id'))
                selected_date_obj = datetime.strptime(session.get('attendance_date_str'), '%Y-%m-%d').date()
                students_in_class = Student.query.filter_by(class_id=selected_class_obj.id).order_by(Student.last_name, Student.first_name).all()
                for student in students_in_class:
                    attendance_record = Attendance.query.filter_by(student_id=student.id, class_id=selected_class_obj.id, date=selected_date_obj).first()
                    students_with_attendance.append((student, {'is_present': attendance_record.is_present if attendance_record else True}))


    # GET request or after selection form POST
    return render_template('take_attendance.html',
                           title='Take Attendance',
                           selection_form=selection_form,
                           students_with_attendance=students_with_attendance,
                           selected_class=selected_class_obj,
                           selected_date=selected_date_obj,
                           class_selection_form_submitted=class_selection_form_submitted)

# Attendance Viewing Route
@login_required
def view_attendance():
    form = AttendanceViewSelectionForm()
    attendance_records = []
    selected_class_name = None
    selected_date_str = None

    # To explicitly track if the form was submitted and processed, for template logic
    form_processed_no_results = False

    if form.validate_on_submit(): # This implies a POST request with valid data
        query = Attendance.query.options(
            joinedload(Attendance.student),
            joinedload(Attendance.class_attended) # Corrected from class_assigned to class_attended
        )

        selected_class_obj = form.class_id.data # This is a Class object or None
        filter_date = form.date.data           # This is a date object or None

        if selected_class_obj:
            query = query.filter(Attendance.class_id == selected_class_obj.id)
            selected_class_name = selected_class_obj.name

        if filter_date:
            query = query.filter(Attendance.date == filter_date)
            selected_date_str = filter_date.strftime('%Y-%m-%d')

        # Order by date, then class name, then student name
        query = query.order_by(Attendance.date.desc(), Class.name, Student.last_name, Student.first_name)

        attendance_records = query.all()

        if not attendance_records:
            form_processed_no_results = True # Form was processed, but query returned nothing
            flash('No attendance records found for the selected criteria.', 'info')

    return render_template('view_attendance.html',
                           title='View Attendance Records',
                           form=form,
                           attendance_records=attendance_records,
                           selected_class_name=selected_class_name, # Pass filter criteria for display
                           selected_date_str=selected_date_str,     # Pass filter criteria for display
                           records_found=(not form_processed_no_results if request.method == 'POST' else True) # A bit complex, simplify in template
                           )
