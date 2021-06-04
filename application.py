# from flask import Flask,render_template,request

# app = Flask(__name__)

# @app.route("/", methods=["GET", "POST"])
# def main_page():
#     if request.method == 'GET':
#         text = "ここに結果が出力されます"
#         return render_template("page.html",text=text)
#     elif request.method == 'POST':
#         name = request.form["name"]
#         text = "こんにちは" + name + "さん"
#         return render_template("page.html",text=text)

# ## 実行
# if __name__ == "__main__":
#     app.run(debug=True)

import os
import sys
import socket
from logging import getLogger, StreamHandler, Formatter, FileHandler

import psutil
from flask import Flask, Blueprint
from waitress import serve
from pathlib import Path

from application.models import resource_path
from application.views import app_view

# プロセス優先度をLowに設定
p = psutil.Process()
p.nice(psutil.IDLE_PRIORITY_CLASS)

# globalに反映されるloggerを取得、設定
logger = getLogger()

# ログレベルの設定
logger.setLevel('INFO')

# waitressのログを非表示
logger.disabled = True

# ログのフォーマット
fmt, dtfmt = '%(asctime)s, %(levelname)s, %(message)s', '%Y-%m-%d %H:%M:%S'

# ログのコンソール出力の設定
console = StreamHandler()
console.setFormatter(Formatter(fmt=fmt, datefmt=dtfmt))
logger.addHandler(console)

# ログのファイル出力先を設定
os.makedirs('log/', exist_ok=True)
file = FileHandler('log/Zuerst.log')
file.setFormatter(Formatter(fmt=fmt, datefmt=dtfmt))
logger.addHandler(file)

# TODO: 戻す！
# サーバ諸元を設定
PORT = 443
# PORT = 444
THREADS = 10

# ホストPCのIPを取得
HOST_IP = socket.gethostbyname(socket.gethostname())

# EXEの場合 (属性がfrozenの場合)
if getattr(sys, 'frozen', False):

    # パスを定義
    path = {
        'template': str(resource_path('templates')),
        'static': str(resource_path('static')),
        'users': str(Path(sys.executable).parent / Path('users')),
        'graphviz': str(resource_path('graphviz/bin')),
    }

# EXEでは無い場合
else:
    # パスを定義
    path = {
        'template': 'templates',
        'static': 'static',
        'users': './users',
        'graphviz': str(
            Path('C:\\Users', os.getlogin(), 'Miniconda3', 'pkgs',
                 'graphviz-2.38-hfd603c8_2', 'Library', 'bin', 'graphviz'))
    }

    # Graphvizが無い場合、プログラム終了
    assert os.path.exists(path['graphviz']), 'No graphviz packages'

# Flaskインスタンスの作成
app = Flask(__name__,
            template_folder=path['template'], static_folder=path['static'])

# USERSフォルダをappに追加
app.register_blueprint(
    Blueprint('users', __name__,
              static_url_path='/users', static_folder=path['users']))

# Graphvizのパスを環境変数に追加
os.environ['PATH'] += os.pathsep + path['graphviz']

# application.pyをappに追加
app.register_blueprint(app_view)

# 秘密鍵を設定
app.config['SECRET_KEY'] = os.urandom(24)


if __name__ == '__main__':

    # デバッグモードの場合
    if sys.gettrace():

        # ローカルPCで動作
        print('\nZuerst works as the stand-alone mode.')
        serve(app, host='127.0.0.1', port=PORT, threads=THREADS)

    # それ以外の場合
    else:
        # 動作モードの確認
        print('Do you want to run Zuerst as a server? -> [y]/n')
        server_mode = input().lower()

        # サーバ動作させる場合
        if server_mode == ('y' or 'yes'):

            # サーバモードで動作
            print('\nZuerst works as the server.')
            serve(app, host=HOST_IP, port=PORT, threads=THREADS)

        # スタンドアロン動作させる場合
        else:

            # ローカルPCで動作
            print('\nZuerst works as the stand-alone mode.')
            serve(app, host='127.0.0.1', port=PORT, threads=THREADS)
