"""Syu_katsu アプリ説明書 PDF 生成スクリプト."""

import os
import sys

from fpdf import FPDF


class ManualPDF(FPDF):
    """日本語対応PDFクラス."""

    def __init__(self):
        super().__init__()
        # Noto Sans JP フォントを使用（Unicode対応）
        font_url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/Variable/TTF/NotoSansCJKjp-VF.ttf"
        font_dir = os.path.join(os.path.dirname(__file__), "_fonts")
        os.makedirs(font_dir, exist_ok=True)
        font_path = os.path.join(font_dir, "NotoSansCJKjp-VF.ttf")

        if not os.path.exists(font_path):
            print("フォントをダウンロード中...")
            import urllib.request
            urllib.request.urlretrieve(font_url, font_path)
            print("ダウンロード完了")

        self.add_font("NotoSansJP", "", font_path, uni=True)
        self.add_font("NotoSansJP", "B", font_path, uni=True)

    def header(self):
        self.set_font("NotoSansJP", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "Syu_katsu — 就活管理アプリ 説明書", align="R")
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("NotoSansJP", "", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"— {self.page_no()} —", align="C")

    def title_page(self):
        self.add_page()
        self.ln(60)
        self.set_font("NotoSansJP", "B", 32)
        self.set_text_color(99, 102, 241)
        self.cell(0, 16, "Syu_katsu", align="C")
        self.ln(20)
        self.set_font("NotoSansJP", "", 16)
        self.set_text_color(60, 60, 60)
        self.cell(0, 10, "就活管理アプリ 説明書", align="C")
        self.ln(40)
        self.set_font("NotoSansJP", "", 11)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, "バージョン: 1.0 (MVP)", align="C")
        self.ln(8)
        self.cell(0, 8, "最終更新: 2026年2月24日", align="C")

    def section(self, title):
        self.set_font("NotoSansJP", "B", 16)
        self.set_text_color(99, 102, 241)
        self.ln(6)
        self.cell(0, 12, title)
        self.ln(4)
        # 下線
        self.set_draw_color(99, 102, 241)
        self.set_line_width(0.5)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(6)

    def subsection(self, title):
        self.set_font("NotoSansJP", "B", 12)
        self.set_text_color(40, 40, 40)
        self.ln(3)
        self.cell(0, 9, title)
        self.ln(5)

    def body_text(self, text):
        self.set_font("NotoSansJP", "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 7, text)
        self.ln(2)

    def bullet(self, text):
        self.set_font("NotoSansJP", "", 10)
        self.set_text_color(50, 50, 50)
        x = self.get_x()
        self.cell(8, 7, "•")
        self.multi_cell(0, 7, text)
        self.ln(1)

    def table_row(self, cells, header=False):
        if header:
            self.set_font("NotoSansJP", "B", 9)
            self.set_fill_color(240, 240, 245)
        else:
            self.set_font("NotoSansJP", "", 9)
            self.set_fill_color(255, 255, 255)
        self.set_text_color(50, 50, 50)
        col_w = (self.w - self.l_margin - self.r_margin) / len(cells)
        for cell in cells:
            self.cell(col_w, 8, str(cell), border=1, fill=header, align="C" if header else "L")
        self.ln()

    def code_block(self, text):
        self.set_font("NotoSansJP", "", 9)
        self.set_fill_color(245, 245, 250)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 6, text, fill=True)
        self.ln(3)


