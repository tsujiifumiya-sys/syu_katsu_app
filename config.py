import os
import sys


def _get_base_dir():
    """PyInstaller でパッケージされた場合は _MEIPASS を使い，
    通常実行時は __file__ ベースのパスを返す．"""
    if getattr(sys, "frozen", False):
        # exe と同じフォルダ（DB やユーザーデータの保存先）
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.dirname(__file__))


def _get_resource_dir():
    """テンプレートや static ファイルの格納先を返す．
    PyInstaller の --add-data で同梱したリソースは _MEIPASS 内に展開される．"""
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.abspath(os.path.dirname(__file__))


BASE_DIR = _get_base_dir()
RESOURCE_DIR = _get_resource_dir()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'syuukatsu.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True

