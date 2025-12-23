import streamlit as st
import PyPDF2
import docx
import os
import re
from dotenv import load_dotenv
import google.generativeai as genai
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(page_title="Applicant Tracking System", layout="wide")

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Google Generative AI
genai.configure(api_key=API_KEY)

class ApplicantTrackingSystem:
    def __init__(self):
        self.resume_text = None

    def upload_resume(self):
        uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])
        if uploaded_file is not None:
            try:
                with st.spinner('Extracting text from resume...'):
                    if uploaded_file.type == "application/pdf":
                        self.resume_text = self.extract_text_from_pdf(uploaded_file)
                    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        self.resume_text = self.extract_text_from_docx(uploaded_file)
                    elif uploaded_file.type == "text/plain":
                        self.resume_text = uploaded_file.read().decode("utf-8")
            except Exception as e:
                st.error(f"Error reading resume: {str(e)}")
                self.resume_text = None

    def extract_text_from_pdf(self, uploaded_file):
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        return text


    def calculate_score(self, requirements):
        import json
        # Failsafe: No resume uploaded
        if not self.resume_text:
            st.warning("No resume uploaded or reading error occurred.")
            return
        # Failsafe: No job description or too short
        if not requirements or len(requirements.strip()) < 20:
            st.warning("Please enter a detailed job description (at least 20 characters). The ATS cannot proceed without it.")
            return
        with st.spinner('Processing resume and job description...'):
            # --- Keyword Match Calculation ---
            from collections import Counter
            import re
            stopwords = set(['the','and','to','of','in','a','for','on','with','is','as','by','at','an','be','are','from','or','that','this','it','was','which','has','have','will','can','not','but','if','your','you','we','our','their','they','i'])
            resume_words = re.findall(r'\b\w+\b', self.resume_text.lower())
            resume_keywords = [w for w in resume_words if w not in stopwords and len(w) > 2]
            jd_words = re.findall(r'\b\w+\b', requirements.lower())
            jd_keywords = [w for w in jd_words if w not in stopwords and len(w) > 2]
            resume_set = set(resume_keywords)
            jd_set = set(jd_keywords)
            match_count = len(resume_set & jd_set)
            match_percent = (match_count / len(jd_set)) * 100 if jd_set else 0

            # --- Load strict industrial-grade ATS prompt template ---
            with open('response_template.json', 'r', encoding='utf-8') as f:
                template_json = json.load(f)
            ats_score_txt = "Score & (_emoji)"
            detection = "(detected value) (Detected Status) (ATS Comment if any) (_emoji)"
            prompt = template_json["prompt_template"].format(
                ats_score_txt=ats_score_txt,
                detection=detection,
                resume_text=self.resume_text,
                requirements=requirements
            )

            # --- Gemini API Call ---
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(prompt)
            response_text = response.text.strip()

            # --- Extract Gemini score and emoji robustly ---
            gemini_score = None
            emoji = ""
            # Try to extract 'Gemini score: 89%' or similar
            gemini_score_line = re.search(r"Gemini score:\s*(\d+)%\s*([\u2705\u26A0\u274C\U0001F929\U0001F60E\U0001F60A\U0001F60D\U0001F929\U0001F929]*)", response_text)
            if gemini_score_line:
                gemini_score = int(gemini_score_line.group(1))
                emoji = gemini_score_line.group(2)
            else:
                # Fallback: try to extract 'ATS score: 89%' if Gemini score not found
                ats_score_line = re.search(r"ATS score:\s*(\d+)%\s*([\u2705\u26A0\u274C]*)", response_text)
                if ats_score_line:
                    gemini_score = int(ats_score_line.group(1))
                    emoji = ats_score_line.group(2)

            # --- Mathematically advanced ATS scoring ---
            # Blend Gemini score and keyword match, penalize low match
            if gemini_score is not None:
                # Weighted blend: 70% Gemini, 30% keyword match
                final_score = 0.7 * gemini_score + 0.3 * match_percent
                # Penalty: If match_percent < 40%, apply a penalty
                if match_percent < 40:
                    penalty = (40 - match_percent) * 0.5  # up to -20 points
                    final_score -= penalty
                final_score = max(0, min(100, round(final_score)))
            else:
                final_score = None


            # --- Percentage Cards for Gemini, Keyword Match, and Final ATS Score ---
            # Format values for display
            match_percent_display = f"{match_percent:.1f}" if match_percent is not None else "--"
            gemini_score_display = f"{gemini_score}%" if gemini_score is not None else "--%"
            final_score_display = f"{final_score}%" if final_score is not None else "--%"
            st.markdown(f"""
                <div style='display: flex; gap: 2em; justify-content: center; margin-bottom: 1.5em;'>
                    <div style='background: #181c22; border-radius: 14px; padding: 1.2em 2em; min-width: 180px; text-align: center; box-shadow: 0 2px 8px rgba(44,62,80,0.10);'>
                        <div style='font-size: 1.1em; color: #FFD700; font-weight: 600;'>Gemini Score</div>
                        <div style='font-size: 2.2em; color: #FFD700; font-weight: bold;'>{gemini_score_display}</div>
                    </div>
                    <div style='background: #181c22; border-radius: 14px; padding: 1.2em 2em; min-width: 180px; text-align: center; box-shadow: 0 2px 8px rgba(44,62,80,0.10);'>
                        <div style='font-size: 1.1em; color: #1abc9c; font-weight: 600;'>Keyword Match</div>
                        <div style='font-size: 2.2em; color: #1abc9c; font-weight: bold;'>{match_percent_display}%</div>
                    </div>
                    <div style='background: #181c22; border-radius: 14px; padding: 1.2em 2em; min-width: 180px; text-align: center; box-shadow: 0 2px 8px rgba(44,62,80,0.10);'>
                        <div style='font-size: 1.1em; color: #2980b9; font-weight: 600;'>Overall ATS Score</div>
                        <div style='font-size: 2.2em; color: #2980b9; font-weight: bold;'>{final_score_display}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # --- Modern Award Card with f-string rendering and animation ---
            if final_score is not None:
                if final_score >= 85:
                    award = "Gold"
                    award_color = "#FFD700"
                elif final_score >= 70:
                    award = "Silver"
                    award_color = "#C0C0C0"
                elif final_score >= 50:
                    award = "Bronze"
                    award_color = "#cd7f32"
                else:
                    award = "No Award"
                    award_color = "#7f8c8d"
            else:
                award = "No Award"
                award_color = "#7f8c8d"

            st.markdown(f"""
                <div style='background: linear-gradient(90deg, #1abc9c 0%, #2980b9 100%); border-radius: 18px; padding: 2em 1em; margin-bottom: 2em; box-shadow: 0 4px 24px rgba(44,62,80,0.15); text-align: center; position: relative;'>
                    <span style='font-size: 2.5em; font-weight: bold; color: #fff;'>ATS Score</span><br>
                    <span id="score-anim" style='font-size: 4em; font-weight: bold; color: #fff;'>{final_score_display}</span>
                    <span style='font-size: 2.5em;'>{emoji}</span>
                    <div style='margin-top: 1em; color: {award_color if award != 'No Award' else '#e74c3c'}; font-size: 1.2em; font-weight: 700;'>🏆 Award Level: {award}</div>
                </div>
                <style>
                @keyframes pop {{
                    0% {{ transform: scale(1); }}
                    60% {{ transform: scale(1.15); }}
                    100% {{ transform: scale(1); }}
                }}
                #score-anim {{
                    animation: pop 1.2s cubic-bezier(.36,1.56,.64,1) 1;
                    display: inline-block;
                }}
                </style>
            """, unsafe_allow_html=True)

            # --- Show the formatted AI response as part of the page ---
            st.markdown("<div style='margin-bottom: 2em;'></div>", unsafe_allow_html=True)
        def beautify_response(text):
            # Split into sections by * **Section:**
            sections = re.split(r'\n\* \*\*', text)
            html = ""
            for i, sec in enumerate(sections):
                if not sec.strip():
                    continue
                # Section title
                if i == 0 and sec.startswith('Overall Assessment:'):
                    title = 'Overall Assessment'
                    body = sec[len('Overall Assessment:'):].strip()
                elif '**' in sec:
                    title, body = sec.split('**', 1)
                    title = title.strip(': ')
                else:
                    title = ''
                    body = sec
                if title:
                    html += f"<div style='margin-top:2em;'><span style='font-size:1.5em;font-weight:700;color:#f1c40f;'>{title}</span></div>"
                # Bullet points and highlights
                lines = body.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    # Stricter: Only exact matches (Detected, ✅) are green, Partial/⚠️ yellow, Not found/❌/Ambiguous red
                    if re.search(r'(Not found|❌|ambiguous|missing)', line, re.I):
                        color = '#e74c3c'
                        icon = '❌'
                    elif re.search(r'(Partial|⚠️)', line, re.I):
                        color = '#f1c40f'
                        icon = '⚠️'
                    elif re.search(r'(Detected|✅)', line, re.I):
                        color = '#27ae60'
                        icon = '✅'
                    else:
                        color = '#eaeaea'
                        icon = ''
                    # Bullet or not
                    if line.startswith('- '):
                        line = line[2:]
                        html += f"<div style='margin-left:1.5em;margin-bottom:0.3em;'><span style='color:{color};font-size:1.1em;'>{icon}</span> <span style='color:{color};font-weight:500;'>{line}</span></div>"
                    else:
                        html += f"<div style='margin-left:0.5em;margin-bottom:0.3em;'><span style='color:{color};font-size:1.1em;'>{icon}</span> <span style='color:{color};font-weight:500;'>{line}</span></div>"
            return html

        # --- Parse and render skills table as a real table ---
        import pandas as pd
        # Find the skills table markdown block
        table_block = re.search(r'(\| Hard Skills \| Soft Skills \|[\s\S]+?\|[\s\S]+?\|)', response_text)
        df_skills = None
        if table_block:
            table_lines = [line.strip() for line in table_block.group(1).split('\n') if line.strip() and line.strip().startswith('|')]
            # Remove header and separator
            if len(table_lines) >= 3:
                data_line = table_lines[2]
                # Split by | and remove empty
                cells = [c.strip() for c in data_line.split('|') if c.strip()]
                if len(cells) == 2:
                    # Parse skill: count pairs for each column
                    def parse_skills(cell):
                        pairs = [s.strip() for s in cell.split(',') if s.strip()]
                        skills = []
                        counts = []
                        for p in pairs:
                            if ':' in p:
                                skill, count = p.split(':', 1)
                                skills.append(skill.strip())
                                counts.append(count.strip())
                            else:
                                skills.append(p.strip())
                                counts.append('1')
                        return skills, counts
                    hard_skills, hard_counts = parse_skills(cells[0])
                    soft_skills, soft_counts = parse_skills(cells[1])
                    max_len = max(len(hard_skills), len(soft_skills))
                    hard_skills += [''] * (max_len - len(hard_skills))
                    hard_counts += [''] * (max_len - len(hard_counts))
                    soft_skills += [''] * (max_len - len(soft_skills))
                    soft_counts += [''] * (max_len - len(soft_counts))
                    df_skills = pd.DataFrame({
                        "Hard Skill": hard_skills,
                        "Hard Count": hard_counts,
                        "Soft Skill": soft_skills,
                        "Soft Count": soft_counts
                    })
            # Remove the markdown table from the response for display
            response_text_clean = response_text.replace(table_block.group(1), '')
        else:
            response_text_clean = response_text

        # --- Render the rest of the response ---
        main_html = beautify_response(response_text_clean)
        st.markdown(f"""
            <div style='background: #23272f; border-radius: 16px; padding: 2em 2em 1em 2em; margin-bottom: 2em; box-shadow: 0 2px 12px rgba(44,62,80,0.10); color: #eaeaea;'>
                {main_html}
        """, unsafe_allow_html=True)
        if df_skills is not None:
            st.markdown("<h5 style='color:#f1c40f;margin-top:1em;'>Skills Table</h5>", unsafe_allow_html=True)
            st.dataframe(df_skills, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # --- Keyword Clouds and Match Percentage ---
        from wordcloud import WordCloud
        import matplotlib.pyplot as plt
        resume_freq = Counter(resume_keywords)
        jd_freq = Counter(jd_keywords)
        if resume_freq:
            wc1 = WordCloud(width=800, height=300, background_color='#181c22', colormap='viridis').generate_from_frequencies(resume_freq)
            fig1, ax1 = plt.subplots(figsize=(8, 3))
            ax1.imshow(wc1, interpolation='bilinear')
            ax1.axis('off')
            st.markdown("<h4 style='color:#f1c40f;margin-top:0.5em;'>Resume Keyword Cloud</h4>", unsafe_allow_html=True)
            st.pyplot(fig1)
        if jd_freq:
            wc2 = WordCloud(width=800, height=300, background_color='#181c22', colormap='plasma').generate_from_frequencies(jd_freq)
            fig2, ax2 = plt.subplots(figsize=(8, 3))
            ax2.imshow(wc2, interpolation='bilinear')
            ax2.axis('off')
            st.markdown("<h4 style='color:#f39c12;margin-top:0.5em;'>Job Description Keyword Cloud</h4>", unsafe_allow_html=True)
            st.pyplot(fig2)
        # Show match percentage
        if resume_keywords and jd_keywords:
            st.markdown(f"<div style='color:#1abc9c;font-size:1.2em;margin-top:1em;'><b>Keyword Match:</b> {match_count} / {len(jd_set)} (<b>{match_percent:.1f}%</b>) of job description keywords found in resume</div>", unsafe_allow_html=True)
        else:
            st.warning("No resume uploaded or reading error occurred.")


# Instantiate the ApplicantTrackingSystem class
ats = ApplicantTrackingSystem()

# Streamlit app layout
st.title("Applicant Tracking System with Google Gemini")
st.sidebar.title("Options")

# Sidebar widgets
with st.sidebar:
    ats.upload_resume()

# Main content
st.header("Enter Job Requirements:")
requirements = st.text_area("Enter job requirements here", height=200)

if st.button("Calculate Score"):
    ats.calculate_score(requirements)

st.sidebar.markdown("### By: Virus1260")