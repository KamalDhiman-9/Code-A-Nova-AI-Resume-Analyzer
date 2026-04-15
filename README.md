# 🤖 AI Resume Analyzer
### NLP-Powered Resume Evaluation & Job Match System

---

## 📌 Project Overview

The **AI Resume Analyzer** is an intelligent system that evaluates your resume
against any job description and provides:

- 📊 A **match score** (0–100%) based on semantic similarity
- 🔑 **Keyword gap analysis** — matched vs. missing skills
- 💡 **Actionable feedback** — specific suggestions to improve your resume
- 🌐 A **browser-based web app** with a modern UI
- 💻 A **command-line interface** for quick terminal use

---

## 📁 Project Structure

```
ai-resume-analyzer/
│
├── resume_analyzer.py     ← Core analysis engine (NLP pipeline)
├── app.py                 ← Flask web application
├── sample_resume.txt      ← Sample resume to test with
│
└── README.md              ← This file
```

---

## ⚙️ Requirements & Installation

### Python Version
Python 3.8 or higher recommended.

### Install Dependencies
```bash
pip install pypdf scikit-learn nltk pandas numpy flask
```

| Library | Purpose |
|---------|---------|
| `pypdf` | Extract text from PDF resumes |
| `scikit-learn` | TF-IDF vectorization & cosine similarity |
| `nltk` | Text preprocessing (tokenize, lemmatize, stopwords) |
| `flask` | Web application server |
| `numpy` | Numerical operations |

---

## ▶️ How to Run

### Option 1 — Web App (Recommended)
```bash
python app.py
```
Then open your browser and go to: **http://127.0.0.1:5000**

### Option 2 — Command Line
```bash
# Interactive CLI mode
python resume_analyzer.py

# Quick demo with built-in sample data
python resume_analyzer.py --demo
```

---

## 🧠 How It Works — Full Pipeline

```
  Resume Input (PDF or Text)
           │
           ▼
  ┌──────────────────────┐
  │  TEXT EXTRACTION     │
  │  • PDF parsing       │
  │  • Raw text input    │
  └────────┬─────────────┘
           │
           ▼
  ┌──────────────────────┐
  │  NLP PREPROCESSING   │
  │  • Lowercase         │
  │  • Remove noise      │
  │  • Tokenization      │
  │  • Stopword removal  │
  │  • Lemmatization     │
  └────────┬─────────────┘
           │
           ▼
  ┌──────────────────────┐
  │  FEATURE EXTRACTION  │
  │  • TF-IDF vectors    │
  │  • Keyword matching  │
  └────────┬─────────────┘
           │
           ▼
  ┌──────────────────────┐
  │  ANALYSIS ENGINE     │
  │  • Cosine similarity │
  │  • Keyword gap check │
  │  • Content checks    │
  └────────┬─────────────┘
           │
           ▼
  ┌──────────────────────┐
  │  REPORT GENERATION   │
  │  • Match score       │
  │  • Missing keywords  │
  │  • Feedback tips     │
  └──────────────────────┘
```

---

## 📊 What the System Analyzes

### 1. Match Score (0–100%)
Uses **TF-IDF cosine similarity** to measure how semantically aligned your
resume content is with the job description.

| Score | Label | Meaning |
|-------|-------|---------|
| 80–100% | Excellent | Strong alignment with the role |
| 60–79%  | Good | Good match with room to improve |
| 40–59%  | Moderate | Several gaps to address |
| 0–39%   | Low | Significant tailoring needed |

### 2. Keyword Gap Analysis
Scans for 70+ technical and professional keywords including:
- Programming languages (Python, Java, SQL...)
- ML/AI tools (TensorFlow, PyTorch, Scikit-learn...)
- Cloud platforms (AWS, Azure, GCP...)
- DevOps tools (Docker, Kubernetes, Git...)
- Soft skills (leadership, agile, communication...)

### 3. Smart Feedback Checks
| Check | What It Looks For |
|-------|------------------|
| Missing keywords | Skills in JD but absent from resume |
| Measurable achievements | Numbers, percentages, impact metrics |
| Action verbs | "Developed", "Led", "Optimized", etc. |
| Resume length | Ideal range: 400–700 words |
| Contact details | Email, phone number |
| Professional summary | 2–3 sentence intro section |
| LinkedIn/GitHub | Profile links for credibility |
| Education section | Degree and institution |

---

## 💡 Sample Feedback Examples

- *"Add these missing keywords from the JD: kubernetes, pytorch, azure"*
- *"Add measurable achievements (e.g., 'Increased sales by 30%')"*
- *"Use strong action verbs: 'Developed', 'Led', 'Optimized'"*
- *"Add a 2–3 sentence Professional Summary at the top"*
- *"Add your LinkedIn profile URL to improve credibility"*

---

## 🧪 Testing with Sample Data

A sample resume is included. To test it:

```bash
# CLI demo mode (uses built-in sample resume + JD)
python resume_analyzer.py --demo

# Or paste the contents of sample_resume.txt into the web app
```

---

## 🚀 Ideas to Extend This Project

1. **AI-Powered Suggestions** — Use OpenAI/Gemini API to rewrite weak bullet points
2. **Multi-Resume Ranking** — Rank multiple resumes for a single job
3. **ATS Simulator** — Simulate Applicant Tracking System scoring
4. **Cover Letter Generator** — Auto-generate a tailored cover letter
5. **Job Scraper** — Fetch live job descriptions from LinkedIn or Indeed
6. **Export to PDF** — Download the full analysis report as a PDF

---

## 🐛 Common Issues & Fixes

| Problem | Cause | Fix |
|---------|-------|-----|
| `ModuleNotFoundError` | Library not installed | `pip install <library>` |
| PDF text is empty | Scanned/image-based PDF | Use text-based PDF or paste text manually |
| Low match score | Resume not tailored | Add more keywords from the JD |
| Flask not found | Not installed | `pip install flask` |
| Port already in use | Another app on port 5000 | Change port in `app.py`: `app.run(port=5001)` |

---

## 📚 Key Concepts

| Concept | Explanation |
|---------|-------------|
| **TF-IDF** | Scores word importance across documents |
| **Cosine Similarity** | Measures angle between two text vectors (0=different, 1=identical) |
| **Lemmatization** | Reduces words to root form for better matching |
| **Keyword Extraction** | Identifies domain-specific technical skills in text |
| **ATS** | Applicant Tracking System — automated resume screener used by companies |

---

*Built with ❤️ using Python, NLTK, Scikit-learn, and Flask*
