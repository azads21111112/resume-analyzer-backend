from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


skills_list = [

    "python",
    "java",
    "flutter",
    "dart",
    "firebase",
    "machine learning",
    "data analysis",
    "sql",
    "html",
    "css",
    "javascript",
    "react",
    "c++",
    "tensorflow",
    "deep learning",
]


def extract_skills(text):

    text = text.lower()

    found_skills = []

    for skill in skills_list:

        if skill in text:

            found_skills.append(skill)

    return found_skills


def calculate_ats_score(

    resume_text,

    matched_skills,

    job_skills
):

    ats_score = 0

    checks = []

    # Skill Score

    if len(job_skills) > 0:

        skill_score = (

            len(matched_skills)

            /

            len(job_skills)

        ) * 40

        ats_score += skill_score

    # Education

    if "education" in resume_text.lower():

        ats_score += 10

        checks.append(
            "Education Section Found"
        )

    # Experience

    if "experience" in resume_text.lower():

        ats_score += 10

        checks.append(
            "Experience Section Found"
        )

    # Projects

    if "project" in resume_text.lower():

        ats_score += 10

        checks.append(
            "Projects Section Found"
        )

    # Email

    email_pattern = r'\S+@\S+'

    if re.search(

        email_pattern,

        resume_text
    ):

        ats_score += 10

        checks.append(
            "Email Found"
        )

    # Phone Number

    phone_pattern = r'\d{10}'

    if re.search(

        phone_pattern,

        resume_text
    ):

        ats_score += 10

        checks.append(
            "Phone Number Found"
        )

    # Resume Length

    words = resume_text.split()

    if 100 <= len(words) <= 1000:

        ats_score += 10

        checks.append(
            "Resume Length Good"
        )

    return round(ats_score, 2), checks


def calculate_match(

    resume_text,

    job_description
):

    vectorizer = TfidfVectorizer()

    vectors = vectorizer.fit_transform([

        resume_text,

        job_description
    ])

    similarity = cosine_similarity(vectors)

    match_percentage = similarity[0][1] * 100

    resume_skills = extract_skills(
        resume_text
    )

    job_skills = extract_skills(
        job_description
    )

    matched_skills = list(

        set(resume_skills)

        &

        set(job_skills)
    )

    missing_skills = list(

        set(job_skills)

        -

        set(resume_skills)
    )

    if len(job_skills) > 0:

        resume_score = (

            len(matched_skills)

            /

            len(job_skills)

        ) * 100

    else:

        resume_score = 0

    recommendations = [

        f"Learn {skill}"

        for skill in missing_skills
    ]

    if resume_score >= 80:

        summary = (
            "Excellent match for this role."
        )

    elif resume_score >= 50:

        summary = (
            "Moderate match. Some important skills are missing."
        )

    else:

        summary = (
            "Low match detected. Improve your technical skills."
        )

    ats_score, ats_checks = calculate_ats_score(

        resume_text,

        matched_skills,

        job_skills
    )

    return {

        "match_percentage":
            round(match_percentage, 2),

        "resume_score":
            round(resume_score, 2),

        "matched_skills":
            matched_skills,

        "missing_skills":
            missing_skills,

        "recommendations":
            recommendations,

        "summary":
            summary,

        "ats_score":
            ats_score,

        "ats_checks":
            ats_checks
    }