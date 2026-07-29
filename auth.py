from flask import Blueprint, request, jsonify
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database import db
from models import User, Analysis

from sqlalchemy import func



auth = Blueprint("auth", __name__)


# ==========================
# User Registration
# ==========================
@auth.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({
            "success": False,
            "message": "All fields are required"
        }), 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({
            "success": False,
            "message": "Email already exists"
        }), 409

    hashed_password = generate_password_hash(
        password,
        method="pbkdf2:sha256"
    )

    user = User(
        name=name,
        email=email,
        password=hashed_password
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Registration Successful"
    }), 201


# ==========================
# User Login
# ==========================
@auth.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    print("========== LOGIN ==========")
    print("Received Email:", repr(email))
    print("Received Password:", repr(password))

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and Password are required"
        }), 400

    user = User.query.filter_by(email=email).first()

    print("User Found:", user)

    if not user:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    if not check_password_hash(user.password, password):
        return jsonify({
            "success": False,
            "message": "Invalid password"
        }), 401

    return jsonify({
        "success": True,
        "message": "Login Successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }), 200

# ==========================
# Analysis History
# ==========================
@auth.route("/history/<int:user_id>", methods=["GET"])
def history(user_id):

    analyses = Analysis.query.filter_by(user_id=user_id) \
        .order_by(Analysis.analyzed_at.desc()) \
        .all()

    history_data = []

    for item in analyses:

        history_data.append({
            "id": item.id,
            "resume_filename": item.resume_filename,
            "ats_score": item.ats_score,
            "match_score": item.match_score,
            "resume_score": item.resume_score,
            "summary": item.summary,
            "date": item.analyzed_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify({
        "success": True,
        "history": history_data
    }), 200



@auth.route("/dashboard/<int:user_id>", methods=["GET"])
def dashboard(user_id):

    total = Analysis.query.filter_by(user_id=user_id).count()

    avg_ats = db.session.query(
        func.avg(Analysis.ats_score)
    ).filter_by(user_id=user_id).scalar() or 0

    avg_match = db.session.query(
        func.avg(Analysis.match_score)
    ).filter_by(user_id=user_id).scalar() or 0

    best_resume = db.session.query(
        func.max(Analysis.resume_score)
    ).filter_by(user_id=user_id).scalar() or 0

    latest = Analysis.query.filter_by(user_id=user_id) \
        .order_by(Analysis.analyzed_at.desc()) \
        .first()

    return jsonify({
        "success": True,
        "dashboard": {
            "total_analyses": total,
            "average_ats_score": round(avg_ats, 2),
            "average_match_score": round(avg_match, 2),
            "best_resume_score": round(best_resume, 2),
            "last_resume": latest.resume_filename if latest else None
        }
    }), 200


# ==========================
# Delete Single Analysis
# ==========================
@auth.route("/delete_analysis/<int:analysis_id>", methods=["DELETE"])
def delete_analysis(analysis_id):

    analysis = Analysis.query.get(analysis_id)

    if not analysis:
        return jsonify({
            "success": False,
            "message": "Analysis not found"
        }), 404

    db.session.delete(analysis)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Analysis deleted successfully"
    }), 200

# ==========================
# Update User Profile
# ==========================
@auth.route("/update_profile/<int:user_id>", methods=["PUT"])
def update_profile(user_id):

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    data = request.get_json()

    if "name" in data:
        user.name = data["name"]

    if "password" in data and data["password"]:
        user.password = generate_password_hash(
            data["password"],
            method="pbkdf2:sha256"
        )

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Profile updated successfully"
    }), 200