from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from flask_login import UserMixin, login_required, current_user, logout_user, login_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bazadate.db'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')


# db.create_all()


@app.route('/', methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated:
        if request.method == 'POST':
            note = request.form.get('note')
            if len(note) < 1:
                flash('Note is too short!', category='error')
            else:
                new_note = Note(data=note, user_id=current_user.id)
                db.session.add(new_note)
                db.session.commit()
                flash('Note added', category='success')
        return render_template("home.html", user=current_user)
    else:
        return render_template("home.html", user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("Login.html", user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greather than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greather than 1 characters.', category='error')
        elif password1 != password2:
            flash('Password don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name,
                            password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('home'))

    return render_template('sign_up.html', user=current_user)


@app.route("/delete")
def delete_note():
    note_id = request.args.get("item_to_delete")
    note_to_delete = Note.query.get(note_id)
    db.session.delete(note_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit_note(id):
    note_to_edit = Note.query.get(id)
    if request.method == 'POST':
        note = request.form.get('note')
        note_to_edit.data = note
        db.session.commit()
        flash('Note edited succesfully!')
        return redirect(url_for('home'))

    return render_template('edit.html', note=note_to_edit, user=current_user)


if __name__ == '__main__':
    app.run(debug=True)
