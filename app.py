from flask import Flask, render_template, request, flash, redirect, url_for, session
from data import Articles
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
import RegisterForm, AddArticle, EditArticle
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

# Data Dictionary
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

    # Creating a Cursor
    cur = mysql.connection.cursor()

    # Getting The list of Articles from Database
    result = cur.execute('select * from articles')

    # Fetch Query Results
    articles = cur.fetchall()

    if result > 0:  # In Case, There are Results
        return render_template('articles.html', articles=articles)
    else:  # No Results
        msg = 'No Articles Found'
        return render_template('articles.html', msg=msg)

    # Closing the Cursor
    cur.close()


@app.route('/article/<string:id>')
def articles(id):
    '''
    Shows Each Article
    :param id: id of each Article
    :return: equivalent artcle based on id (article.html)
    '''

    # Creating a Cursor
    cur = mysql.connection.cursor()

    # Querying Database
    cur.execute('select * from articles where id=%s', [id])

    # Fetch Query Result
    article = cur.fetchone()

    return render_template('article.html', article=article)


@app.route('/register', methods=['GET', 'POST'])
def register():
    '''
    Registration of user to Database, there will be
    An insert to theusers Table will be Commited.
    :return: redirects to index(home)
    '''

    # Getting form from Frontend
    form = RegisterForm.Form(request.form)

    # Evaluates the Method & the Validation of the Form
    if request.method == 'POST' and form.validate():
        name = form.name.data  # gets the name from frontend form
        email = form.email.data  # gets the email from frontend form
        username = form.username.data  # gets the username from frontend form
        password = sha256_crypt.encrypt(
            str(form.password.data))  # gets the password from frontend form

        # Create Cursor
        cur = mysql.connection.cursor()

        # Inserts into Database (Registration Process)
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
    '''
    Login Process, Including Database Query
    and Auhtentication of The User
    :return: login.html Template
    '''

    # Evaluates the Method
    if request.method == 'POST':
        username = request.form['username']  # gets the username from request
        password_candidate = request.form['password']  # gets the password from request

        # Create Cursor
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

        cur.execute('insert into articles (title, body, author) values(%s, %s, %s)',
                    (title, body, session['username']))

        mysql.connection.commit()

        cur.close()

        flash('Article Created', 'success')

        return redirect(url_for('dashboard'))
    return render_template('add_article.html', form=form)


@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    cur = mysql.connection.cursor()
    result = cur.execute('select * from articles where id = %s', [id])
    article = cur.fetchone()

    form = EditArticle.ArticleForm(request.form)

    form.title.data = article['title']
    form.body.data = article['body']

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']

        cur = mysql.connection.cursor()

        cur.execute('update articles set title=%s, body=%s where id = %s', (title, body, id))

        mysql.connection.commit()

        cur.close()

        flash('Article Updated', 'success')

        return redirect(url_for('dashboard'))
    return render_template('edit_article.html', form=form)


@app.route('/delete_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def delete_article(id):
    cur = mysql.connection.cursor()

    cur.execute('delete from articles where id = %s', [id])

    mysql.connection.commit()

    cur.close()

    flash('Article Deleted', 'success')

    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.secret_key = 'secretkey'
    app.run(debug=True)