def main():
    pdf = ManualPDF()
    pdf.set_auto_page_break(auto=True, margin=20)

    # --- 表紙 ---
    pdf.title_page()

    # --- 概要 ---
    pdf.add_page()
    pdf.section("1. アプリ概要")
    pdf.body_text(
        "Syu_katsu は、個人の就職活動を効率的に管理するためのWebアプリケーションです。\n"
        "企業情報・選考状況・ES・志望動機・自己分析・スケジュールを一元管理できます。\n"
        "Python + Flask で構築されており、ローカルPC上で動作します。\n"
        "PyInstallerによるexe化に対応しており、USBで持ち運び・他人への配布も可能です。"
    )

    pdf.subsection("主な特徴")
    features = [
        "ダッシュボード — カンバンボード・統計・ES締切ウィジェットで全体像を把握",
        "企業管理 — 志望度・業界・マイページ情報を登録・管理",
        "選考トラッキング — ステータス別タイムラインで進捗を可視化",
        "カレンダー — FullCalendar.jsによる月/週/日表示",
        "ES管理 — 設問・回答・文字数制限・締切をテーブル管理",
        "志望動機管理 — 企業別バージョン管理、添削メモ対応",
        "自己分析 — 自己PR・ガクチカ・長所・短所をタブ表示",
        "就活軸管理 — 軸の定義と企業との合致度マトリックス",
        "ポータブル対応 — exeファイルとして配布可能",
    ]
    for f in features:
        pdf.bullet(f)

    # --- 技術スタック ---
    pdf.section("2. 技術スタック")
    pdf.table_row(["レイヤー", "技術"], header=True)
    pdf.table_row(["バックエンド", "Python 3.12 + Flask"])
    pdf.table_row(["ORM", "Flask-SQLAlchemy"])
    pdf.table_row(["データベース", "SQLite（ファイルベース）"])
    pdf.table_row(["フロントエンド", "HTML + CSS + JS（Jinja2）"])
    pdf.table_row(["カレンダー", "FullCalendar.js v6"])
    pdf.table_row(["フォント", "Google Fonts（Inter, Noto Sans JP）"])
    pdf.table_row(["ポータブル化", "PyInstaller"])

    # --- セットアップ ---
    pdf.add_page()
    pdf.section("3. セットアップ（開発モード）")
    pdf.subsection("前提条件")
    pdf.bullet("Python 3.10 以上がインストールされていること")
    pdf.ln(3)
    pdf.subsection("手順")
    pdf.body_text("1. プロジェクトフォルダに移動")
    pdf.code_block("cd syuukatsu_app")
    pdf.body_text("2. 仮想環境を作成・有効化")
    pdf.code_block("python -m venv venv\n.\\venv\\Scripts\\activate   # Windows\nsource venv/bin/activate  # Mac/Linux")
    pdf.body_text("3. 依存パッケージをインストール")
    pdf.code_block("pip install -r requirements.txt")
    pdf.body_text("4. アプリを起動")
    pdf.code_block("python app.py")
    pdf.body_text("5. ブラウザで http://127.0.0.1:5000 を開く")

    # --- ポータブル版 ---
    pdf.section("4. ポータブル版（exe）の使い方")
    pdf.body_text(
        "dist/Syu_katsu/ フォルダをUSBやZIPで配布できます。\n"
        "相手のPCにPythonがインストールされていなくても動作します。"
    )
    pdf.subsection("起動方法")
    pdf.bullet("Syu_katsu.exe をダブルクリック")
    pdf.bullet("ブラウザが自動で開きます（http://127.0.0.1:5000）")
    pdf.bullet("終了するにはコンソールウィンドウを閉じてください")
    pdf.ln(3)
    pdf.subsection("注意事項")
    pdf.bullet("データは syuukatsu.db としてexeと同じフォルダに保存されます")
    pdf.bullet("ウイルス対策ソフトが誤検知する場合は例外に追加してください")

    # --- 画面説明 ---
    pdf.add_page()
    pdf.section("5. 画面一覧と操作方法")

    screens = [
        ("ダッシュボード（/）",
         "アプリのトップページ。統計カード（登録企業数・選考中・内定・内定率）、"
         "カンバンボード（未応募/選考中/内定/不合格/辞退）、直近のイベント、"
         "ES締切ウィジェット（未提出ESの締切日と残日数）を表示します。"),
        ("企業管理（/companies）",
         "登録済み企業をカード形式で一覧表示。「+企業を追加」ボタンから新規登録。"
         "各カードをクリックすると企業詳細ページ（選考タイムライン付き）に遷移します。"),
        ("カレンダー（/calendar）",
         "FullCalendar.jsによる月/週/日表示。クリックでイベント追加、"
         "既存イベントクリックで編集・削除。種別ごとに色分け表示されます。"),
        ("就活軸（/axes）",
         "軸の名前・説明・優先度を登録。優先度順に表示されます。"),
        ("軸マトリックス（/matrix）",
         "企業×就活軸のテーブル。各セルのドット(●)をクリックして1〜5のスコアを設定。"
         "同じドットを再クリックでリセット。スコアはAJAXで即時保存されます。"
         "行末に合計スコアが表示され、企業間の比較に活用できます。"),
        ("ES管理（/es）",
         "全企業のESをテーブル形式で一覧表示。設問・ステータス・文字数・締切を確認。"
         "フォームではリアルタイム文字数カウントが動作し、制限超過時は赤色で警告します。"),
        ("志望動機（/motivations）",
         "企業別にグループ化して表示。同じ企業に複数の志望動機を追加すると"
         "バージョンが自動採番（v1→v2→…）されます。用途（ES/面接/OB訪問）と"
         "添削メモを記録できます。"),
        ("自己分析（/self-analysis）",
         "自己PR・ガクチカ・長所・短所の4カテゴリをタブ切替で表示。"
         "同じカテゴリに複数追加するとバージョンが自動採番されます。"),
    ]

    for screen_name, desc in screens:
        pdf.subsection(screen_name)
        pdf.body_text(desc)

    # --- データモデル ---
    pdf.add_page()
    pdf.section("6. データモデル")
    pdf.body_text("主要テーブルの一覧：")
    tables = [
        ("users", "ユーザー情報（氏名・メール・大学・研究テーマ）"),
        ("companies", "企業情報（志望度・業界・マイページURL等）"),
        ("selections", "選考ステージ・ステータス・振り返り"),
        ("job_axes", "就活軸（名前・説明・優先度）"),
        ("company_axis_match", "企業×軸の合致度スコア（1〜5）"),
        ("entry_sheets", "ES設問・回答・文字数制限・締切・ステータス"),
        ("motivations", "志望動機（バージョン管理・用途・添削メモ）"),
        ("schedules", "スケジュール（カレンダーイベント）"),
        ("self_analyses", "自己分析（カテゴリ別バージョン管理）"),
    ]
    pdf.table_row(["テーブル名", "説明"], header=True)
    for name, desc in tables:
        pdf.table_row([name, desc])

    # --- ビルド方法 ---
    pdf.ln(5)
    pdf.section("7. ポータブル版のビルド方法")
    pdf.code_block(
        "pip install pyinstaller\n\n"
        'pyinstaller --noconfirm --onedir --name Syu_katsu \\\n'
        '  --add-data "templates;templates" \\\n'
        '  --add-data "static;static" \\\n'
        '  --hidden-import=flask \\\n'
        '  --hidden-import=flask_sqlalchemy \\\n'
        '  --collect-submodules flask \\\n'
        '  app.py'
    )
    pdf.body_text("出力先: dist/Syu_katsu/")

    # --- 出力 ---
    output_path = os.path.join(os.path.dirname(__file__), "Syu_katsu_説明書.pdf")
    pdf.output(output_path)
    print(f"PDF生成完了: {output_path}")


if __name__ == "__main__":
    main()
