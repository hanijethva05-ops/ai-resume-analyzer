import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from pypdf import PdfReader
from docx import Document
from io import BytesIO
import os
import re


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "analysis_done": False,
    "resume_text": "",
    "job_description": "",

    "resume_skills": [],
    "job_skills": [],
    "matched_skills": [],
    "missing_skills": [],

    "matched_keywords": [],
    "missing_keywords": [],

    "match_score": 0,

    "ai_result": "",
    "action_result": "",

    "history": []
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# LOAD CSS
# =========================================================

def load_css():

    try:

        with open(
            "style.css",
            "r",
            encoding="utf-8"
        ) as f:

            css = f.read()

        st.markdown(
            f"<style>{css}</style>",
            unsafe_allow_html=True
        )

    except FileNotFoundError:

        st.warning(
            "style.css file was not found. "
            "The application will run with default Streamlit styling."
        )


load_css()


# =========================================================
# FILE EXTRACTION
# =========================================================

def extract_pdf_text(file):

    reader = PdfReader(file)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def extract_docx_text(file):

    document = Document(file)

    text = ""

    for paragraph in document.paragraphs:

        text += paragraph.text + "\n"

    return text


# =========================================================
# SKILLS DATABASE
# =========================================================

skills_database = [

    "Python",
    "SQL",
    "Excel",
    "Power BI",
    "Tableau",

    "Machine Learning",
    "Deep Learning",
    "Data Analysis",
    "Data Science",

    "Java",
    "C++",
    "HTML",
    "CSS",
    "JavaScript",
    "React",

    "Git",
    "GitHub",

    "AWS",
    "Azure",

    "Communication",
    "Problem Solving",

    "Data Modeling",
    "Statistics",

    "MySQL",
    "PostgreSQL",
    "MongoDB",

    "Pandas",
    "NumPy",
    "Matplotlib",
    "Seaborn"

]


# =========================================================
# DETECT SKILLS
# =========================================================

def detect_skills(text):

    detected_skills = []

    text_lower = text.lower()

    for skill in skills_database:

        if skill.lower() in text_lower:

            detected_skills.append(skill)

    return detected_skills


# =========================================================
# ATS KEYWORD DETECTION
# =========================================================

def detect_keywords(
    resume_text,
    job_description
):

    resume_lower = resume_text.lower()

    job_lower = job_description.lower()

    words = re.findall(
        r"\b[a-zA-Z][a-zA-Z+#.-]{3,}\b",
        job_lower
    )

    stop_words = {

        "about",
        "above",
        "after",
        "again",
        "also",
        "and",
        "are",
        "been",
        "being",
        "below",
        "between",
        "both",
        "can",
        "could",
        "from",
        "have",
        "having",
        "into",
        "more",
        "most",
        "must",
        "other",
        "our",
        "ours",
        "should",
        "some",
        "such",
        "than",
        "that",
        "their",
        "there",
        "these",
        "they",
        "this",
        "those",
        "through",
        "using",
        "very",
        "what",
        "when",
        "where",
        "which",
        "while",
        "will",
        "with",
        "would",
        "your",

        "years",
        "year",
        "role",
        "roles",
        "work",
        "working",
        "job",
        "jobs",
        "candidate",
        "candidates",
        "looking",
        "responsibilities",
        "requirements",
        "required",
        "preferred",
        "skills",
        "skill",
        "experience"
    }

    unique_words = []

    for word in words:

        word = word.strip(
            ".,:;()[]{}!?\"'"
        )

        if (
            len(word) >= 4
            and word not in stop_words
            and word not in unique_words
        ):

            unique_words.append(word)

    matched_keywords = []
    missing_keywords = []

    for keyword in unique_words[:40]:

        if keyword in resume_lower:

            matched_keywords.append(keyword)

        else:

            missing_keywords.append(keyword)

    return (
        matched_keywords,
        missing_keywords
    )


# =========================================================
# AI ANALYSIS
# =========================================================

