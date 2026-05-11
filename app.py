from flask import Flask, request, jsonify

from resume_parser import extract_text_from_pdf

from job_matcher import calculate_match

app = Flask(__name__)


@app.route("/analyze", methods=["POST"])
def analyze_resume():

    pdf_file = request.files["resume"]

    job_description = request.form["job_description"]

    pdf_path = "temp_resume.pdf"

    pdf_file.save(pdf_path)

    resume_text = extract_text_from_pdf(pdf_path)

    result = calculate_match(
        resume_text,
        job_description
    )

    return jsonify(result)


if __name__ == "__main__":

    app.run(
    host="0.0.0.0",
    port=5000
)