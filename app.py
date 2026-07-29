print("App started")
from flask import Flask, request, jsonify

from flask_cors import CORS

import os

import uuid

import json

from resume_parser import extract_text_from_pdf

from job_matcher import calculate_match

from database import db
from models import User, Resume, Analysis
from auth import auth

from sqlalchemy import desc
from sqlalchemy import func

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from flask import send_file

app = Flask(__name__)

# ======================================================
# Upload Folder
# ======================================================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


CORS(app)

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = \
    "sqlite:///" + os.path.join(BASE_DIR, "database", "resume.db")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(auth)




@app.route("/analyze", methods=["POST"])
def analyze_resume():

    try:

        # ==========================
        # Validate Input
        # ==========================

        if "resume" not in request.files:
            return jsonify({
                "success": False,
                "message": "Resume file is required."
            }), 400

        pdf_file = request.files["resume"]

        if pdf_file.filename == "":
            return jsonify({
                "success": False,
                "message": "Please select a PDF file."
            }), 400

        if not pdf_file.filename.lower().endswith(".pdf"):
            return jsonify({
                "success": False,
                "message": "Only PDF files are allowed."
            }), 400

        job_description = request.form.get(
            "job_description",
            ""
        ).strip()

        if not job_description:
            return jsonify({
                "success": False,
                "message": "Job description is required."
            }), 400

        user_id = int(
            request.form.get("user_id", 1)
        )

        # ==========================
        # Save Uploaded File
        # ==========================

        unique_filename = (
            f"{uuid.uuid4().hex}.pdf"
        )

        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            unique_filename
        )

        pdf_file.save(file_path)

        # ==========================
        # Resume Analysis
        # ==========================

        resume_text = extract_text_from_pdf(
            file_path
        )

        result = calculate_match(
            resume_text,
            job_description
        )

        # ==========================
        # Save to Database
        # ==========================

        analysis = Analysis(

            user_id=user_id,

            resume_filename=pdf_file.filename,

            ats_score=result.get(
                "ats_score",
                0
            ),

            match_score=result.get(
                "match_percentage",
                0
            ),

            resume_score=result.get(
                "resume_score",
                0
            ),

            summary=result.get(
                "summary",
                ""
            ),

            ats_checks=json.dumps(
                result.get(
                    "ats_checks",
                    []
                )
            ),

            matched_skills=json.dumps(
                result.get(
                    "matched_skills",
                    []
                )
            ),

            missing_skills=json.dumps(
                result.get(
                    "missing_skills",
                    []
                )
            ),

            recommendations=json.dumps(
                result.get(
                    "recommendations",
                    []
                )
            ),

            recommended_jobs=json.dumps(
                result.get(
                    "recommended_jobs",
                    []
                )
            ),

            recommended_careers=json.dumps(
                result.get(
                    "recommended_careers",
                    []
                )
            )

        )

        db.session.add(analysis)

        db.session.commit()

        # ==========================
        # Delete Temporary File
        # ==========================

        if os.path.exists(file_path):
            os.remove(file_path)

        return jsonify({

            "success": True,

            "message": "Resume analyzed successfully.",

            "data": result

        }), 200

    except Exception as e:

        db.session.rollback()

        return jsonify({

            "success": False,

            "message": str(e)

        }), 500









@app.route("/history/<int:user_id>", methods=["GET"])
def get_history(user_id):

    try:

        analyses = Analysis.query.filter_by(
            user_id=user_id
        ).order_by(
            desc(Analysis.analyzed_at)
        ).all()

        history = []

        for item in analyses:

            history.append({

                "id": item.id,

                "resume_filename": item.resume_filename,

                "ats_score": item.ats_score,

                "match_score": item.match_score,

                "resume_score": item.resume_score,

                "summary": item.summary,

                "ats_checks": json.loads(item.ats_checks),

                "matched_skills": json.loads(item.matched_skills),

                "missing_skills": json.loads(item.missing_skills),

                "recommendations": json.loads(item.recommendations),

                "recommended_jobs": json.loads(item.recommended_jobs),

                "recommended_careers": json.loads(item.recommended_careers),

                "analyzed_at": item.analyzed_at.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

            })

        return jsonify({

            "success": True,

            "count": len(history),

            "history": history

        }), 200

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)

        }), 500


@app.route("/history/<int:analysis_id>", methods=["DELETE"])
def delete_history(analysis_id):

    try:

        analysis = Analysis.query.get(analysis_id)

        if analysis is None:

            return jsonify({

                "success": False,

                "message": "Analysis not found."

            }), 404

        db.session.delete(analysis)

        db.session.commit()

        return jsonify({

            "success": True,

            "message": "History deleted successfully."

        }), 200

    except Exception as e:

        db.session.rollback()

        return jsonify({

            "success": False,

            "message": str(e)

        }), 500


