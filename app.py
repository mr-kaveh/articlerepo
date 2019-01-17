from flask import Flask, render_template, request, flash, redirect, url_for, session, logging
from data import Articles
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
import RegisterForm
import AddArticle
from functools import wraps

app = Flask(__name__)

# mysql Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init mysql
mysql = MySQL(app)

data = Articles()


@app.route('/')
def index():
    '''
    Brings up the Home Page
    :return: home.html Template
    '''
    return render_template('home.html')


@app.route('/about')
def about():
    '''
    Brings up the About Page
    :return: about.html Template
    '''
    return render_template('about.html')


@app.route('/articles')
def article():
    '''
    Brings up the List of Articles
    :return: articles.html Template
    '''
    cur = mysql.connection.cursor()

    result = cur.execute('select * from articles')
    articles = cur.fetchall()
    if result > 0:
        return render_template('articles.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('articles.html', msg=msg)

    cur.close()


@app.route('/article/<string:id>')
def articles(id):
    '''
    Shows Each Article
    :param id: id of each Article
    :return: equivalent artcle based on id (article.html)
    '''
    cur = mysql.connection.cursor()
    result = cur.execute('select * from articles where id=%s',[id])
    article = cur.fetchone()

    return render_template('article.html', article=article )


@app.route('/register', methods=['GET', 'POST'])
def register():
    '''
    Registration of user to Database, there will be
    An insert to theusers Table will be Commited.
    :return: redirection to index
    '''
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        cur = mysql.connection.cursor()

        result = cur.execute('select * from users where username = %s', [username])

        if result > 0:
            data = cur.fetchone()
            password = data['password']

            if sha256_crypt.verify(password_candidate, password):
                # passed
                session['logged_in'] = True
                session['username'] = username

                flash('You Are Now Logged In', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid Login'
                return render_template('login.html', error=error)
            # Connection Close
            cur.close()
        else:
            error = 'Username Not Found'
            return render_template('login.html', error=error)
    return render_template('login.html')


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please Login', 'danger')
            return redirect(url_for('login'))

    return wrap


@app.route('/logout')
def logout():
    session.clear()
    flash('You Are Now Logged Out', 'success')
    return redirect(url_for('login'))


@app.route('/dashboard')
@is_logged_in
def dashboard():
    cur = mysql.connection.cursor()

    result = cur.execute('select * from articles')
    articles = cur.fetchall()
    if result > 0:
        return render_template('dashboard.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('dashboards.html', msg=msg)

    cur.close()


@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = AddArticle.ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        cur = mysql.connection.cursor()

        cur.execute('insert into articles (title, body, author) values(%s, %s, %s)', (title, body, session['username']))

        mysql.connection.commit()

        cur.close()

        flash('Article Created', 'success')

        return redirect(url_for('dashboard'))
    return render_template('add_article.html', form=form)

if __name__ == '__main__':
    app.secret_key = 'secretkey'
    app.run(debug=True)
