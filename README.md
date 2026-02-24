# 📋 Syu_katsu — 就活管理アプリ

個人の就職活動を効率的に管理するためのWebアプリケーションです。  
企業情報・選考状況・ES・志望動機・自己分析・スケジュールを一元管理できます。

---

## 🚀 特徴

- **ダッシュボード** — 選考カンバンボード・統計・ES締切ウィジェットで全体像を把握
- **企業管理** — 志望度・業界・マイページ情報をCRUD管理
- **選考トラッキング** — ステータス別タイムラインで選考進捗を可視化
- **カレンダー** — FullCalendar.jsで面接・説明会・締切をスケジュール管理
- **ES管理** — 設問・回答・文字数制限・締切をテーブル管理（リアルタイム文字数カウント）
- **志望動機管理** — 企業別にバージョン管理、用途（ES/面接）・添削メモ対応
- **自己分析** — 自己PR・ガクチカ・長所・短所をカテゴリ別タブ表示＋バージョン管理
- **就活軸管理** — 軸の定義と優先度設定
- **企業×就活軸マトリックス** — 各企業と就活軸の合致度をスコア（1〜5）で評価・比較
- **ポータブル対応** — PyInstallerでexe化、USBで持ち運び可能

---

## 📦 技術スタック

| レイヤー | 技術 |
|---|---|
| バックエンド | Python 3.12 + Flask |
| ORM | Flask-SQLAlchemy |
| データベース | SQLite（ファイルベース） |
| フロントエンド | HTML + CSS + JavaScript（Jinja2テンプレート） |
| カレンダー | FullCalendar.js v6 |
| フォント | Google Fonts（Inter, Noto Sans JP） |
| ポータブル化 | PyInstaller |

---

## 🛠️ セットアップ（開発モード）

### 前提条件
- Python 3.10 以上

### 手順

```bash
# 1. リポジトリをクローンまたはフォルダをコピー
cd syuukatsu_app

# 2. 仮想環境を作成・有効化
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. 依存パッケージをインストール
pip install -r requirements.txt

# 4. アプリを起動
python app.py
```

ブラウザで **http://127.0.0.1:5000** を開いてください。

---

## 💻 ポータブル版（exe）の使い方

`dist/Syu_katsu/` フォルダをUSBやZIPで配布できます。

1. `Syu_katsu.exe` をダブルクリック
2. ブラウザが自動で開きます（http://127.0.0.1:5000）
3. 終了するにはコンソールウィンドウを閉じてください

> ⚠️ Pythonのインストールは不要です。  
> ⚠️ データは `syuukatsu.db` としてexeと同じフォルダに保存されます。

---

## 📁 プロジェクト構成

```
syuukatsu_app/
├── app.py              # Flask メインアプリケーション（Blueprint構成）
├── config.py           # 設定（DB接続、シークレットキー）
├── models.py           # SQLAlchemy データモデル定義
├── requirements.txt    # 依存パッケージ一覧
├── syuukatsu.db        # SQLite データベース（自動生成）
├── static/
│   └── style.css       # ダークテーマ CSS デザインシステム
├── templates/
│   ├── base.html           # ベーステンプレート（サイドバー）
│   ├── dashboard.html      # ダッシュボード
│   ├── companies.html      # 企業一覧
│   ├── company_form.html   # 企業追加・編集フォーム
│   ├── company_detail.html # 企業詳細
│   ├── calendar.html       # カレンダー
│   ├── axes.html           # 就活軸管理
│   ├── axis_matrix.html    # 企業×就活軸マトリックス
│   ├── es_list.html        # ES一覧
│   ├── es_form.html        # ES追加・編集フォーム
│   ├── motivation_list.html    # 志望動機一覧
│   ├── motivation_form.html    # 志望動機追加・編集フォーム
│   ├── self_analysis.html      # 自己分析（タブ表示）
│   └── self_analysis_form.html # 自己分析追加・編集フォーム
└── dist/
    └── Syu_katsu/      # ポータブル版（PyInstaller出力）
        ├── Syu_katsu.exe
        └── _internal/
```

---

## 📖 画面一覧

| 画面 | URL | 説明 |
|---|---|---|
| ダッシュボード | `/` | 統計カード＋カンバン＋直近イベント＋ES締切 |
| 企業一覧 | `/companies` | カード形式で企業を表示 |
| 企業追加 | `/companies/new` | 企業情報の入力フォーム |
| 企業詳細 | `/companies/<id>` | 企業情報＋選考タイムライン |
| カレンダー | `/calendar` | FullCalendar月/週/日表示 |
| 就活軸 | `/axes` | 軸の追加・削除 |
| 軸マトリックス | `/matrix` | 企業×軸のスコアマトリックス |
| ES管理 | `/es` | 全ESのテーブル一覧 |
| ES追加/編集 | `/es/new`, `/es/<id>/edit` | ES設問・回答フォーム |
| 志望動機 | `/motivations` | 企業別グループ表示 |
| 自己分析 | `/self-analysis` | カテゴリ別タブ表示 |

---

## 📊 データモデル

主要なテーブル：

- **users** — ユーザー情報
- **companies** — 企業情報（志望度、マイページURL等）
- **selections** — 選考ステージ・ステータス・振り返り
- **job_axes** — 就活軸（名前・優先度）
- **company_axis_match** — 企業×軸の合致度スコア
- **entry_sheets** — ES設問・回答・文字数制限・締切
- **motivations** — 志望動機（バージョン管理）
- **schedules** — スケジュール（カレンダーイベント）
- **self_analyses** — 自己分析（カテゴリ別バージョン管理）

---

## 🔧 ポータブル版のビルド方法

```bash
# PyInstallerをインストール
pip install pyinstaller

# ビルド実行
pyinstaller --noconfirm --onedir --name Syu_katsu \
  --add-data "templates;templates" \
  --add-data "static;static" \
  --hidden-import=flask \
  --hidden-import=flask_sqlalchemy \
  --collect-submodules flask \
  app.py
```

出力先: `dist/Syu_katsu/`

---

## 📝 ライセンス

個人利用向け。自由にカスタマイズ・再配布してください。
