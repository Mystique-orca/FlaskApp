
from flask import Flask, render_template, request, url_for, redirect
from module import create_post, get_posts
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#this will initialize the app
app = Flask(__name__)
#database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class Posts(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(20), nullable = False)
	content = db.Column(db.String(200), nullable = False)
	date_created = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return '<Posts %r>' %self.id



#endpoint specification
@app.route('/', methods=['GET','POST'])
def index():
	
	if request.method == 'GET':
		pass

	if request.method == 'POST':
		name = request.form['name']
		post = request.form['post']
		new_post = Posts(name = name, content = post)
	
		try:
			db.session.add(new_post)
			db.session.commit()
			return redirect('/')
		except:
			return 'There seems to be an issue!'

	else:
		posts = Posts.query.order_by(Posts.date_created).all()
		return render_template('index.html', posts=posts)


#endpoint specification
@app.route('/delete/<int:id>', methods=['GET','POST'])
def delete(id):
	post_to_delete = Posts.query.get_or_404(id)
	
	try:
		db.session.delete(post_to_delete)
		db.session.commit()
		return redirect('/')
	except:
		return 'Can\'t delete the Post'

#endpoint specification
@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
	post_to_update = Posts.query.get_or_404(id)
	
	if request.method == 'POST':
		post_to_update.content = request.form['content']
		try:
			db.session.commit()
			return redirect('/')
		except:
			return 'Failed to Update'	
	else:
		return render_template('update.html', post=post_to_update)

if __name__ == '__main__':
	app.run(debug=True)
