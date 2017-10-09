import os

from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app)


@socketio.on("message")
def handleMessage(msg):
    print("Message: " + msg)
    send(msg, broadcast=True)


@socketio.on('type_status')
def handle_type_status(user):
    print(user)
    emit('user', {'data': user['data']}, broadcast=True)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 33508))
    print("port: ", port)
    socketio.run(app, host='0.0.0.0', port=port)
