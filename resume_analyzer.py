# ============================================================
#   AI Resume Analyzer
#   Evaluates resumes against job descriptions
#   Supports: PDF upload + Text input | CLI + Web App
# ============================================================

# ── STEP 1: Install & Import Libraries ───────────────────────
# Run in terminal before use:
#   pip install pypdf scikit-learn nltk pandas numpy flask

import re
import string
import os
import json
from collections import Counter

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download NLTK resources
print("📥 Downloading NLTK resources...")
for pkg in ['stopwords', 'punkt', 'punkt_tab', 'wordnet', 'omw-1.4']:
    nltk.download(pkg, quiet=True)
print("✅ Ready.\n")

# ── STEP 2: PDF Text Extraction ──────────────────────────────

def extract_text_from_pdf(pdf_path):
    """
    Extract raw text from a PDF resume file.

    Parameters:
        pdf_path : str — path to the PDF file

    Returns:
        str — extracted text content
    """
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        if not text.strip():
            raise ValueError("PDF appears to be empty or scanned (no extractable text).")
        return text
    except ImportError:
        raise ImportError("pypdf not installed. Run: pip install pypdf")


# ── STEP 3: Text Preprocessing ───────────────────────────────

lemmatizer = WordNetLemmatizer()
stop_words  = set(stopwords.words('english'))

def preprocess(text):
    """Clean and normalize text for NLP analysis."""
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", " ", text)          # Remove URLs
    text = re.sub(r"[%s]" % re.escape(string.punctuation), " ", text)  # Remove punctuation
    text = re.sub(r"\d+", " ", text)                       # Remove numbers
    text = re.sub(r"\s+", " ", text).strip()               # Normalize whitespace
    tokens = word_tokenize(text)
    tokens = [lemmatizer.lemmatize(t) for t in tokens
              if t not in stop_words and len(t) > 2]
    return " ".join(tokens)


# ── STEP 4: Keyword Extraction ───────────────────────────────

# Curated list of technical & professional keywords
TECH_KEYWORDS = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go",
    "swift", "kotlin", "r", "scala", "php", "rust", "matlab",
    # Web & Frameworks
    "react", "angular", "vue", "nodejs", "django", "flask", "fastapi",
    "spring", "html", "css", "rest", "graphql", "api",
    # Data & ML
    "machine learning", "deep learning", "nlp", "tensorflow", "pytorch",
    "keras", "scikit-learn", "pandas", "numpy", "sql", "mysql", "postgresql",
    "mongodb", "data analysis", "data science", "power bi", "tableau",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "git", "github",
    "linux", "devops", "terraform", "jenkins",
    # Soft Skills
    "leadership", "communication", "teamwork", "problem solving",
    "project management", "agile", "scrum", "collaboration",
    # Business
    "excel", "powerpoint", "jira", "confluence", "salesforce", "sap",
}

def extract_keywords(text):
    """Extract relevant keywords from text using the curated keyword list."""
    text_lower = text.lower()
    found = set()
    for kw in TECH_KEYWORDS:
        if kw in text_lower:
            found.add(kw)
    return found


def extract_top_words(text, n=20):
    """Extract top N most frequent meaningful words from text."""
    cleaned = preprocess(text)
    words = cleaned.split()
    freq  = Counter(words)
    return [word for word, _ in freq.most_common(n)]


# ── STEP 5: Match Score Calculation ──────────────────────────

def calculate_match_score(resume_text, jd_text):
    """
    Calculate semantic similarity between resume and job description
    using TF-IDF cosine similarity.

    Returns:
        float — match score between 0 and 100
    """
    vectorizer = TfidfVectorizer()
    cleaned_resume = preprocess(resume_text)
    cleaned_jd     = preprocess(jd_text)

    tfidf_matrix = vectorizer.fit_transform([cleaned_resume, cleaned_jd])
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(score * 100, 2)


# ── STEP 6: Gap Analysis ─────────────────────────────────────

def analyze_gaps(resume_text, jd_text):
    """
    Identify keywords present in the JD but missing from the resume.

    Returns:
        dict with matched and missing keyword sets
    """
    resume_kws = extract_keywords(resume_text)
    jd_kws     = extract_keywords(jd_text)

    matched = resume_kws & jd_kws
    missing = jd_kws - resume_kws

    return {
        "jd_keywords"     : sorted(jd_kws),
        "resume_keywords" : sorted(resume_kws),
        "matched_keywords": sorted(matched),
        "missing_keywords": sorted(missing),
    }


# ── STEP 7: Feedback Generator ───────────────────────────────

