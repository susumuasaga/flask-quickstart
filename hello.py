import time

from cfenv import AppEnv
from flask import Flask
import os

app = Flask(__name__)


@app.route('/')
def hello_world():
    app_env = AppEnv()
    time.sleep(1)
    return (f'Nome da aplicação: {app_env.name}\n'
            f'Instância: {app_env.index}\n'
            f'Endereço da instância: {os.getenv("CF_INSTANCE_ADDR")}\n')


if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))
    app.run('0.0.0.0', port)
