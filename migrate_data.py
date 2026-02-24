"""SQLite → PostgreSQL データ移行スクリプト."""

import os
import sqlite3
from sqlalchemy import create_engine, text

# --- 設定 ---
SQLITE_PATH = os.path.join(os.path.dirname(__file__), "syuukatsu.db")
PG_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_aK8johTJOuU1@ep-blue-field-a1a7soyx-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require",
)

# テーブルの移行順序（外部キー依存を考慮）
TABLES = [
    "users",
    "companies",
    "job_axes",
    "company_axis_match",
    "selections",
    "interview_notes",
    "entry_sheets",
    "motivations",
    "schedules",
    "self_analyses",
]


def migrate():
    # SQLite 接続
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row

    # PostgreSQL 接続
    pg_engine = create_engine(PG_URL)

    print(f"SQLite: {SQLITE_PATH}")
    print(f"PostgreSQL: {PG_URL[:40]}...")
    print("=" * 50)

    with pg_engine.connect() as pg_conn:
        for table in TABLES:
            try:
                rows = sqlite_conn.execute(f"SELECT * FROM {table}").fetchall()
            except sqlite3.OperationalError:
                print(f"  {table}: テーブルが存在しません（スキップ）")
                continue

            if not rows:
                print(f"  {table}: 0 件（スキップ）")
                continue

            columns = rows[0].keys()

            # 既存データを削除（重複防止）
            pg_conn.execute(text(f"DELETE FROM {table}"))

            # データ挿入
            col_str = ", ".join(columns)
            param_str = ", ".join([f":{c}" for c in columns])
            insert_sql = text(f"INSERT INTO {table} ({col_str}) VALUES ({param_str})")

            for row in rows:
                row_dict = dict(row)
                # SQLite の 0/1 → PostgreSQL の boolean に変換
                for key, val in row_dict.items():
                    if key in ("reminder",) and isinstance(val, int):
                        row_dict[key] = bool(val)
                pg_conn.execute(insert_sql, row_dict)

            print(f"  {table}: {len(rows)} 件を移行しました")

        pg_conn.commit()

    # シーケンス（自動採番）をリセット
    with pg_engine.connect() as pg_conn:
        for table in TABLES:
            try:
                result = pg_conn.execute(
                    text(f"SELECT MAX(id) FROM {table}")
                ).fetchone()
                if result and result[0]:
                    pg_conn.execute(
                        text(
                            f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), {result[0]})"
                        )
                    )
            except Exception:
                pass  # company_axis_match 等 id列がないテーブルはスキップ
        pg_conn.commit()

    sqlite_conn.close()
    print("=" * 50)
    print("移行完了！")


if __name__ == "__main__":
    migrate()
