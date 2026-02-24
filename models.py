"""就活管理アプリ — データベースモデル定義."""

from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# ---------------------------------------------------------------------------
# ユーザー
# ---------------------------------------------------------------------------
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, default="ユーザー")
    email = db.Column(db.String(200), unique=True, nullable=True)
    university = db.Column(db.String(200), nullable=True)
    research_theme = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # リレーション
    companies = db.relationship("Company", backref="user", lazy=True, cascade="all, delete-orphan")
    job_axes = db.relationship("JobAxis", backref="user", lazy=True, cascade="all, delete-orphan")
    schedules = db.relationship("Schedule", backref="user", lazy=True, cascade="all, delete-orphan")
    self_analyses = db.relationship("SelfAnalysis", backref="user", lazy=True, cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# 就活軸
# ---------------------------------------------------------------------------
class JobAxis(db.Model):
    __tablename__ = "job_axes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.Integer, default=1)


# ---------------------------------------------------------------------------
# 企業×軸 合致度（多対多の中間テーブル）
# ---------------------------------------------------------------------------
class CompanyAxisMatch(db.Model):
    __tablename__ = "company_axis_match"

    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), primary_key=True)
    axis_id = db.Column(db.Integer, db.ForeignKey("job_axes.id"), primary_key=True)
    score = db.Column(db.Integer, default=3)  # 1〜5


# ---------------------------------------------------------------------------
# 企業
# ---------------------------------------------------------------------------
class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    industry = db.Column(db.String(100), nullable=True)
    job_type = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    preference = db.Column(db.Integer, default=3)  # 1〜5
    mypage_url = db.Column(db.String(500), nullable=True)
    mypage_id = db.Column(db.String(200), nullable=True)
    mypage_password = db.Column(db.String(500), nullable=True)  # 暗号化して保存
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # リレーション
    selections = db.relationship("Selection", backref="company", lazy=True, cascade="all, delete-orphan")
    motivations = db.relationship("Motivation", backref="company", lazy=True, cascade="all, delete-orphan")
    entry_sheets = db.relationship("EntrySheet", backref="company", lazy=True, cascade="all, delete-orphan")
    schedules = db.relationship("Schedule", backref="company", lazy=True)
    axis_matches = db.relationship("CompanyAxisMatch", backref="company", lazy=True, cascade="all, delete-orphan")

    @property
    def latest_selection(self):
        """最新の選考ステータスを返す."""
        if not self.selections:
            return None
        return max(self.selections, key=lambda s: s.scheduled_at or datetime(1, 1, 1))

    @property
    def status_label(self):
        """現在のステータスラベルを返す."""
        latest = self.latest_selection
        if latest:
            return latest.status
        return "未応募"


# ---------------------------------------------------------------------------
# 選考状況
# ---------------------------------------------------------------------------
SELECTION_STAGES = [
    "エントリー開始待ち",
    "エントリー",
    "書類選考",
    "適性検査",
    "1次面接",
    "2次面接",
    "3次面接",
    "最終面接",
]

SELECTION_STATUSES = [
    "予定",
    "結果待ち",
    "合格",
    "不合格",
    "辞退",
    "内定",
]


class Selection(db.Model):
    __tablename__ = "selections"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    stage = db.Column(db.String(50), nullable=False)  # SELECTION_STAGES の値
    status = db.Column(db.String(50), default="予定")  # SELECTION_STATUSES の値
    scheduled_at = db.Column(db.DateTime, nullable=True)
    location = db.Column(db.String(300), nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # 面接振り返り用
    interview_notes = db.relationship("InterviewNote", backref="selection", lazy=True, cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# 面接振り返りノート
# ---------------------------------------------------------------------------
class InterviewNote(db.Model):
    __tablename__ = "interview_notes"

    id = db.Column(db.Integer, primary_key=True)
    selection_id = db.Column(db.Integer, db.ForeignKey("selections.id"), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=True)
    reflection = db.Column(db.Text, nullable=True)


# ---------------------------------------------------------------------------
# 志望動機
# ---------------------------------------------------------------------------
class Motivation(db.Model):
    __tablename__ = "motivations"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    version = db.Column(db.Integer, default=1)
    target_use = db.Column(db.String(50), nullable=True)  # ES / 面接
    review_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# ES（エントリーシート）
# ---------------------------------------------------------------------------
class EntrySheet(db.Model):
    __tablename__ = "entry_sheets"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=True)
    char_limit = db.Column(db.Integer, nullable=True)
    deadline = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default="下書き")  # 下書き/提出済み/合格/不合格
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# スケジュール
# ---------------------------------------------------------------------------
EVENT_TYPES = [
    "説明会",
    "ES締め切り",
    "面接",
    "その他",
]


class Schedule(db.Model):
    __tablename__ = "schedules"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=True)
    event_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    start_at = db.Column(db.DateTime, nullable=False)
    end_at = db.Column(db.DateTime, nullable=True)
    location_or_url = db.Column(db.String(500), nullable=True)
    reminder = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# 自己分析
# ---------------------------------------------------------------------------
ANALYSIS_CATEGORIES = ["自己PR", "ガクチカ", "長所", "短所"]


class SelfAnalysis(db.Model):
    __tablename__ = "self_analyses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # ANALYSIS_CATEGORIES の値
    content = db.Column(db.Text, nullable=False)
    version = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
