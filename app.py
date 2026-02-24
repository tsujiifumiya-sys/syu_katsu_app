"""就活管理アプリ — Flask メインアプリケーション."""

import os
from datetime import datetime, timezone
from functools import wraps

from flask import (
    Blueprint,
    Flask,
    Response,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from config import Config, RESOURCE_DIR
from models import (
    ANALYSIS_CATEGORIES,
    EVENT_TYPES,
    SELECTION_STAGES,
    SELECTION_STATUSES,
    Company,
    CompanyAxisMatch,
    EntrySheet,
    InterviewNote,
    JobAxis,
    Motivation,
    Schedule,
    Selection,
    SelfAnalysis,
    User,
    db,
)

# ==================================================================
# Blueprint 定義 — ルートを create_app() の外に定義
# ==================================================================
main_bp = Blueprint("main", __name__)


def _parse_datetime(value):
    """文字列を datetime に変換."""
    if not value:
        return None
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


# ------------------------------------------------------------------
# ダッシュボード
# ------------------------------------------------------------------
@main_bp.route("/")
def dashboard():
    user = User.query.first()
    companies = Company.query.filter_by(user_id=user.id).order_by(Company.preference.desc()).all()

    upcoming = (
        Schedule.query.filter_by(user_id=user.id)
        .filter(Schedule.start_at >= datetime.now(timezone.utc))
        .order_by(Schedule.start_at)
        .limit(5)
        .all()
    )

    # ES締切ウィジェット: 未提出のESを締切順で取得
    from datetime import date
    es_deadlines = (
        EntrySheet.query.join(Company)
        .filter(Company.user_id == user.id)
        .filter(EntrySheet.status.in_(['下書き']))
        .filter(EntrySheet.deadline.isnot(None))
        .order_by(EntrySheet.deadline.asc())
        .limit(8)
        .all()
    )
    today = date.today()

    return render_template(
        "dashboard.html",
        user=user,
        companies=companies,
        upcoming=upcoming,
        es_deadlines=es_deadlines,
        today=today,
    )


# ------------------------------------------------------------------
# 企業管理
# ------------------------------------------------------------------
@main_bp.route("/companies")
def company_list():
    user = User.query.first()
    companies = (
        Company.query.filter_by(user_id=user.id)
        .order_by(Company.preference.desc())
        .all()
    )
    return render_template("companies.html", companies=companies)


@main_bp.route("/companies/new", methods=["GET", "POST"])
def company_new():
    user = User.query.first()
    if request.method == "POST":
        company = Company(
            user_id=user.id,
            name=request.form.get("name", ""),
            industry=request.form.get("industry", ""),
            job_type=request.form.get("job_type", ""),
            description=request.form.get("description", ""),
            preference=int(request.form.get("preference", 3)),
            mypage_url=request.form.get("mypage_url", ""),
            mypage_id=request.form.get("mypage_id", ""),
            mypage_password=request.form.get("mypage_password", ""),
            notes=request.form.get("notes", ""),
        )
        db.session.add(company)
        db.session.commit()
        return redirect(url_for("main.company_detail", company_id=company.id))
    return render_template("company_form.html", company=None)


@main_bp.route("/companies/<int:company_id>")
def company_detail(company_id):
    company = Company.query.get_or_404(company_id)
    axes = JobAxis.query.filter_by(user_id=company.user_id).all()
    return render_template(
        "company_detail.html",
        company=company,
        axes=axes,
        stages=SELECTION_STAGES,
        statuses=SELECTION_STATUSES,
    )


@main_bp.route("/companies/<int:company_id>/edit", methods=["GET", "POST"])
def company_edit(company_id):
    company = Company.query.get_or_404(company_id)
    if request.method == "POST":
        company.name = request.form.get("name", company.name)
        company.industry = request.form.get("industry", "")
        company.job_type = request.form.get("job_type", "")
        company.description = request.form.get("description", "")
        company.preference = int(request.form.get("preference", 3))
        company.mypage_url = request.form.get("mypage_url", "")
        company.mypage_id = request.form.get("mypage_id", "")
        company.mypage_password = request.form.get("mypage_password", "")
        company.notes = request.form.get("notes", "")
        db.session.commit()
        return redirect(url_for("main.company_detail", company_id=company.id))
    return render_template("company_form.html", company=company)


@main_bp.route("/companies/<int:company_id>/delete", methods=["POST"])
def company_delete(company_id):
    company = Company.query.get_or_404(company_id)
    db.session.delete(company)
    db.session.commit()
    return redirect(url_for("main.company_list"))


# ------------------------------------------------------------------
# 選考管理
# ------------------------------------------------------------------
@main_bp.route("/companies/<int:company_id>/selections/new", methods=["POST"])
def selection_new(company_id):
    Company.query.get_or_404(company_id)
    sel = Selection(
        company_id=company_id,
        stage=request.form.get("stage", "エントリー"),
        status=request.form.get("status", "予定"),
        scheduled_at=_parse_datetime(request.form.get("scheduled_at")),
        location=request.form.get("location", ""),
        feedback=request.form.get("feedback", ""),
    )
    db.session.add(sel)
    db.session.commit()
    return redirect(url_for("main.company_detail", company_id=company_id))


@main_bp.route("/selections/<int:sel_id>/update", methods=["POST"])
def selection_update(sel_id):
    sel = Selection.query.get_or_404(sel_id)
    sel.status = request.form.get("status", sel.status)
    sel.feedback = request.form.get("feedback", sel.feedback)
    db.session.commit()
    return redirect(url_for("main.company_detail", company_id=sel.company_id))


# ------------------------------------------------------------------
# スケジュール (API for FullCalendar)
# ------------------------------------------------------------------
@main_bp.route("/calendar")
def calendar_view():
    return render_template("calendar.html", event_types=EVENT_TYPES)


@main_bp.route("/api/events")
def api_events():
    user = User.query.first()
    schedules = Schedule.query.filter_by(user_id=user.id).all()
    events = []
    color_map = {
        "説明会": "#6366f1",
        "ES締切": "#f59e0b",
        "Webテスト": "#10b981",
        "面接": "#ef4444",
        "OB訪問": "#8b5cf6",
        "内定承諾期限": "#ec4899",
        "その他": "#64748b",
    }
    for s in schedules:
        events.append(
            {
                "id": s.id,
                "title": s.title,
                "start": s.start_at.isoformat() if s.start_at else None,
                "end": s.end_at.isoformat() if s.end_at else None,
                "backgroundColor": color_map.get(s.event_type, "#64748b"),
                "borderColor": color_map.get(s.event_type, "#64748b"),
                "extendedProps": {
                    "event_type": s.event_type,
                    "location_or_url": s.location_or_url or "",
                    "company_name": s.company.name if s.company else "",
                    "company_id": s.company_id,
                },
            }
        )
    return jsonify(events)


@main_bp.route("/api/events", methods=["POST"])
def api_event_create():
    user = User.query.first()
    data = request.get_json()
    schedule = Schedule(
        user_id=user.id,
        company_id=data.get("company_id") or None,
        event_type=data.get("event_type", "その他"),
        title=data.get("title", ""),
        start_at=_parse_datetime(data.get("start")),
        end_at=_parse_datetime(data.get("end")),
        location_or_url=data.get("location_or_url", ""),
    )
    db.session.add(schedule)
    db.session.commit()
    return jsonify({"id": schedule.id}), 201


@main_bp.route("/api/events/<int:event_id>", methods=["PUT"])
def api_event_update(event_id):
    schedule = Schedule.query.get_or_404(event_id)
    data = request.get_json()
    if "title" in data:
        schedule.title = data["title"]
    if "start" in data:
        schedule.start_at = _parse_datetime(data["start"])
    if "end" in data:
        schedule.end_at = _parse_datetime(data["end"])
    if "event_type" in data:
        schedule.event_type = data["event_type"]
    if "location_or_url" in data:
        schedule.location_or_url = data["location_or_url"]
    if "company_id" in data:
        schedule.company_id = data["company_id"] or None
    db.session.commit()
    return jsonify({"ok": True})


@main_bp.route("/api/events/<int:event_id>", methods=["DELETE"])
def api_event_delete(event_id):
    schedule = Schedule.query.get_or_404(event_id)
    db.session.delete(schedule)
    db.session.commit()
    return jsonify({"ok": True})


# ------------------------------------------------------------------
# 就活軸管理
# ------------------------------------------------------------------
@main_bp.route("/axes")
def axes_list():
    user = User.query.first()
    axes = (
        JobAxis.query.filter_by(user_id=user.id).order_by(JobAxis.priority).all()
    )
    return render_template("axes.html", axes=axes)


@main_bp.route("/axes/new", methods=["POST"])
def axis_new():
    user = User.query.first()
    axis = JobAxis(
        user_id=user.id,
        name=request.form.get("name", ""),
        description=request.form.get("description", ""),
        priority=int(request.form.get("priority", 1)),
    )
    db.session.add(axis)
    db.session.commit()
    return redirect(url_for("main.axes_list"))


@main_bp.route("/axes/<int:axis_id>/delete", methods=["POST"])
def axis_delete(axis_id):
    axis = JobAxis.query.get_or_404(axis_id)
    db.session.delete(axis)
    db.session.commit()
    return redirect(url_for("main.axes_list"))


# ------------------------------------------------------------------
# 企業×就活軸マトリックス
# ------------------------------------------------------------------
@main_bp.route("/matrix")
def axis_matrix():
    user = User.query.first()
    companies = Company.query.filter_by(user_id=user.id).order_by(Company.preference.desc()).all()
    axes = JobAxis.query.filter_by(user_id=user.id).order_by(JobAxis.priority).all()

    # 既存スコアを dict化: {(company_id, axis_id): score}
    scores = {}
    for match in CompanyAxisMatch.query.all():
        scores[(match.company_id, match.axis_id)] = match.score

    return render_template(
        "axis_matrix.html",
        companies=companies,
        axes=axes,
        scores=scores,
    )


@main_bp.route("/matrix/save", methods=["POST"])
def axis_matrix_save():
    """AJAXでスコアを保存."""
    data = request.get_json()
    company_id = int(data.get("company_id"))
    axis_id = int(data.get("axis_id"))
    score = int(data.get("score", 0))

    match = CompanyAxisMatch.query.filter_by(
        company_id=company_id, axis_id=axis_id
    ).first()

    if score == 0:
        # スコア0 = 削除
        if match:
            db.session.delete(match)
    else:
        if match:
            match.score = score
        else:
            match = CompanyAxisMatch(
                company_id=company_id, axis_id=axis_id, score=score
            )
            db.session.add(match)

    db.session.commit()
    return jsonify({"ok": True})


# ------------------------------------------------------------------
# 企業一覧 API（カレンダーのドロップダウン用）
# ------------------------------------------------------------------
@main_bp.route("/api/companies")
def api_companies():
    user = User.query.first()
    companies = (
        Company.query.filter_by(user_id=user.id).order_by(Company.name).all()
    )
    return jsonify([{"id": c.id, "name": c.name} for c in companies])


# ------------------------------------------------------------------
# ES（エントリーシート）管理
# ------------------------------------------------------------------
ES_STATUSES = ["下書き", "提出済み", "合格", "不合格"]


@main_bp.route("/es")
def es_list():
    """ES 一覧（全企業分をまとめて表示）."""
    user = User.query.first()
    companies = Company.query.filter_by(user_id=user.id).order_by(Company.name).all()
    # 締切が近い順にソート
    all_es = (
        EntrySheet.query.join(Company)
        .filter(Company.user_id == user.id)
        .order_by(EntrySheet.deadline.asc().nullslast(), EntrySheet.created_at.desc())
        .all()
    )
    return render_template("es_list.html", entry_sheets=all_es, companies=companies, es_statuses=ES_STATUSES)


@main_bp.route("/es/new", methods=["GET", "POST"])
def es_new():
    user = User.query.first()
    companies = Company.query.filter_by(user_id=user.id).order_by(Company.name).all()
    if request.method == "POST":
        es = EntrySheet(
            company_id=int(request.form.get("company_id")),
            question=request.form.get("question", ""),
            answer=request.form.get("answer", ""),
            char_limit=int(request.form.get("char_limit") or 0) or None,
            deadline=_parse_date(request.form.get("deadline")),
            status=request.form.get("status", "下書き"),
        )
        db.session.add(es)
        db.session.commit()
        return redirect(url_for("main.es_list"))
    return render_template("es_form.html", es=None, companies=companies, es_statuses=ES_STATUSES)


@main_bp.route("/es/<int:es_id>/edit", methods=["GET", "POST"])
def es_edit(es_id):
    es = EntrySheet.query.get_or_404(es_id)
    user = User.query.first()
    companies = Company.query.filter_by(user_id=user.id).order_by(Company.name).all()
    if request.method == "POST":
        es.company_id = int(request.form.get("company_id", es.company_id))
        es.question = request.form.get("question", es.question)
        es.answer = request.form.get("answer", "")
        es.char_limit = int(request.form.get("char_limit") or 0) or None
        es.deadline = _parse_date(request.form.get("deadline"))
        es.status = request.form.get("status", es.status)
        db.session.commit()
        return redirect(url_for("main.es_list"))
    return render_template("es_form.html", es=es, companies=companies, es_statuses=ES_STATUSES)


@main_bp.route("/es/<int:es_id>/delete", methods=["POST"])
def es_delete(es_id):
    es = EntrySheet.query.get_or_404(es_id)
    db.session.delete(es)
    db.session.commit()
    return redirect(url_for("main.es_list"))


# ------------------------------------------------------------------
# 志望動機管理
# ------------------------------------------------------------------
MOTIVATION_USES = ["ES", "面接", "OB訪問", "その他"]


@main_bp.route("/motivations")
def motivation_list():
    """志望動機一覧（企業別にグループ化）."""
    user = User.query.first()
    companies = (
        Company.query.filter_by(user_id=user.id)
        .order_by(Company.preference.desc())
        .all()
    )
    return render_template("motivation_list.html", companies=companies, uses=MOTIVATION_USES)


@main_bp.route("/motivations/new", methods=["GET", "POST"])
def motivation_new():
    user = User.query.first()
    companies = Company.query.filter_by(user_id=user.id).order_by(Company.name).all()
    if request.method == "POST":
        company_id = int(request.form.get("company_id"))
        # 同じ企業の既存バージョンの最大値 + 1
        max_ver = (
            db.session.query(db.func.max(Motivation.version))
            .filter_by(company_id=company_id)
            .scalar()
            or 0
        )
        mot = Motivation(
            company_id=company_id,
            content=request.form.get("content", ""),
            version=max_ver + 1,
            target_use=request.form.get("target_use", "ES"),
            review_notes=request.form.get("review_notes", ""),
        )
        db.session.add(mot)
        db.session.commit()
        return redirect(url_for("main.motivation_list"))
    return render_template("motivation_form.html", motivation=None, companies=companies, uses=MOTIVATION_USES)


@main_bp.route("/motivations/<int:mot_id>/edit", methods=["GET", "POST"])
def motivation_edit(mot_id):
    mot = Motivation.query.get_or_404(mot_id)
    user = User.query.first()
    companies = Company.query.filter_by(user_id=user.id).order_by(Company.name).all()
    if request.method == "POST":
        mot.content = request.form.get("content", mot.content)
        mot.target_use = request.form.get("target_use", mot.target_use)
        mot.review_notes = request.form.get("review_notes", "")
        db.session.commit()
        return redirect(url_for("main.motivation_list"))
    return render_template("motivation_form.html", motivation=mot, companies=companies, uses=MOTIVATION_USES)


@main_bp.route("/motivations/<int:mot_id>/delete", methods=["POST"])
def motivation_delete(mot_id):
    mot = Motivation.query.get_or_404(mot_id)
    db.session.delete(mot)
    db.session.commit()
    return redirect(url_for("main.motivation_list"))


# ------------------------------------------------------------------
# 自己分析
# ------------------------------------------------------------------
@main_bp.route("/self-analysis")
def self_analysis_list():
    user = User.query.first()
    analyses = {}
    for cat in ANALYSIS_CATEGORIES:
        analyses[cat] = (
            SelfAnalysis.query.filter_by(user_id=user.id, category=cat)
            .order_by(SelfAnalysis.version.desc())
            .all()
        )
    return render_template(
        "self_analysis.html",
        analyses=analyses,
        categories=ANALYSIS_CATEGORIES,
    )


@main_bp.route("/self-analysis/new", methods=["GET", "POST"])
def self_analysis_new():
    user = User.query.first()
    if request.method == "POST":
        category = request.form.get("category", "自己PR")
        max_ver = (
            db.session.query(db.func.max(SelfAnalysis.version))
            .filter_by(user_id=user.id, category=category)
            .scalar()
            or 0
        )
        sa = SelfAnalysis(
            user_id=user.id,
            category=category,
            content=request.form.get("content", ""),
            version=max_ver + 1,
        )
        db.session.add(sa)
        db.session.commit()
        return redirect(url_for("main.self_analysis_list"))
    return render_template(
        "self_analysis_form.html",
        analysis=None,
        categories=ANALYSIS_CATEGORIES,
    )


@main_bp.route("/self-analysis/<int:sa_id>/edit", methods=["GET", "POST"])
def self_analysis_edit(sa_id):
    sa = SelfAnalysis.query.get_or_404(sa_id)
    if request.method == "POST":
        sa.content = request.form.get("content", sa.content)
        db.session.commit()
        return redirect(url_for("main.self_analysis_list"))
    return render_template(
        "self_analysis_form.html",
        analysis=sa,
        categories=ANALYSIS_CATEGORIES,
    )


@main_bp.route("/self-analysis/<int:sa_id>/delete", methods=["POST"])
def self_analysis_delete(sa_id):
    sa = SelfAnalysis.query.get_or_404(sa_id)
    db.session.delete(sa)
    db.session.commit()
    return redirect(url_for("main.self_analysis_list"))


# ------------------------------------------------------------------
# ヘルパー（日付パース）
# ------------------------------------------------------------------
def _parse_date(value):
    """文字列を date に変換."""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


# ==================================================================
# アプリケーションファクトリ
# ==================================================================
def create_app():
    """Flask アプリケーションファクトリ."""
    import sys

    # PyInstaller 実行時はリソースディレクトリを明示指定
    app = Flask(
        __name__,
        template_folder=os.path.join(RESOURCE_DIR, "templates"),
        static_folder=os.path.join(RESOURCE_DIR, "static"),
    )
    app.config.from_object(Config)
    db.init_app(app)

    # Blueprint をアプリに登録
    app.register_blueprint(main_bp)

    # ----------------------------------------------------------
    # Basic 認証（環境変数で有効化、ローカル開発時は無効）
    # ----------------------------------------------------------
    auth_user = os.environ.get("BASIC_AUTH_USERNAME")
    auth_pass = os.environ.get("BASIC_AUTH_PASSWORD")

    if auth_user and auth_pass:

        @app.before_request
        def require_basic_auth():
            auth = request.authorization
            if (
                not auth
                or auth.username != auth_user
                or auth.password != auth_pass
            ):
                return Response(
                    "認証が必要です。",
                    401,
                    {"WWW-Authenticate": 'Basic realm="Syu_katsu"'},
                )

    with app.app_context():
        db.create_all()
        if not User.query.first():
            default_user = User(name="ユーザー")
            db.session.add(default_user)
            db.session.commit()

    return app
# ==================================================================
# アプリケーションインスタンス（gunicorn が app:app でインポート可能）
# ==================================================================
app = create_app()


if __name__ == "__main__":
    import sys
    import webbrowser
    import threading

    # exe として実行されている場合はブラウザを自動起動
    is_frozen = getattr(sys, "frozen", False)
    if is_frozen:
        def open_browser():
            webbrowser.open("http://127.0.0.1:5000")
        threading.Timer(1.5, open_browser).start()

    app.run(
        debug=not is_frozen,
        port=5000,
        use_reloader=not is_frozen,
    )
