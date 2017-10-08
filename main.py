import os

from flask import Flask, render_template
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app)


@socketio.on("message")
def handleMessage(msg):
    print("Message: " + msg)
    send(msg, broadcast=True)


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

if __name__ == '__main__':
    socketio.run(app, debug=True)