def generate_feedback(score, gap_analysis, resume_text):
    """
    Generate actionable, prioritized improvement suggestions
    based on match score and keyword gaps.

    Returns:
        list of feedback strings
    """
    feedback = []
    missing  = gap_analysis["missing_keywords"]
    matched  = gap_analysis["matched_keywords"]

    # ── Score-based feedback ──
    if score >= 80:
        feedback.append("✅ Excellent match! Your resume aligns strongly with this job.")
    elif score >= 60:
        feedback.append("🟡 Good match. A few targeted improvements can boost your chances.")
    elif score >= 40:
        feedback.append("🟠 Moderate match. Consider tailoring your resume more to this role.")
    else:
        feedback.append("🔴 Low match. Your resume needs significant alignment with this JD.")

    # ── Missing keywords ──
    if missing:
        top_missing = missing[:8]
        feedback.append(
            f"📌 Add these missing keywords from the JD: "
            f"{', '.join(top_missing)}"
            + (" and more." if len(missing) > 8 else ".")
        )

    # ── Matched keywords ──
    if matched:
        feedback.append(
            f"✅ Good: Your resume already contains these relevant skills: "
            f"{', '.join(list(matched)[:6])}."
        )

    # ── Resume content checks ──
    resume_lower = resume_text.lower()

    # Quantifiable achievements
    has_numbers = bool(re.search(r'\d+\s*(%|percent|million|k\b|years|months|projects|users|clients)', resume_lower))
    if not has_numbers:
        feedback.append(
            "📊 Add measurable achievements (e.g., 'Increased sales by 30%', "
            "'Managed a team of 10', 'Reduced load time by 2 seconds')."
        )

    # Action verbs
    action_verbs = ["developed", "built", "designed", "led", "managed", "implemented",
                    "created", "improved", "achieved", "delivered", "launched", "optimized"]
    found_verbs = [v for v in action_verbs if v in resume_lower]
    if len(found_verbs) < 3:
        feedback.append(
            "💪 Use strong action verbs to start bullet points: "
            "e.g., 'Developed', 'Led', 'Optimized', 'Delivered', 'Launched'."
        )

    # Resume length check
    word_count = len(resume_text.split())
    if word_count < 200:
        feedback.append(
            f"📝 Resume seems short ({word_count} words). "
            "Aim for 400–700 words covering experience, skills, and achievements."
        )
    elif word_count > 900:
        feedback.append(
            f"✂️  Resume may be too long ({word_count} words). "
            "Keep it concise — ideally 1–2 pages for most roles."
        )

    # Education section
    if not any(kw in resume_lower for kw in ["bachelor", "master", "b.sc", "m.sc", "degree", "university", "college"]):
        feedback.append(
            "🎓 Consider adding an Education section with your degree, institution, and graduation year."
        )

    # Contact information
    has_email = bool(re.search(r'[\w.+-]+@[\w-]+\.[a-z]{2,}', resume_lower))
    has_phone = bool(re.search(r'(\+?\d[\d\s\-]{8,})', resume_text))
    if not has_email:
        feedback.append("📧 Add your email address to the contact section.")
    if not has_phone:
        feedback.append("📞 Add your phone number to the contact section.")

    # LinkedIn / GitHub
    if "linkedin" not in resume_lower:
        feedback.append("🔗 Add your LinkedIn profile URL to improve credibility.")
    if any(kw in gap_analysis["jd_keywords"] for kw in ["github", "git", "open source"]):
        if "github" not in resume_lower:
            feedback.append("💻 This role values GitHub — add your GitHub profile link.")

    # Summary section
    if not any(kw in resume_lower for kw in ["summary", "objective", "profile", "about"]):
        feedback.append(
            "📋 Add a 2–3 sentence Professional Summary at the top "
            "highlighting your key strengths and career goal."
        )

    return feedback


# ── STEP 8: Full Analysis Pipeline ───────────────────────────

def analyze_resume(resume_text, job_description):
    """
    Full resume analysis pipeline.

    Parameters:
        resume_text     : str — raw resume text
        job_description : str — job description or role

    Returns:
        dict — full analysis report
    """
    if not resume_text.strip():
        raise ValueError("Resume text is empty.")
    if not job_description.strip():
        raise ValueError("Job description is empty.")

    score        = calculate_match_score(resume_text, job_description)
    gap_analysis = analyze_gaps(resume_text, job_description)
    feedback     = generate_feedback(score, gap_analysis, resume_text)
    top_jd_words = extract_top_words(job_description, n=10)

    # Score label
    if score >= 80:
        label = "Excellent"
    elif score >= 60:
        label = "Good"
    elif score >= 40:
        label = "Moderate"
    else:
        label = "Low"

    return {
        "match_score"      : score,
        "score_label"      : label,
        "jd_keywords"      : gap_analysis["jd_keywords"],
        "resume_keywords"  : gap_analysis["resume_keywords"],
        "matched_keywords" : gap_analysis["matched_keywords"],
        "missing_keywords" : gap_analysis["missing_keywords"],
        "top_jd_topics"    : top_jd_words,
        "feedback"         : feedback,
        "word_count"       : len(resume_text.split()),
    }


# ── STEP 9: CLI Report Printer ────────────────────────────────