def get_ai_analysis(
    resume_text,
    job_description
):

    if client is None:

        return (
            "OpenAI API key was not found. "
            "Please check your .env file."
        )

    prompt = f"""
You are an expert ATS resume analyst and career coach.

Analyze the candidate's resume against the target job description.

RESUME:
{resume_text[:12000]}

JOB DESCRIPTION:
{job_description[:10000]}

Give a professional but beginner-friendly analysis.

Use these sections:

## Overall Assessment

## Strong Matching Skills

## Missing or Weak Skills

## ATS Keyword Gaps

## Resume Improvement Suggestions

## Recommended Projects

## Interview Preparation

## Personalized Action Plan

Give the candidate 5 specific and practical actions
they should take to improve their chances for this job.

Prioritize the actions based on:

- Missing skills
- ATS keyword gaps
- Resume weaknesses
- Job requirements

For each action explain:

- What to improve
- Why it matters
- How the candidate can improve it

Do not invent experience, education, skills,
achievements, certifications or projects.
"""

    response = client.responses.create(
        model="gpt-6-luna",
        input=prompt
    )

    return response.output_text


# =========================================================
# QUICK ACTIONS
# =========================================================

def get_quick_action(
    action,
    resume_text,
    job_description
):

    if client is None:

        return "OpenAI API key was not found."

    if action == "tailor":

        prompt = f"""
You are an expert ATS resume writer.

Improve the candidate's resume for the target job.

IMPORTANT:
Do not invent experience, education,
projects, certifications or achievements.

Only improve wording, structure,
keyword alignment and presentation.

RESUME:
{resume_text[:12000]}

JOB DESCRIPTION:
{job_description[:10000]}

Provide:

# Tailored Resume

## Professional Summary

## Core Skills

## Improved Project Descriptions

## Improved Experience Bullet Points

## ATS Keywords to Include

## Final Resume Improvement Notes
"""

    else:

        prompt = f"""
You are an expert career coach.

Create a professional job application cover letter.

Do not invent experience, education,
projects, certifications or achievements.

RESUME:
{resume_text[:12000]}

JOB DESCRIPTION:
{job_description[:10000]}

Make it:

- Professional
- Concise
- ATS-friendly
- Suitable for a fresher/job applicant
- Specific to the target role

Use:

# Cover Letter

Dear Hiring Manager,

[Cover letter]

Sincerely,
[Candidate Name]
"""

    response = client.responses.create(
        model="gpt-6-luna",
        input=prompt
    )

    return response.output_text


# =========================================================
# CREATE DOCX REPORT
# =========================================================

def create_analysis_docx():

    document = Document()

    document.add_heading(
        "AI Resume Analysis Report",
        level=0
    )

    document.add_paragraph(
        "Generated by AI Resume Analyzer"
    )

    # Match Score

    document.add_heading(
        "Resume Match Score",
        level=1
    )

    document.add_paragraph(
        f"Overall Match: "
        f"{st.session_state.match_score:.0f}%"
    )

    # Matching Skills

    document.add_heading(
        "Matching Skills",
        level=1
    )

    if st.session_state.matched_skills:

        for skill in st.session_state.matched_skills:

            document.add_paragraph(
                skill,
                style="List Bullet"
            )

    else:

        document.add_paragraph(
            "No matching skills detected."
        )

    # Missing Skills

    document.add_heading(
        "Missing / Weak Skills",
        level=1
    )

    if st.session_state.missing_skills:

        for skill in st.session_state.missing_skills:

            document.add_paragraph(
                skill,
                style="List Bullet"
            )

    else:

        document.add_paragraph(
            "No major missing skills detected."
        )

    # ATS Keywords

    document.add_heading(
        "ATS Keywords Found",
        level=1
    )

    if st.session_state.matched_keywords:

        for keyword in st.session_state.matched_keywords:

            document.add_paragraph(
                keyword,
                style="List Bullet"
            )

    else:

        document.add_paragraph(
            "No important matching keywords detected."
        )

    # Missing Keywords

    document.add_heading(
        "ATS Keywords Missing",
        level=1
    )

    if st.session_state.missing_keywords:

        for keyword in st.session_state.missing_keywords:

            document.add_paragraph(
                keyword,
                style="List Bullet"
            )

    else:

        document.add_paragraph(
            "No major keyword gaps detected."
        )

    # AI Analysis

    document.add_heading(
        "AI Resume Analysis",
        level=1
    )

    document.add_paragraph(
        st.session_state.ai_result
    )

    # Quick Action Result

    if st.session_state.action_result:

        document.add_heading(
            "AI Generated Result",
            level=1
        )

        document.add_paragraph(
            st.session_state.action_result
        )

    file_stream = BytesIO()

    document.save(file_stream)

    file_stream.seek(0)

    return file_stream


