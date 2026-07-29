from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# =====================================
# Supported Skills
# =====================================

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

# =====================================
# Job Recommendation Mapping
# =====================================

JOB_MAPPING = {

    "python": [
        "Python Developer",
        "Backend Developer"
    ],

    "java": [
        "Java Developer",
        "Software Engineer"
    ],

    "flutter": [
        "Flutter Developer",
        "Mobile App Developer"
    ],

    "dart": [
        "Flutter Developer"
    ],

    "firebase": [
        "Firebase Developer"
    ],

    "machine learning": [
        "Machine Learning Engineer",
        "AI Engineer",
        "Data Scientist"
    ],

    "deep learning": [
        "Deep Learning Engineer",
        "AI Researcher"
    ],

    "tensorflow": [
        "AI Engineer",
        "Machine Learning Engineer"
    ],

    "sql": [
        "Database Developer",
        "Data Analyst"
    ],

    "data analysis": [
        "Data Analyst",
        "Business Analyst"
    ],

    "html": [
        "Frontend Developer"
    ],

    "css": [
        "Frontend Developer"
    ],

    "javascript": [
        "Frontend Developer",
        "Full Stack Developer"
    ],

    "react": [
        "React Developer",
        "Frontend Developer"
    ],

    "c++": [
        "Software Engineer"
    ]
}

# =====================================
# Career Recommendation Mapping
# =====================================

CAREER_MAPPING = {

    "python": "Software Development",

    "java": "Software Development",

    "flutter": "Mobile App Development",

    "dart": "Mobile App Development",

    "firebase": "Mobile App Development",

    "machine learning": "Artificial Intelligence",

    "deep learning": "Artificial Intelligence",

    "tensorflow": "Artificial Intelligence",

    "sql": "Data Science",

    "data analysis": "Data Science",

    "html": "Web Development",

    "css": "Web Development",

    "javascript": "Web Development",

    "react": "Web Development",

    "c++": "Software Engineering"
}


# =====================================
# Extract Skills
# =====================================

def extract_skills(text):

    text = text.lower()

    found_skills = []

    for skill in skills_list:
        if skill in text:
            found_skills.append(skill)

    return found_skills


# =====================================
# ATS Score
# =====================================

def calculate_ats_score(
        resume_text,
        matched_skills,
        job_skills
):

    ats_score = 0
    checks = []

    # Skill Score (40 Marks)

    if len(job_skills) > 0:

        skill_score = (
                              len(matched_skills)
                              / len(job_skills)
                      ) * 40

        ats_score += skill_score

    # Education

    if "education" in resume_text.lower():
        ats_score += 10
        checks.append("Education Section Found")

    # Experience

    if "experience" in resume_text.lower():
        ats_score += 10
        checks.append("Experience Section Found")

    # Projects

    if "project" in resume_text.lower():
        ats_score += 10
        checks.append("Projects Section Found")

    # Email

    email_pattern = r"\S+@\S+"

    if re.search(email_pattern, resume_text):
        ats_score += 10
        checks.append("Email Found")

    # Phone

    phone_pattern = r"\d{10}"

    if re.search(phone_pattern, resume_text):
        ats_score += 10
        checks.append("Phone Number Found")

    # Resume Length

    words = resume_text.split()

    if 100 <= len(words) <= 1000:
        ats_score += 10
        checks.append("Resume Length Good")

    return round(ats_score, 2), checks


# =====================================
# Resume Matching
# =====================================

def calculate_match(resume_text, job_description):

    vectorizer = TfidfVectorizer()

    vectors = vectorizer.fit_transform([
        resume_text,
        job_description
    ])

    similarity = cosine_similarity(vectors)

    match_percentage = similarity[0][1] * 100

    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)

    matched_skills = list(
        set(resume_skills) &
        set(job_skills)
    )

    missing_skills = list(
        set(job_skills) -
        set(resume_skills)
    )

    # Resume Score

    if len(job_skills) > 0:

        resume_score = (
                               len(matched_skills)
                               / len(job_skills)
                       ) * 100

    else:

        resume_score = 0

    # Recommendations

    recommendations = [
        f"Learn {skill}"
        for skill in missing_skills
    ]

    # Recommended Jobs

    recommended_jobs = []

    source_skills = (
        resume_skills
        if resume_skills
        else missing_skills
    )

    for skill in source_skills:

        if skill in JOB_MAPPING:
            recommended_jobs.extend(
                JOB_MAPPING[skill]
            )

    recommended_jobs = sorted(
        list(set(recommended_jobs))
    )

    # Recommended Careers

    recommended_careers = []

    for skill in source_skills:

        if skill in CAREER_MAPPING:
            recommended_careers.append(
                CAREER_MAPPING[skill]
            )

    recommended_careers = sorted(
        list(set(recommended_careers))
    )

    # Summary

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

    # ATS Score

    ats_score, ats_checks = calculate_ats_score(
        resume_text,
        matched_skills,
        job_skills
    )

    return {

        "match_percentage": round(
            match_percentage,
            2
        ),

        "resume_score": round(
            resume_score,
            2
        ),

        "matched_skills": matched_skills,

        "missing_skills": missing_skills,

        "recommendations": recommendations,

        "summary": summary,

        "ats_score": ats_score,

        "ats_checks": ats_checks,

        "recommended_jobs": recommended_jobs,

        "recommended_careers": recommended_careers
    }