def print_report(report):
    """Print a formatted analysis report to the terminal."""
    bar_filled = int(report["match_score"] / 5)
    bar = "█" * bar_filled + "░" * (20 - bar_filled)

    print("\n" + "=" * 60)
    print("        🤖 AI RESUME ANALYZER — REPORT")
    print("=" * 60)

    print(f"\n📊 MATCH SCORE:  {report['match_score']}% — {report['score_label']}")
    print(f"   [{bar}]")

    print(f"\n📄 Resume Word Count : {report['word_count']}")

    print(f"\n🔑 JD Keywords Detected     : {len(report['jd_keywords'])}")
    print(f"   {', '.join(report['jd_keywords'][:10]) or 'None found'}")

    print(f"\n✅ Matched Keywords ({len(report['matched_keywords'])}) :")
    print(f"   {', '.join(report['matched_keywords']) or 'None'}")

    print(f"\n❌ Missing Keywords ({len(report['missing_keywords'])}) :")
    print(f"   {', '.join(report['missing_keywords']) or 'None — great coverage!'}")

    print(f"\n💡 IMPROVEMENT SUGGESTIONS:")
    for i, tip in enumerate(report['feedback'], 1):
        print(f"   {i}. {tip}")

    print("\n" + "=" * 60)


# ── STEP 10: CLI Entry Point ──────────────────────────────────

def run_cli():
    """Run the analyzer interactively from the command line."""
    print("\n" + "=" * 60)
    print("        🤖 AI RESUME ANALYZER — CLI MODE")
    print("=" * 60)
    print("Options:")
    print("  1. Paste resume as text")
    print("  2. Load resume from PDF file")
    choice = input("\nChoose input method (1 or 2): ").strip()

    resume_text = ""

    if choice == "2":
        pdf_path = input("Enter path to PDF file (e.g., resume.pdf): ").strip()
        if not os.path.exists(pdf_path):
            print("❌ File not found.")
            return
        print("📄 Extracting text from PDF...")
        resume_text = extract_text_from_pdf(pdf_path)
        print(f"✅ Extracted {len(resume_text.split())} words from PDF.")
    else:
        print("\nPaste your resume text below.")
        print("When done, type 'END' on a new line and press Enter:")
        lines = []
        while True:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
        resume_text = "\n".join(lines)

    print("\nPaste the Job Description below.")
    print("When done, type 'END' on a new line and press Enter:")
    jd_lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        jd_lines.append(line)
    job_description = "\n".join(jd_lines)

    print("\n⏳ Analyzing resume...")
    report = analyze_resume(resume_text, job_description)
    print_report(report)

    # Save JSON report
    with open("resume_analysis_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("💾 Full report saved to: resume_analysis_report.json")


# ── STEP 11: Demo Mode (Quick Test) ──────────────────────────

def run_demo():
    """Run a quick demo with built-in sample data."""
    sample_resume = """
    John Doe | john.doe@email.com | +1-555-0100 | linkedin.com/in/johndoe

    PROFESSIONAL SUMMARY
    Results-driven Software Engineer with 3 years of experience in Python,
    machine learning, and data analysis. Passionate about building scalable
    AI solutions and delivering measurable business impact.

    SKILLS
    Python, TensorFlow, Scikit-learn, Pandas, NumPy, SQL, Git, Docker,
    REST APIs, Flask, Data Analysis, Machine Learning, Deep Learning

    EXPERIENCE
    Software Engineer — TechCorp (2021–Present)
    • Developed a machine learning pipeline that improved prediction accuracy by 25%
    • Built REST APIs using Flask serving 10,000+ daily requests
    • Reduced data processing time by 40% through SQL query optimization
    • Collaborated with a team of 8 engineers in an agile environment

    Junior Developer — StartupXYZ (2020–2021)
    • Implemented data analysis dashboards using Pandas and Matplotlib
    • Maintained Python scripts for ETL processes

    EDUCATION
    B.Sc. Computer Science — State University, 2020

    PROJECTS
    • Resume Analyzer: NLP-based tool to match resumes to job descriptions
    • Stock Predictor: LSTM model for time-series forecasting
    """

    sample_jd = """
    We are looking for a Senior Data Scientist to join our AI team.

    Requirements:
    - 3+ years experience in Python, machine learning, and deep learning
    - Proficiency in TensorFlow, PyTorch, and Scikit-learn
    - Strong SQL and data analysis skills
    - Experience with AWS or Azure cloud platforms
    - Knowledge of NLP and computer vision
    - Experience with Docker and Kubernetes
    - Excellent communication and leadership skills
    - Agile/Scrum experience preferred
    - GitHub portfolio demonstrating projects
    """

    print("🚀 Running demo analysis...")
    report = analyze_resume(sample_resume, sample_jd)
    print_report(report)
    return report


# ── Main ──────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_demo()
    else:
        run_cli()