# =========================================================
# RESET
# =========================================================

def reset_analysis():

    st.session_state.analysis_done = False

    st.session_state.resume_text = ""

    st.session_state.job_description = ""

    st.session_state.resume_skills = []

    st.session_state.job_skills = []

    st.session_state.matched_skills = []

    st.session_state.missing_skills = []

    st.session_state.matched_keywords = []

    st.session_state.missing_keywords = []

    st.session_state.match_score = 0

    st.session_state.ai_result = ""

    st.session_state.action_result = ""


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("📄 AI Resume Analyzer")

    st.caption(
        "Smart Resume Analysis & ATS Matching"
    )

    st.divider()

    if st.button(
        "＋ New Analysis",
        use_container_width=True
    ):

        reset_analysis()

        st.rerun()

    st.divider()

    st.subheader("📌 Saved Roles")

    st.caption("📊 Data Analyst")
    st.caption("💻 Web Developer")
    st.caption("📈 MIS Analyst")
    st.caption("📣 Digital Marketing")

    st.divider()

    st.subheader("📜 Analysis History")

    if st.session_state.history:

        for item in st.session_state.history[-5:]:

            st.caption(
                "📄 " + item
            )

    else:

        st.caption(
            "No previous analyses yet."
        )

    st.divider()

    st.subheader("⚙️ Settings")

    if api_key:

        st.success(
            "🔑 API Status: Active"
        )

    else:

        st.error(
            "⚠️ API Key Not Found"
        )


# =========================================================
# HEADER
# =========================================================

st.title(
    "📄 AI Resume Analyzer"
)

st.subheader(
    "Smart Resume Analysis • ATS Job Matching • AI Career Insights"
)

st.write(
    "Upload your resume and compare it with a target job "
    "description using skill matching and AI-powered analysis."
)

st.divider()


# =========================================================
# MAIN COLUMNS
# =========================================================

left_col, right_col = st.columns(
    [0.95, 1.05],
    gap="large"
)


# =========================================================
# LEFT COLUMN
# =========================================================

with left_col:

    st.header(
        "📂 Resume & Job Input"
    )

    st.caption(
        "Upload your resume and paste the target job description."
    )

    st.subheader(
        "📄 Upload Resume"
    )

    st.caption(
        "Supported formats: PDF / DOCX"
    )

    resume_file = st.file_uploader(
        "Choose your resume",
        type=["pdf", "docx"]
    )

    if resume_file:

        st.success(
            f"Uploaded: {resume_file.name}"
        )

    st.subheader(
        "📝 Job Description"
    )

    st.caption(
        "Paste the target job requirements and responsibilities."
    )

    job_description = st.text_area(
        "Job Description",
        height=300,
        placeholder=(
            "Example:\n\n"
            "We are looking for a Data Analyst.\n\n"
            "Required skills:\n"
            "Python\n"
            "SQL\n"
            "Excel\n"
            "Power BI\n"
            "Tableau\n"
            "Data Analysis\n"
            "Communication\n\n"
            "Responsibilities:\n"
            "Analyze business data...\n"
            "Create dashboards...\n"
            "Prepare reports..."
        )
    )

    st.write("")

    analyze_button = st.button(
        "✨ Run AI ATS Analysis",
        type="primary",
        use_container_width=True
    )


