from database import db
from datetime import datetime


# ======================================================
# User Model
# ======================================================

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    analyses = db.relationship(
        "Analysis",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )


# ======================================================
# Resume Model
# ======================================================

class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    filename = db.Column(
        db.String(255),
        nullable=False
    )

    upload_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# ======================================================
# Analysis Model
# ======================================================

class Analysis(db.Model):
    __tablename__ = "analysis"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    resume_filename = db.Column(
        db.String(255),
        nullable=False
    )

    ats_score = db.Column(
        db.Float,
        default=0
    )

    match_score = db.Column(
        db.Float,
        default=0
    )

    resume_score = db.Column(
        db.Float,
        default=0
    )

    summary = db.Column(
        db.Text,
        default=""
    )

    ats_checks = db.Column(
        db.Text,
        default=""
    )

    matched_skills = db.Column(
        db.Text,
        default=""
    )

    missing_skills = db.Column(
        db.Text,
        default=""
    )

    recommendations = db.Column(
        db.Text,
        default=""
    )

    recommended_jobs = db.Column(
        db.Text,
        default=""
    )

    recommended_careers = db.Column(
        db.Text,
        default=""
    )

    analyzed_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )