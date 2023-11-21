from io import BytesIO

from flask import Flask, render_template, request, redirect, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.app_context().push()

app.config['SECRET_KEY'] = 'SECRET'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book_library.db'

db = SQLAlchemy()
db.init_app(app)




class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(120), nullable=False)
    rating = db.Column(db.Float(120), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    book_data = db.Column(db.LargeBinary, nullable=False)

    def __init__(self, title, description, rating, author, book_data):
        self.title = title
        self.description = description
        self.rating = rating
        self.author = author
        self.book_data = book_data


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.password = password


@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        emailForm = request.form['email']
        passwordForm = request.form['password']

        userIsExist = User.query.filter_by(email=emailForm).first()

        if userIsExist is None:
            newUser = User(emailForm, passwordForm)
            db.session.add(newUser)
            db.session.commit()
            session['user'] = newUser.email
            return redirect('/')

        else:
            if userIsExist.password == passwordForm:
                session['user'] = userIsExist.email
                return redirect('/')
            else:
                flash("Password is incorrect")

    return render_template('signup.html')


@app.route('/')
def main():
    books = Book.query.all()

    return render_template('index.html', books=books)


@app.route('/upload_book', methods=['GET', 'POST'])
def upload_book():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        author = request.form['author']
        if 'book' in request.files:
            book_file = request.files['book']
            if book_file.filename:
                book_data = book_file.read()
                rating = 5.0
                book = Book(title, description, rating, author, book_data)
                db.session.add(book)
                db.session.commit()
                return redirect('/')

    return render_template('add_book.html')


@app.route('/download/<int:upload_title>')
def download(upload_title):
    upload = Book.query.filter_by(title=upload_title).first()
    if upload is not None:
        return send_file(BytesIO(upload.book_data), as_attachment=True, download_name=upload.title)


@app.route('/logout')
def logout():
    session['user'] = None
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)

with app.app_context():
    db.create_all()
