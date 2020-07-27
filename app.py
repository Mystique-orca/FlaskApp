
from flask import Flask, flash, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user




#this will initialize the app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Mystique'
Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class Posts(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String(20), nullable = False)
	content = db.Column(db.Text, nullable = False)
	date_created = db.Column(db.DateTime, default=datetime.utcnow)
	owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(30), nullable = False)
	email = db.Column(db.String(30), nullable = False)
	password = db.Column(db.String(80), nullable = False)
	date_created = db.Column(db.DateTime, default=datetime.utcnow)
	posts = db.relationship('Posts', backref='owner')

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


class LoginForm(FlaskForm):
	username = StringField('username', validators=[InputRequired(), Length(min=4, max=30)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
	remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
	username = StringField('username', validators=[InputRequired(), Length(min=4, max=30)])
	email = StringField('email', validators=[InputRequired(), Email(message="Invalid Email"), Length(max=30)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
	
#endpoint specification
@app.route('/', methods=['GET','POST'])
def home():
	posts = Posts.query.order_by(Posts.date_created).all()
	users = User.query.with_entities(User.username, User.id)
	return render_template('home.html', posts=posts, users=users)

#endpoint specification
@app.route('/index', methods=['GET','POST'])
@login_required
def index():
	
	if request.method == 'GET':
		pass

	if request.method == 'POST':
		title = request.form['title']
		post = request.form['post']
		new_post = Posts(title = title, content = post, owner=current_user)
	
		try:
			db.session.add(new_post)
			db.session.commit()
			return redirect('/index')
		except:
			return 'There seems to be an issue!'

	else:
		posts = Posts.query.order_by(Posts.date_created).filter_by(owner_id=current_user.id).all()
		return render_template('index.html', posts=posts, name = current_user.username)

#endpoint specification
@app.route('/login', methods=['GET','POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username = form.username.data.lower()).first()
		if user:
			if check_password_hash(user.password, form.password.data):
				login_user(user, remember=form.remember.data)
				return redirect(url_for('index'))
			else:
				flash('Invalid Password')
		else:
			flash('Invalid Username')
	return render_template('login.html', form=form)

#endpoint specification
@app.route('/signup', methods=['GET','POST'])
def signup():
	form = RegisterForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username = form.username.data).first()
		email = User.query.filter_by(email = form.email.data).first()
		if user:
			flash('User already exists')
		if email:
			flash('Email already signed up by other user')
		else:
			hashed_password = generate_password_hash(form.password.data, method='sha256')
			new_user = User(username = form.username.data.lower(), email = form.email.data, password = hashed_password)
			db.session.add(new_user)
			db.session.commit()
		return redirect(url_for('login'))
	return render_template('signup.html', form=form)


#endpoint specification
@app.route('/delete/<int:id>', methods=['GET','POST'])
@login_required
def delete(id):
	post_to_delete = Posts.query.get_or_404(id)
	
	try:
		db.session.delete(post_to_delete)
		db.session.commit()
		return redirect('/index')
	except:
		return 'Can\'t delete the Post'

#endpoint specification
@app.route('/update/<int:id>', methods=['GET','POST'])
@login_required
def update(id):
	post_to_update = Posts.query.get_or_404(id)
	
	if request.method == 'POST':
		post_to_update.content = request.form['content']
		try:
			db.session.commit()
			return redirect('/index')
		except:
			return 'Failed to Update'	
	else:
		return render_template('update.html', post=post_to_update)

#endpoint specification
@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('home'))


if __name__ == '__main__':
	app.run(debug=True)