# =========================================================
# ANALYSIS
# =========================================================

if analyze_button:

    if resume_file is None:

        st.error(
            "📄 Please upload your resume first."
        )

    elif not job_description.strip():

        st.error(
            "📝 Please enter the job description."
        )

    else:

        with st.spinner(
            "🤖 Analyzing your resume..."
        ):

            try:

                # -----------------------------------------
                # EXTRACT RESUME
                # -----------------------------------------

                if resume_file.name.lower().endswith(".pdf"):

                    resume_text = extract_pdf_text(
                        resume_file
                    )

                else:

                    resume_text = extract_docx_text(
                        resume_file
                    )

                if not resume_text.strip():

                    st.error(
                        "Could not extract text from this resume."
                    )

                else:

                    # -------------------------------------
                    # SKILLS
                    # -------------------------------------

                    resume_skills = detect_skills(
                        resume_text
                    )

                    job_skills = detect_skills(
                        job_description
                    )

                    matched_skills = []

                    missing_skills = []

                    for skill in job_skills:

                        if skill in resume_skills:

                            matched_skills.append(
                                skill
                            )

                        else:

                            missing_skills.append(
                                skill
                            )

                    # -------------------------------------
                    # KEYWORDS
                    # -------------------------------------

                    (
                        matched_keywords,
                        missing_keywords
                    ) = detect_keywords(
                        resume_text,
                        job_description
                    )

                    # -------------------------------------
                    # SCORE
                    # -------------------------------------

                    if job_skills:

                        match_score = (
                            len(matched_skills)
                            /
                            len(job_skills)
                        ) * 100

                    else:

                        match_score = 0

                    # -------------------------------------
                    # AI ANALYSIS
                    # -------------------------------------

                    if client:

                        ai_result = get_ai_analysis(
                            resume_text,
                            job_description
                        )

                    else:

                        ai_result = (
                            "AI analysis unavailable because "
                            "the OpenAI API key was not found."
                        )

                    # -------------------------------------
                    # SAVE RESULTS
                    # -------------------------------------

                    st.session_state.analysis_done = True

                    st.session_state.resume_text = (
                        resume_text
                    )

                    st.session_state.job_description = (
                        job_description
                    )

                    st.session_state.resume_skills = (
                        resume_skills
                    )

                    st.session_state.job_skills = (
                        job_skills
                    )

                    st.session_state.matched_skills = (
                        matched_skills
                    )

                    st.session_state.missing_skills = (
                        missing_skills
                    )

                    st.session_state.matched_keywords = (
                        matched_keywords
                    )

                    st.session_state.missing_keywords = (
                        missing_keywords
                    )

                    st.session_state.match_score = (
                        match_score
                    )

                    st.session_state.ai_result = (
                        ai_result
                    )

                    st.session_state.action_result = ""

                    # -------------------------------------
                    # HISTORY
                    # -------------------------------------

                    if job_skills:

                        role_name = " • ".join(
                            job_skills[:3]
                        )

                    else:

                        role_name = "Job Analysis"

                    history_item = (
                        f"{role_name} — "
                        f"{match_score:.0f}% Match"
                    )

                    if history_item not in (
                        st.session_state.history
                    ):

                        st.session_state.history.append(
                            history_item
                        )

                    st.success(
                        "✅ Resume analysis completed."
                    )

            except Exception as e:

                st.error(
                    "❌ Something went wrong during analysis."
                )

                st.code(
                    str(e)
                )


# =========================================================
# RIGHT COLUMN
# =========================================================

