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


def _get_database_uri():
    """環境変数 DATABASE_URL があれば PostgreSQL，なければ SQLite を使用."""
    uri = os.environ.get("DATABASE_URL")
    if uri:
        # Render/Neon は postgres:// を返すが SQLAlchemy は postgresql:// を要求
        if uri.startswith("postgres://"):
            uri = uri.replace("postgres://", "postgresql://", 1)
        return uri
    return f"sqlite:///{os.path.join(BASE_DIR, 'syuukatsu.db')}"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = _get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True

