import os
import json
import re
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import PyPDF2
import io

app = Flask(__name__, static_folder="static")
CORS(app)


def extract_text_from_pdf(file_bytes):
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return f"[Could not extract PDF text: {str(e)}]"


def extract_text_from_file(file):
    filename = file.filename.lower()
    content = file.read()
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(content)
    else:
        try:
            return content.decode("utf-8")
        except Exception:
            return content.decode("latin-1", errors="ignore")


def analyze_resumes_locally(job_description, resume_contents):
    """Local keyword-based resume analysis without API"""
    
    # Extract key terms from job description
    jd_words = re.findall(r'\b\w+\b', job_description.lower())
    
    # Common technical skills to look for
    tech_skills = [
        'python', 'java', 'javascript', 'react', 'node', 'docker', 'aws', 'azure', 'gcp',
        'sql', 'mongodb', 'postgresql', 'mysql', 'redis', 'kubernetes', 'ci/cd', 'git',
        'linux', 'ubuntu', 'windows', 'macos', 'api', 'rest', 'graphql', 'microservices',
        'machine learning', 'ai', 'data science', 'analytics', 'tensorflow', 'pytorch',
        'flask', 'django', 'fastapi', 'spring', 'angular', 'vue', 'html', 'css', 'sass',
        'webpack', 'babel', 'jest', 'testing', 'agile', 'scrum', 'devops', 'terraform'
    ]
    
    # Extract required skills from job description
    required_skills = []
    for skill in tech_skills:
        if skill in job_description.lower():
            required_skills.append(skill)
    
    # Also extract capitalized words that might be skills
    capitalized_words = re.findall(r'\b[A-Z][a-zA-Z]+\b', job_description)
    required_skills.extend([word.lower() for word in capitalized_words if len(word) > 2])
    
    results = []
    
    for resume in resume_contents:
        resume_text = resume['text'].lower()
        resume_name = resume['name']
        
        # Extract candidate name (simple heuristic)
        name_match = re.search(r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b', resume['name'] or resume_text)
        candidate_name = name_match.group(1) if name_match else resume_name.replace('.pdf', '').replace('.txt', '')
        
        # Extract current/last role (simple heuristic)
        role_patterns = [
            r'(?:current|present|senior|lead|principal|junior|associate)\s+([a-z\s]+(?:engineer|developer|manager|analyst|designer|architect))',
            r'([a-z\s]+(?:engineer|developer|manager|analyst|designer|architect))\s+(?:at|@|from)',
            r'experience\s+as\s+([a-z\s]+(?:engineer|developer|manager|analyst|designer|architect))'
        ]
        
        inferred_role = "Candidate"
        for pattern in role_patterns:
            match = re.search(pattern, resume_text)
            if match:
                inferred_role = match.group(1).strip().title()
                break
        
        # Calculate skill matches
        skills_matched = []
        skills_missing = []
        
        for skill in required_skills:
            if skill in resume_text:
                skills_matched.append(skill)
            else:
                skills_missing.append(skill)
        
        # Calculate scores
        skill_score = min(100, (len(skills_matched) / max(len(required_skills), 1)) * 100)
        
        # Experience score based on years mentioned
        years_exp = sum(int(n) for n in re.findall(r'(\d+)\s+(?:years?|yrs?)\s+(?:of\s+)?(?:experience|exp)', resume_text))
        exp_score = min(100, years_exp * 10)  # 10 points per year, max 100
        
        # Education score (simple heuristic)
        education_keywords = ['bachelor', 'master', 'phd', 'degree', 'university', 'college', 'bs', 'ms', 'ba', 'ma']
        education_score = 70 if any(keyword in resume_text for keyword in education_keywords) else 40
        
        # Culture fit score (based on keywords)
        culture_keywords = ['team', 'collaborate', 'communication', 'leadership', 'project', 'deadline']
        culture_score = min(100, len([k for k in culture_keywords if k in resume_text]) * 20)
        
        # Overall score
        overall_score = int((skill_score * 0.4 + exp_score * 0.3 + education_score * 0.2 + culture_score * 0.1))
        
        # Generate summary
        if overall_score >= 75:
            summary = f"Strong candidate with good technical alignment and relevant experience."
        elif overall_score >= 50:
            summary = f"Moderate fit with some relevant skills but may have gaps in key areas."
        else:
            summary = f"Limited match - significant skill gaps or insufficient experience."
        
        # Bias detection (simple check for demographic indicators)
        bias_indicators = []
        if re.search(r'\b(19|20)\d{2}\b', resume_text):  # Years that might indicate age
            bias_indicators.append("potential age indicator")
        if any(word in resume_text for word in ['married', 'single', 'children', 'kids']):
            bias_indicators.append("personal information")
        
        bias_flag = "; ".join(bias_indicators) if bias_indicators else None
        
        results.append({
            "name": candidate_name,
            "role": inferred_role[:20],  # Limit to 4 words max
            "score": overall_score,
            "skills_matched": skills_matched[:10],  # Limit to top 10
            "skills_missing": skills_missing[:10],
            "breakdown": {
                "technical": int(skill_score),
                "experience": int(exp_score),
                "education": int(education_score),
                "culture_fit": int(culture_score)
            },
            "summary": summary,
            "bias_flag": bias_flag
        })
    
    # Sort by score descending
    results.sort(key=lambda x: x['score'], reverse=True)
    return results


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    jd = request.form.get("job_description", "").strip()
    if not jd:
        return jsonify({"error": "Job description is required"}), 400

    files = request.files.getlist("resumes")
    if not files or all(f.filename == "" for f in files):
        return jsonify({"error": "At least one resume is required"}), 400

    resume_contents = []
    for f in files:
        text = extract_text_from_file(f)
        resume_contents.append({"name": f.filename, "text": text[:2000]})

    try:
        results = analyze_resumes_locally(jd, resume_contents)
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": f"Analysis error: {str(e)}"}), 500


if __name__ == "__main__":
    print("\n🚀  Resume Screener running at http://localhost:5000\n")
    app.run(debug=True, port=5000)
