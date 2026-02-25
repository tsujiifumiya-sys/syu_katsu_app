# 📋 Syu_katsu — 就活管理アプリ

個人の就職活動を効率的に管理するためのWebアプリケーションです。  
企業情報・選考状況・ES・志望動機・自己分析・スケジュールを一元管理できます。

---

## 🚀 特徴

- **ダッシュボード** — カレンダー連携の直近イベント、ES締切ウィジェット、企業を選考段階別（エントリー・書類選考・適性検査・選考中）にグループ表示して全体像を把握
- **企業管理** — 志望度・業界・マイページ情報をCRUD管理
- **選考トラッキング** — 各選考の段階（エントリー開始待ち〜最終面接）・ステータス（予定〜内定）・詳細（日時・場所）をカード形式で柔軟に記録・更新
- **カレンダー** — FullCalendar.jsで面接・説明会・ES締切をスケジュール管理（日付選択で簡単入力、種別ごとに色分け表示）
- **ES管理** — 設問・回答・文字数制限をテーブル管理（リアルタイム文字数カウント対応）
- **就活軸管理** — 軸の定義と優先度設定（インライン編集対応）
- **クラウドデプロイ対応** — Render等のPaaSでのホスティング、PostgreSQL接続対応
- **セキュリティ** — 本番環境向けにBasic認証を標準搭載

---

## 📦 技術スタック

| レイヤー | 技術 |
|---|---|
| バックエンド | Python 3.12 + Flask |
| ORM | Flask-SQLAlchemy |
| データベース | PostgreSQL（本番 / 例: Neon） または SQLite（開発用） |
| フロントエンド | HTML + CSS + JavaScript（Jinja2テンプレート） |
| カレンダー | FullCalendar.js v6 |
| フォント | Google Fonts（Inter, Noto Sans JP） |
| デプロイ | Render / Gunicorn (+ Basic Authentication) |

---

## 🛠️ セットアップ（ローカル開発モード）

### 前提条件
- Python 3.10 以上

### 手順

```bash
# 1. リポジトリをクローンまたはフォルダをコピー
cd syu_katsu_app

# 2. 仮想環境を作成・有効化
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. 依存パッケージをインストール
pip install -r requirements.txt

# 4. アプリを起動 (デフォルトはローカルのSQLiteを使用)
python app.py
```

ブラウザで **http://127.0.0.1:5000** を開いてください。

---

## ☁️ デプロイ (Render を想定した本番環境)

このアプリはRenderでのホスティングに最適化されています（`render.yaml` 付属）。

### 必要な環境変数

Renderデプロイ時に以下の環境変数を設定してください。

- `DATABASE_URL`: PostgreSQLの接続URL（例: Neonなどから取得）
- `SECRET_KEY`: セッション用のランダムな文字列
- `BASIC_AUTH_USERNAME`: Basic認証用のユーザー名
- `BASIC_AUTH_PASSWORD`: Basic認証用のパスワード

※ 環境変数を設定すると自動的にBasic認証が有効になります。ローカル開発時は未設定で構いません。

---

## 📁 プロジェクト構成

```
syu_katsu_app/
├── app.py              # Flask メインアプリケーション
├── config.py           # 設定（DB接続、シークレットキー、Basic認証）
├── models.py           # SQLAlchemy データモデル定義
├── requirements.txt    # 依存パッケージ一覧
├── render.yaml         # Render デプロイ用の設定ファイル
├── migrate_data.py     # SQLite から PostgreSQL へのデータ移行スクリプト
├── static/
│   └── style.css       # ダークテーマ CSS デザインシステム
└── templates/
    ├── base.html           # ベーステンプレート（サイドバー）
    ├── dashboard.html      # ダッシュボード
    ├── companies.html      # 企業一覧
    ├── company_form.html   # 企業追加・編集フォーム
    ├── company_detail.html # 企業詳細（選考カード管理）
    ├── calendar.html       # カレンダー管理
    ├── axes.html           # 就活軸管理
    ├── es_list.html        # ES一覧
    └── es_form.html        # ES追加・編集フォーム
```

---

## 📖 画面一覧

| 画面 | URL | 説明 |
|---|---|---|
| ダッシュボード | `/` | 企業グループ一覧＋直近イベント＋ES締切 |
| 企業一覧 | `/companies` | カード形式で企業を表示 |
| 企業追加 | `/companies/new` | 企業情報の入力フォーム |
| 企業詳細 | `/companies/<id>` | 企業情報＋選考状況（カード形式で編集可能） |
| カレンダー | `/calendar` | FullCalendar月/週/日表示（日付クリックで作成） |
| 就活軸 | `/axes` | 軸の追加・インライン編集・削除 |
| ES管理 | `/es` | 全ESのテーブル一覧 |
| ES追加/編集 | `/es/new`, `/es/<id>/edit` | ES設問・回答フォーム（文字数カウント対応） |

---

## 📊 データモデル

主要なテーブル：

- **users** — ユーザー情報
- **companies** — 企業情報（志望度、マイページURL等）
- **selections** — 選考（ステージ・ステータス・日時・場所）
- **job_axes** — 就活軸（名前・優先度）
- **entry_sheets** — ES設問・回答・文字数制限
- **schedules** — スケジュール（カレンダー連携）

---

## 📝 ライセンス

個人利用向け。自由にカスタマイズ・再配布してください。
