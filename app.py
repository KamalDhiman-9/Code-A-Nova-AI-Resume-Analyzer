"""
AI Resume Analyzer — Web App (Flask)
Run with:  python app.py
Then open: http://127.0.0.1:5000
"""

from flask import Flask, request, jsonify, render_template_string
import os
import tempfile
from resume_analyzer import analyze_resume, extract_text_from_pdf

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max upload

# ── HTML Template ─────────────────────────────────────────────
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>AI Resume Analyzer</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Segoe UI', sans-serif;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
      min-height: 100vh; color: #e0e0e0; padding: 30px 20px;
    }
    .container { max-width: 900px; margin: 0 auto; }
    h1 {
      text-align: center; font-size: 2rem; font-weight: 700;
      background: linear-gradient(90deg, #00d4ff, #7b2ff7);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      margin-bottom: 8px;
    }
    .subtitle { text-align: center; color: #aaa; margin-bottom: 30px; font-size: 0.95rem; }
    .card {
      background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
      border-radius: 16px; padding: 28px; margin-bottom: 24px;
      backdrop-filter: blur(10px);
    }
    .card h2 { font-size: 1.1rem; margin-bottom: 16px; color: #00d4ff; }
    .tabs { display: flex; gap: 10px; margin-bottom: 16px; }
    .tab {
      padding: 8px 20px; border-radius: 8px; cursor: pointer;
      border: 1px solid rgba(255,255,255,0.15); background: transparent;
      color: #aaa; font-size: 0.9rem; transition: all 0.2s;
    }
    .tab.active { background: #00d4ff22; border-color: #00d4ff; color: #00d4ff; }
    textarea {
      width: 100%; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.15);
      border-radius: 10px; color: #e0e0e0; padding: 14px; font-size: 0.9rem;
      resize: vertical; outline: none; font-family: inherit; transition: border 0.2s;
    }
    textarea:focus { border-color: #00d4ff; }
    .upload-area {
      border: 2px dashed rgba(255,255,255,0.2); border-radius: 10px;
      padding: 30px; text-align: center; cursor: pointer;
      transition: all 0.2s; color: #aaa;
    }
    .upload-area:hover { border-color: #00d4ff; color: #00d4ff; }
    .upload-area input { display: none; }
    .upload-icon { font-size: 2rem; margin-bottom: 8px; }
    button.analyze-btn {
      width: 100%; padding: 14px; border-radius: 10px; border: none;
      background: linear-gradient(90deg, #00d4ff, #7b2ff7);
      color: white; font-size: 1rem; font-weight: 600; cursor: pointer;
      transition: opacity 0.2s; letter-spacing: 0.5px;
    }
    button.analyze-btn:hover { opacity: 0.85; }
    button.analyze-btn:disabled { opacity: 0.5; cursor: not-allowed; }
    .hidden { display: none; }

    /* Results */
    #results { animation: fadeIn 0.5s ease; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; } }

    .score-section { text-align: center; padding: 20px 0; }
    .score-circle {
      width: 130px; height: 130px; border-radius: 50%; margin: 0 auto 16px;
      display: flex; flex-direction: column; align-items: center;
      justify-content: center; font-size: 2.2rem; font-weight: 700;
      border: 5px solid;
    }
    .score-label { font-size: 0.85rem; font-weight: 400; margin-top: 2px; }
    .score-excellent { border-color: #2ecc71; color: #2ecc71; }
    .score-good      { border-color: #f1c40f; color: #f1c40f; }
    .score-moderate  { border-color: #e67e22; color: #e67e22; }
    .score-low       { border-color: #e74c3c; color: #e74c3c; }

    .progress-bar-wrap { background: rgba(255,255,255,0.1); border-radius: 50px; height: 10px; margin: 12px 0 4px; }
    .progress-bar { height: 10px; border-radius: 50px; transition: width 1s ease; }

    .keyword-grid { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
    .kw-badge {
      padding: 5px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 500;
    }
    .kw-matched { background: #2ecc7122; border: 1px solid #2ecc71; color: #2ecc71; }
    .kw-missing { background: #e74c3c22; border: 1px solid #e74c3c; color: #e74c3c; }

    .feedback-list { list-style: none; }
    .feedback-list li {
      padding: 12px 16px; border-radius: 10px; margin-bottom: 10px;
      background: rgba(255,255,255,0.04); border-left: 3px solid #00d4ff;
      font-size: 0.92rem; line-height: 1.5;
    }

    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 14px; }
    .stat-box {
      background: rgba(255,255,255,0.04); border-radius: 12px; padding: 16px;
      text-align: center; border: 1px solid rgba(255,255,255,0.08);
    }
    .stat-box .stat-val { font-size: 1.8rem; font-weight: 700; color: #00d4ff; }
    .stat-box .stat-lbl { font-size: 0.8rem; color: #888; margin-top: 4px; }

    .loader {
      display: flex; align-items: center; justify-content: center; gap: 10px;
      padding: 20px; color: #aaa;
    }
    .spinner {
      width: 24px; height: 24px; border: 3px solid rgba(255,255,255,0.1);
      border-top-color: #00d4ff; border-radius: 50%; animation: spin 0.8s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
  </style>
</head>
<body>
<div class="container">

  <h1>🤖 AI Resume Analyzer</h1>
  <p class="subtitle">Match your resume to any job description and get instant AI-powered feedback</p>

  <!-- Input Card -->
  <div class="card">
    <h2>📄 Step 1 — Upload Your Resume</h2>
    <div class="tabs">
      <button class="tab active" onclick="switchTab('text')">Paste Text</button>
      <button class="tab" onclick="switchTab('pdf')">Upload PDF</button>
    </div>

    <div id="tab-text">
      <textarea id="resume-text" rows="10" placeholder="Paste your full resume text here..."></textarea>
    </div>
    <div id="tab-pdf" class="hidden">
      <div class="upload-area" onclick="document.getElementById('pdf-input').click()">
        <input type="file" id="pdf-input" accept=".pdf" onchange="handleFileSelect(this)"/>
        <div class="upload-icon">📁</div>
        <div id="file-label">Click to select a PDF resume</div>
        <div style="font-size:0.8rem; margin-top:6px; color:#666">Max 5MB</div>
      </div>
    </div>
  </div>

  <div class="card">
    <h2>💼 Step 2 — Paste Job Description</h2>
    <textarea id="jd-text" rows="8" placeholder="Paste the full job description or just the job title and key requirements..."></textarea>
  </div>

  <button class="analyze-btn" onclick="analyzeResume()" id="analyze-btn">
    ⚡ Analyze My Resume
  </button>

  <!-- Loader -->
  <div id="loader" class="hidden" style="margin-top:20px">
    <div class="loader"><div class="spinner"></div> Analyzing your resume with AI...</div>
  </div>

  <!-- Results -->
  <div id="results" class="hidden" style="margin-top:28px">

    <div class="card">
      <h2>📊 Match Score</h2>
      <div class="score-section">
        <div id="score-circle" class="score-circle">
          <span id="score-val">--</span>
          <span class="score-label" id="score-lbl">--</span>
        </div>
        <div class="progress-bar-wrap">
          <div id="score-bar" class="progress-bar" style="width:0%"></div>
        </div>
      </div>
    </div>

    <div class="card">
      <h2>📈 Quick Stats</h2>
      <div class="stats-grid">
        <div class="stat-box"><div class="stat-val" id="stat-matched">-</div><div class="stat-lbl">Matched Keywords</div></div>
        <div class="stat-box"><div class="stat-val" id="stat-missing">-</div><div class="stat-lbl">Missing Keywords</div></div>
        <div class="stat-box"><div class="stat-val" id="stat-words">-</div><div class="stat-lbl">Resume Words</div></div>
        <div class="stat-box"><div class="stat-val" id="stat-jdkw">-</div><div class="stat-lbl">JD Keywords</div></div>
      </div>
    </div>

    <div class="card">
      <h2>✅ Matched Keywords</h2>
      <div id="matched-kws" class="keyword-grid"></div>
    </div>

    <div class="card">
      <h2>❌ Missing Keywords</h2>
      <div id="missing-kws" class="keyword-grid"></div>
    </div>

    <div class="card">
      <h2>💡 Improvement Suggestions</h2>
      <ul id="feedback-list" class="feedback-list"></ul>
    </div>

  </div>
</div>

<script>
  let activeTab = 'text';
  let selectedFile = null;

  function switchTab(tab) {
    activeTab = tab;
    document.getElementById('tab-text').classList.toggle('hidden', tab !== 'text');
    document.getElementById('tab-pdf').classList.toggle('hidden', tab !== 'pdf');
    document.querySelectorAll('.tab').forEach((t, i) => {
      t.classList.toggle('active', (i === 0 && tab === 'text') || (i === 1 && tab === 'pdf'));
    });
  }

  function handleFileSelect(input) {
    selectedFile = input.files[0];
    document.getElementById('file-label').textContent = selectedFile
      ? '📄 ' + selectedFile.name : 'Click to select a PDF resume';
  }

  async function analyzeResume() {
    const jd = document.getElementById('jd-text').value.trim();
    if (!jd) { alert('Please paste a job description.'); return; }

    const btn = document.getElementById('analyze-btn');
    btn.disabled = true;
    document.getElementById('loader').classList.remove('hidden');
    document.getElementById('results').classList.add('hidden');

    try {
      let response;
      if (activeTab === 'pdf' && selectedFile) {
        const form = new FormData();
        form.append('pdf', selectedFile);
        form.append('jd', jd);
        response = await fetch('/analyze_pdf', { method: 'POST', body: form });
      } else {
        const resumeText = document.getElementById('resume-text').value.trim();
        if (!resumeText) { alert('Please paste your resume text.'); return; }
        response = await fetch('/analyze_text', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ resume: resumeText, jd })
        });
      }

      const data = await response.json();
      if (data.error) { alert('Error: ' + data.error); return; }
      renderResults(data);

    } catch(e) {
      alert('Something went wrong. Make sure the Flask server is running.');
    } finally {
      btn.disabled = false;
      document.getElementById('loader').classList.add('hidden');
    }
  }

  function renderResults(r) {
    const scoreColors = {
      Excellent: { cls: 'score-excellent', bar: '#2ecc71' },
      Good:      { cls: 'score-good',      bar: '#f1c40f' },
      Moderate:  { cls: 'score-moderate',  bar: '#e67e22' },
      Low:       { cls: 'score-low',       bar: '#e74c3c' },
    };
    const sc = scoreColors[r.score_label] || scoreColors.Low;

    const circle = document.getElementById('score-circle');
    circle.className = 'score-circle ' + sc.cls;
    document.getElementById('score-val').textContent = r.match_score + '%';
    document.getElementById('score-lbl').textContent = r.score_label;

    const bar = document.getElementById('score-bar');
    bar.style.background = sc.bar;
    setTimeout(() => bar.style.width = r.match_score + '%', 100);

    document.getElementById('stat-matched').textContent = r.matched_keywords.length;
    document.getElementById('stat-missing').textContent = r.missing_keywords.length;
    document.getElementById('stat-words').textContent   = r.word_count;
    document.getElementById('stat-jdkw').textContent    = r.jd_keywords.length;

    const matchedEl = document.getElementById('matched-kws');
    matchedEl.innerHTML = r.matched_keywords.length
      ? r.matched_keywords.map(k => `<span class="kw-badge kw-matched">${k}</span>`).join('')
      : '<span style="color:#888">No matched keywords found.</span>';

    const missingEl = document.getElementById('missing-kws');
    missingEl.innerHTML = r.missing_keywords.length
      ? r.missing_keywords.map(k => `<span class="kw-badge kw-missing">${k}</span>`).join('')
      : '<span style="color:#2ecc71">🎉 No missing keywords — great coverage!</span>';

    const fbList = document.getElementById('feedback-list');
    fbList.innerHTML = r.feedback.map(f => `<li>${f}</li>`).join('');

    document.getElementById('results').classList.remove('hidden');
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
  }
</script>
</body>
</html>
"""

# ── Routes ────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/analyze_text", methods=["POST"])
def analyze_text():
    try:
        data   = request.get_json()
        resume = data.get("resume", "").strip()
        jd     = data.get("jd", "").strip()
        if not resume or not jd:
            return jsonify({"error": "Both resume and job description are required."}), 400
        report = analyze_resume(resume, jd)
        return jsonify(report)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/analyze_pdf", methods=["POST"])
def analyze_pdf():
    try:
        if "pdf" not in request.files:
            return jsonify({"error": "No PDF file uploaded."}), 400
        pdf_file = request.files["pdf"]
        jd       = request.form.get("jd", "").strip()
        if not jd:
            return jsonify({"error": "Job description is required."}), 400

        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf_file.save(tmp.name)
            tmp_path = tmp.name

        resume_text = extract_text_from_pdf(tmp_path)
        os.unlink(tmp_path)

        report = analyze_resume(resume_text, jd)
        return jsonify(report)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Run ───────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🚀 Starting AI Resume Analyzer Web App...")
    print("   Open http://127.0.0.1:5000 in your browser\n")
    app.run(debug=True, port=5000)
