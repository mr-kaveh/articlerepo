from flask import Flask, render_template, request, flash, redirect, url_for, session, logging
from data import Articles
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
import RegisterForm

app = Flask(__name__)


#mysql Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
#init mysql
mysql = MySQL(app)

data = Articles()


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/articles')
def article():
    return render_template('articles.html', articles=data)


@app.route('/article/<string:id>')
def articles(id):
    return render_template('article.html', id=id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm.Form(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        # Create Cursor
        cur = mysql.connection.cursor()
        cur.execute('insert into users(name, email, username, password)' \
                    'values(%s, %s, %s, %s)', (name, email, username, password))
        # Commits To Database
        mysql.connection.commit()
        # Closes Connection
        cur.close()
        flash('You Are Now Registered', 'Success')
        return redirect(url_for('index'))

    return render_template('register.html', form=form)


if __name__ == '__main__':
    app.secret_key = 'secret-$@DFDF##@$#@'
    app.run(debug=True)