with right_col:

    st.header(
        "🤖 AI Match & ATS Insights"
    )

    st.caption(
        "Your resume match score, ATS compatibility and AI insights."
    )

    # =====================================================
    # EMPTY STATE
    # =====================================================

    if not st.session_state.analysis_done:

        st.info(
            """
            🤖 **AI Insights will appear here**

            Upload your resume, paste the job description,
            and click **Run AI ATS Analysis**.
            """
        )

    # =====================================================
    # RESULTS
    # =====================================================

    else:

        score = st.session_state.match_score

        # =================================================
        # ATS STATUS
        # =================================================

        if score >= 80:

            ats_status = "🟢 High Match"

        elif score >= 50:

            ats_status = "🟡 Moderate Match"

        else:

            ats_status = "🔴 Low Match"

        # =================================================
        # TOP METRICS
        # =================================================

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "🎯 Match Score",
                f"{score:.0f}%"
            )

        with col2:

            st.metric(
                "✅ Matched Skills",
                len(
                    st.session_state.matched_skills
                )
            )

        with col3:

            st.metric(
                "❌ Missing Skills",
                len(
                    st.session_state.missing_skills
                )
            )

        st.write("")

        st.success(
            f"ATS Readiness: {ats_status}"
        )

        # =================================================
        # PROFESSIONAL MATCH SCORE
        # =================================================

        st.subheader(
            "📈 Resume Match Strength"
        )

        score_value = int(
            st.session_state.match_score
        )

        if score_value >= 80:

            score_message = (
                "Excellent match! Your resume is highly relevant to this job."
            )

        elif score_value >= 60:

            score_message = (
                "Good match! A few improvements can make your resume stronger."
            )

        elif score_value >= 40:

            score_message = (
                "Moderate match. Consider adding relevant skills and keywords."
            )

        else:

            score_message = (
                "Low match. Your resume needs more alignment with this job."
            )

        st.progress(
            min(score_value, 100) / 100
        )

        st.caption(
            f"{score_value}% Match — {score_message}"
        )

        # =================================================
        # SKILL BREAKDOWN
        # =================================================

        st.subheader(
            "📊 Skill Breakdown"
        )

        total_job_skills = len(
            st.session_state.job_skills
        )

        matched_count = len(
            st.session_state.matched_skills
        )

        missing_count = len(
            st.session_state.missing_skills
        )

        if total_job_skills > 0:

            skill_match_percentage = (
                matched_count
                /
                total_job_skills
            ) * 100

        else:

            skill_match_percentage = 0

        # =================================================
        # SKILL METRICS
        # =================================================

        skill_metric1, skill_metric2, skill_metric3, skill_metric4 = st.columns(4)

        with skill_metric1:

            st.metric(
                "🎯 Job Skills",
                total_job_skills
            )

        with skill_metric2:

            st.metric(
                "✅ Matched",
                matched_count
            )

        with skill_metric3:

            st.metric(
                "❌ Missing",
                missing_count
            )

        with skill_metric4:

            st.metric(
                "📈 Skill Match",
                f"{skill_match_percentage:.0f}%"
            )

        st.write("")

        st.caption(
            "Overall Skill Alignment"
        )

        st.progress(
            min(skill_match_percentage, 100) / 100
        )

        # =================================================
        # MATCHING + MISSING SKILLS
        # =================================================

        skill_col1, skill_col2 = st.columns(2)

        with skill_col1:

            st.markdown(
                "### ✅ Matching Skills"
            )

            if st.session_state.matched_skills:

                for skill in (
                    st.session_state.matched_skills
                ):

                    st.success(
                        skill,
                        icon="✅"
                    )

            else:

                st.info(
                    "No matching skills detected."
                )

        with skill_col2:

            st.markdown(
                "### ❌ Missing / Weak Skills"
            )

            if st.session_state.missing_skills:

                for skill in (
                    st.session_state.missing_skills
                ):

                    st.error(
                        skill,
                        icon="⚠️"
                    )

            else:

                st.success(
                    "No important missing skills detected.",
                    icon="✅"
                )

        # =================================================
        # SKILL INSIGHT
        # =================================================

        if skill_match_percentage >= 80:

            st.success(
                "🎉 Excellent skill alignment! "
                "Your resume contains most of the skills "
                "required by this job."
            )

        elif skill_match_percentage >= 60:

            st.warning(
                "👍 Good skill alignment. "
                "Adding a few missing skills can improve "
                "your job match."
            )

        elif skill_match_percentage >= 40:

            st.warning(
                "⚠️ Moderate skill alignment. "
                "Consider learning and demonstrating more "
                "of the required skills."
            )

        else:

            st.error(
                "🚨 Low skill alignment. "
                "Your resume needs significant improvement "
                "for this particular job."
            )

        # =================================================
        # AI ANALYSIS
        # =================================================

        st.divider()

        st.subheader(
            "✨ AI Resume Analysis"
        )

        with st.container(border=True):

            st.markdown(
                st.session_state.ai_result
            )

        # =================================================
        # AI ACTION PLAN
        # =================================================

        st.subheader(
            "🚀 Personalized Action Plan"
        )

        st.caption(
            "AI-generated steps to improve your resume and job match."
        )

        with st.container(border=True):

            st.markdown(
                """
                ### 🎯 What You Should Do Next

                Follow these priority recommendations based
                on the skills missing from your resume.
                """
            )

            if st.session_state.missing_skills:

                st.markdown(
                    "### 📚 Priority Skills to Improve"
                )

                for skill in (
                    st.session_state.missing_skills
                ):

                    st.warning(
                        f"Improve or demonstrate **{skill}**",
                        icon="⚠️"
                    )

            else:

                st.success(
                    "🎉 No major missing skills detected. "
                    "Focus on resume presentation and ATS keywords."
                )

        # =================================================
        # RESUME STRENGTH DASHBOARD
        # =================================================

        st.divider()

        st.subheader(
            "📊 Resume Strength Dashboard"
        )

        st.caption(
            "A quick overview of how well your resume is aligned with this job."
        )

        resume_skill_count = len(
            st.session_state.resume_skills
        )

        job_skill_count = len(
            st.session_state.job_skills
        )

        matched_skill_count = len(
            st.session_state.matched_skills
        )

        missing_skill_count = len(
            st.session_state.missing_skills
        )

        ats_score = int(
            st.session_state.match_score
        )

        # =================================================
        # ATS KEYWORD SCORE
        # =================================================

        total_keywords = (
            len(st.session_state.matched_keywords)
            +
            len(st.session_state.missing_keywords)
        )

        if total_keywords > 0:

            keyword_score = (
                len(st.session_state.matched_keywords)
                /
                total_keywords
            ) * 100

        else:

            keyword_score = 0

        # =================================================
        # OVERALL ATS SCORE
        # =================================================

        overall_ats_score = int(
            (
                ats_score * 0.70
                +
                keyword_score * 0.30
            )
        )

        # =================================================
        # SKILL COVERAGE
        # =================================================

        if job_skill_count > 0:

            skill_coverage = int(
                (
                    matched_skill_count
                    /
                    job_skill_count
                ) * 100
            )

        else:

            skill_coverage = 0

        # =================================================
        # DASHBOARD METRICS
        # =================================================

        dash1, dash2, dash3, dash4 = st.columns(4)

        with dash1:

            st.metric(
                "📄 Resume Skills",
                resume_skill_count
            )

        with dash2:

            st.metric(
                "🎯 Job Requirements",
                job_skill_count
            )

        with dash3:

            st.metric(
                "✅ Skill Coverage",
                f"{skill_coverage}%"
            )

        with dash4:

            st.metric(
                "🚀 Overall ATS Score",
                f"{overall_ats_score}%"
            )

        st.write("")

        st.caption(
            f"Skill Match: {ats_score:.0f}%  •  "
            f"Keyword Match: {keyword_score:.0f}%"
        )

        # =================================================
        # RESUME STRENGTH
        # =================================================

        st.markdown(
            "### 💪 Resume Strength"
        )

        if overall_ats_score >= 80:

            strength_label = "Excellent"

            strength_message = (
                "Your resume has strong alignment with this job."
            )

        elif overall_ats_score >= 60:

            strength_label = "Good"

            strength_message = (
                "Your resume is reasonably aligned, "
                "but some improvements are recommended."
            )

        elif overall_ats_score >= 40:

            strength_label = "Moderate"

            strength_message = (
                "Your resume needs more alignment "
                "with the target job."
            )

        else:

            strength_label = "Needs Improvement"

            strength_message = (
                "Your resume requires significant "
                "improvement for this role."
            )

        st.progress(
            min(overall_ats_score, 100) / 100
        )

        st.info(
            f"**{strength_label} Resume** — "
            f"{strength_message}"
        )

        # =================================================
        # ATS KEYWORD ANALYSIS
        # =================================================

        st.divider()

        st.subheader(
            "🔎 ATS Keyword Analysis"
        )

        st.caption(
            "Keywords found in the job description and their presence in your resume."
        )

        keyword_col1, keyword_col2 = st.columns(2)

        with keyword_col1:

            st.markdown(
                "### ✅ Keywords Found"
            )

            if st.session_state.matched_keywords:

                for keyword in (
                    st.session_state.matched_keywords
                ):

                    st.success(
                        keyword,
                        icon="✅"
                    )

            else:

                st.info(
                    "No important matching keywords detected."
                )

        with keyword_col2:

            st.markdown(
                "### ⚠️ Keywords Missing"
            )

            if st.session_state.missing_keywords:

                for keyword in (
                    st.session_state.missing_keywords
                ):

                    st.warning(
                        keyword,
                        icon="⚠️"
                    )

            else:

                st.success(
                    "Excellent! No major keyword gaps detected.",
                    icon="✅"
                )


