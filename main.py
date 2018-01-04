import os
import json
from functools import wraps

from flask import Flask, render_template, session, flash, redirect, url_for, request
from flask_socketio import SocketIO, send, emit, disconnect

from forms import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SCRF_ENABLED'] = True
socketio = SocketIO(app)

users = []


def login_required(test):
    global users
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            return redirect(url_for('login'))

    return wrap


@socketio.on("message")
def handleMessage(msg):
    print("Message: " + msg)
    send(msg, broadcast=True)


@socketio.on('type_status')
def handle_type_status(user):
    print(user)
    emit('user', {'data': user['data']}, broadcast=True)


@socketio.on('logout_status')
def handle_logout_status(logout_status):
    disconnect()
    # print(session['user'], 'Disconnected')
    emit('logout_status', {'data': logout_status['data']}, broadcast=True)


@socketio.on('disconnect')
def disconnect_socket():
    print(session['user'], 'Disconnected')
    logout()


@app.route('/')
@login_required
def index():
    global users
    if session['user'] not in users:
        users.append(session['user'])
    return render_template('index.html', all_users=users)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    error = None
    global users

    if request.method == 'POST':
        if form.validate_on_submit():
            if request.form['name'] not in users:
                session['user'] = request.form['name']
                session['logged_in'] = True
                users.append(session['user'])
                print(users)
                return redirect(url_for('index'))
            else:
                flash('{} is in use. Please select an other one'.format(request.form['name']))
                return redirect(url_for('login'))

    return render_template('login.html', form=form, error=error)


@app.route('/logout/')
@login_required
def logout():
    global users
    flash('Goodbye ! {}'.format(session['user'].upper()))
    session.pop('logged_in', None)
    try:
        users.remove(session['user'])
        print(session['user'], 'removed')

    except:
        pass
    session.pop('user', None)
    session.clear()
    return redirect(url_for('login'))


@app.errorhandler(500)
def pageNotFound(error):
    return render_template('errors/500.html')


@app.route('/get_all_users', methods=['GET', 'POST'])
def get_users():
    global users
    return json.dumps(users)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 33508))
    print("port: ", port)
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
