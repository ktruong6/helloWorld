import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_required, LoginManager, login_user, logout_user
from werkzeug.security import check_password_hash

from authorize import role_required
from models import db, Student, Major, User
from datetime import datetime as dt

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'university.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'beyond_course_scope'
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view='login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('student_view_all'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/student/view')
def student_view_all():
    students = Student.query.outerjoin(Major, Student.major_id == Major.major_id) \
        .add_entity(Major) \
        .order_by(Student.last_name, Student.first_name) \
        .all()
    return render_template('student_view_all.html', students=students)


@app.route('/student/view/<int:student_id>')
def student_view(student_id):
    student = Student.query.filter_by(student_id=student_id).first()
    majors = Major.query.order_by(Major.major) \
        .order_by(Major.major) \
        .all()

    if student:
        return render_template('student_entry.html', student=student, majors=majors, action='read')

    else:
        flash(f'Student attempting to be viewed could not be found!', 'error')
        return redirect(url_for('student_view_all'))


@app.route('/student/create', methods=['GET', 'POST'])
def student_create():
    if request.method == 'GET':
        majors = Major.query.order_by(Major.major) \
            .order_by(Major.major) \
            .all()
        return render_template('student_entry.html', majors=majors, action='create')
    elif request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        major_id = request.form['major_id']

        birth_date = request.form['birth_date']
        is_honors = True if 'is_honors' in request.form else False

        email = request.form['email']
        student = Student(first_name=first_name, last_name=last_name, email=email, major_id=major_id,
                          birth_date=dt.strptime(birth_date, '%Y-%m-%d'), is_honors=is_honors)
        db.session.add(student)
        db.session.commit()
        flash(f'{first_name} {last_name} was successfully added!', 'success')
        return redirect(url_for('student_view_all'))

    flash('Invalid action. Please try again.', 'error')
    return redirect(url_for('student_view_all'))


@app.route('/student/update/<int:student_id>', methods=['GET', 'POST'])
def student_edit(student_id):
    if request.method == 'GET':
        student = Student.query.filter_by(student_id=student_id).first()
        majors = Major.query.order_by(Major.major) \
            .order_by(Major.major) \
            .all()

        if student:
            return render_template('student_entry.html', student=student, majors=majors, action='update')

        else:
            flash(f'Student attempting to be edited could not be found!', 'error')

    elif request.method == 'POST':
        student = Student.query.filter_by(student_id=student_id).first()

        if student:
            student.first_name = request.form['first_name']
            student.last_name = request.form['last_name']
            student.email = request.form['email']
            student.major_id = request.form['major_id']
            student.birthdate = dt.strptime(request.form['birth_date'], '%Y-%m-%d')
            student.num_credits_completed = request.form['num_credits_completed']
            student.gpa = request.form['gpa']
            student.is_honors = True if 'is_honors' in request.form else False

            db.session.commit()
            flash(f'{student.first_name} {student.last_name} was successfully updated!', 'success')
        else:
            flash(f'Student attempting to be edited could not be found!', 'error')

        return redirect(url_for('student_view_all'))

    return redirect(url_for('student_view_all'))


@app.route('/student/delete/<int:student_id>')
def student_delete(student_id):
    student = Student.query.filter_by(student_id=student_id).first()

    if student:
        db.session.delete(student)
        db.session.commit()
        flash(f'{student} was successfully deleted!', 'success')
    else:
        flash(f'Delete failed! Student could not be found.', 'error')

    return redirect(url_for('student_view_all'))


@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/training')
@login_required
@role_required(['ADMIN', 'MANAGER'])
def training():
    return render_template('training.html')


if __name__ == '__main__':
    app.run()