# =========================================================
# QUICK ACTIONS
# =========================================================

if st.session_state.analysis_done:

    st.divider()

    st.header(
        "💡 Quick Actions"
    )

    st.caption(
        "Use AI to improve your application further."
    )

    action1, action2 = st.columns(2)

    with action1:

        tailor_button = st.button(
            "✨ Tailor My Resume",
            use_container_width=True
        )

    with action2:

        cover_button = st.button(
            "✉️ Generate Cover Letter",
            use_container_width=True
        )

    # =====================================================
    # TAILOR RESUME
    # =====================================================

    if tailor_button:

        if client is None:

            st.error(
                "OpenAI API key not found."
            )

        else:

            with st.spinner(
                "✨ Tailoring your resume..."
            ):

                try:

                    result = get_quick_action(
                        "tailor",
                        st.session_state.resume_text,
                        st.session_state.job_description
                    )

                    st.session_state.action_result = result

                except Exception as e:

                    st.error(
                        f"Could not tailor resume: {e}"
                    )

    # =====================================================
    # COVER LETTER
    # =====================================================

    if cover_button:

        if client is None:

            st.error(
                "OpenAI API key not found."
            )

        else:

            with st.spinner(
                "✉️ Creating your cover letter..."
            ):

                try:

                    result = get_quick_action(
                        "cover",
                        st.session_state.resume_text,
                        st.session_state.job_description
                    )

                    st.session_state.action_result = result

                except Exception as e:

                    st.error(
                        f"Could not create cover letter: {e}"
                    )

    # =====================================================
    # AI GENERATED RESULT
    # =====================================================

    if st.session_state.action_result:

        st.divider()

        st.subheader(
            "🤖 AI Generated Result"
        )

        with st.container(border=True):

            st.markdown(
                st.session_state.action_result
            )


# =========================================================
# DOWNLOAD REPORT
# =========================================================

if st.session_state.analysis_done:

    st.divider()

    st.header(
        "📥 Download Results"
    )

    st.caption(
        "Save your AI resume analysis for later use."
    )

    report_file = create_analysis_docx()

    st.download_button(
        label="📄 Download Analysis Report",
        data=report_file,
        file_name="AI_Resume_Analysis_Report.docx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
        use_container_width=True
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "📄 AI Resume Analyzer • Built with Python, Streamlit & OpenAI"
)