@app.route("/dashboard/<int:user_id>", methods=["GET"])
def dashboard(user_id):

    try:

        total_resumes = Analysis.query.filter_by(
            user_id=user_id
        ).count()

        average_ats = db.session.query(
            func.avg(Analysis.ats_score)
        ).filter_by(
            user_id=user_id
        ).scalar()

        average_match = db.session.query(
            func.avg(Analysis.match_score)
        ).filter_by(
            user_id=user_id
        ).scalar()

        average_resume = db.session.query(
            func.avg(Analysis.resume_score)
        ).filter_by(
            user_id=user_id
        ).scalar()

        best_ats = db.session.query(
            func.max(Analysis.ats_score)
        ).filter_by(
            user_id=user_id
        ).scalar()

        best_match = db.session.query(
            func.max(Analysis.match_score)
        ).filter_by(
            user_id=user_id
        ).scalar()

        best_resume = db.session.query(
            func.max(Analysis.resume_score)
        ).filter_by(
            user_id=user_id
        ).scalar()

        return jsonify({

            "success": True,

            "data": {

                "total_resumes": total_resumes,

                "average_ats_score": round(average_ats or 0, 2),

                "average_match_score": round(average_match or 0, 2),

                "average_resume_score": round(average_resume or 0, 2),

                "best_ats_score": round(best_ats or 0, 2),

                "best_match_score": round(best_match or 0, 2),

                "best_resume_score": round(best_resume or 0, 2)

            }

        }), 200

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)

        }), 500







@app.route("/profile/<int:user_id>", methods=["GET"])
def get_profile(user_id):

    try:

        user = User.query.get(user_id)

        if user is None:

            return jsonify({

                "success": False,

                "message": "User not found."

            }), 404

        total_resumes = Analysis.query.filter_by(
            user_id=user_id
        ).count()

        average_ats = db.session.query(
            func.avg(Analysis.ats_score)
        ).filter_by(
            user_id=user_id
        ).scalar()

        average_match = db.session.query(
            func.avg(Analysis.match_score)
        ).filter_by(
            user_id=user_id
        ).scalar()


        return jsonify({

            "success": True,

            "data": {

                "id": user.id,

                "name": user.name,

                "email": user.email,

                "created_at": user.created_at.strftime("%Y-%m-%d"),

                "total_resumes": total_resumes,

                "average_ats_score": round(average_ats or 0, 2),
                "average_match_score": round(average_match or 0, 2),

            }

        }), 200

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)

        }), 500











@app.route("/career/<int:user_id>", methods=["GET"])
def get_career(user_id):

    try:

        latest_analysis = Analysis.query.filter_by(
            user_id=user_id
        ).order_by(
            Analysis.analyzed_at.desc()
        ).first()

        if latest_analysis is None:

            return jsonify({

                "success": False,

                "message": "No analysis found."

            }), 404

        return jsonify({

            "success": True,

            "data": {

                "recommended_careers": json.loads(
                    latest_analysis.recommended_careers
                ),

                "recommended_jobs": json.loads(
                    latest_analysis.recommended_jobs
                ),

                "job_portals": [

                    {
                        "name": "Bdjobs",
                        "url": "https://bdjobs.com"
                    },

                    {
                        "name": "LinkedIn Jobs",
                        "url": "https://www.linkedin.com/jobs/"
                    },

                    {
                        "name": "Indeed",
                        "url": "https://www.indeed.com"
                    },

                    {
                        "name": "Glassdoor",
                        "url": "https://www.glassdoor.com/Jobs/"
                    }

                ]

            }

        }), 200

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)

        }), 500


@app.route("/export/<int:analysis_id>", methods=["GET"])
def export_pdf(analysis_id):

    try:

        analysis = Analysis.query.get(analysis_id)

        if analysis is None:

            return jsonify({
                "success": False,
                "message": "Analysis not found."
            }), 404

        pdf_name = f"analysis_{analysis.id}.pdf"

        pdf = SimpleDocTemplate(pdf_name)

        styles = getSampleStyleSheet()

        story = []

        story.append(Paragraph("<b>Resume Analysis Report</b>", styles["Heading1"]))

        story.append(Paragraph(f"Resume: {analysis.resume_filename}", styles["BodyText"]))
        story.append(Paragraph(f"ATS Score: {analysis.ats_score}", styles["BodyText"]))
        story.append(Paragraph(f"Match Score: {analysis.match_score}", styles["BodyText"]))
        story.append(Paragraph(f"Resume Score: {analysis.resume_score}", styles["BodyText"]))
        story.append(Paragraph(f"Summary: {analysis.summary}", styles["BodyText"]))

        story.append(Paragraph("<br/>", styles["BodyText"]))

        story.append(Paragraph("<b>Matched Skills</b>", styles["Heading2"]))
        story.append(
            Paragraph(
                ", ".join(json.loads(analysis.matched_skills)),
                styles["BodyText"]
            )
        )

        story.append(Paragraph("<b>Missing Skills</b>", styles["Heading2"]))
        story.append(
            Paragraph(
                ", ".join(json.loads(analysis.missing_skills)),
                styles["BodyText"]
            )
        )

        story.append(Paragraph("<b>Recommendations</b>", styles["Heading2"]))
        story.append(
            Paragraph(
                "<br/>".join(json.loads(analysis.recommendations)),
                styles["BodyText"]
            )
        )

        pdf.build(story)

        return send_file(
            pdf_name,
            as_attachment=True
        )

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route("/")
def home():
    return "Backend is running!"


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )