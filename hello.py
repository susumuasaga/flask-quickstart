from flask import Flask
import os

app = Flask(__name__)

port = int(os.getenv("PORT", 8080))


@app.route('/')
def hello_world():
    return 'Hello World! I am running on port ' + str(port)


if __name__ == '__main__':
    app.run('0.0.0.0', port)
