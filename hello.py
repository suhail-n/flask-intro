import os
import logging
import pymysql
from logging.handlers import RotatingFileHandler


from flask import Flask, request, render_template, url_for, redirect, flash, make_response, session
app = Flask(__name__)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'], request.form['password']):
            flash("successfully logged in")
            session['username'] = request.form.get('username')
            return redirect(url_for('welcome'))
        else:
            flash("Incorrect username and password", "error")
            error = "Incorrect username and password"
            app.logger.warning('Incorrect username and password for user {}'.format(request.form.get('username')))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/hello')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)

def valid_login(username, password):
    #mysql
    MYSQL_DATABASE_HOST = os.getenv('IP', '0.0.0.0')
    MYSQL_DATABASE_USER = 'app_user'
    MYSQL_DATABASE_PASSWORD = 'app_pass'
    MYSQL_DATABASE_DB = 'my_flask_app'
    conn = pymysql.connect(
        host=MYSQL_DATABASE_HOST,
        user=MYSQL_DATABASE_USER,
        passwd=MYSQL_DATABASE_PASSWORD,
        db=MYSQL_DATABASE_DB
        )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE username='{}' and password='{}'".format(username, password))
    data = cursor.fetchone()
    
    return True if data else False

# @app.route('/welcome/<username>')
@app.route('/')
def welcome():
    if 'username' in session:
        return render_template('welcome.html', username=session.get('username'))
    else:
        return redirect(url_for('login'))
    # return render_template('welcome.html', username=username)


if __name__ == '__main__':
    host = os.getenv('IP', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    # for dev only. Will reload the server for cp changes and log debugging
    # will change view internal server errors to a stacktrace
    app.debug = True
    # this will encode any session. Should be a difficult key
    # use os.urandom(24) for a good secret key
    app.secret_key = '\xb9\xe6\x0c\xba_\xf7Ur\x04\x91\x07\xda\xffQwO\xc0y\xb2\x88\xa1\xb1\xe8\x10'
    
    # setup logging
    handler = RotatingFileHandler('error.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    
    app.run(host=host, port=port)
