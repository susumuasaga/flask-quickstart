from flask import Flask
import os

app = Flask(__name__)


@app.route('/')
def hello_world():
    return f'Hello World! I am running on port {port}.'


if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))
    app.run('0.0.0.0', port)
