# Applicant Tracking System (ATS) with Google Gemini

This project is an **industrial-grade Applicant Tracking System (ATS)** built using Streamlit, Google Generative AI (Gemini), and advanced Python libraries. It provides rigorous, realistic ATS scoring and analysis for resumes against job descriptions, suitable for enterprise-level recruitment.

## Key Features
- **Strict, Realistic ATS Scoring:**
  - Mathematically advanced scoring blends Gemini AI analysis and keyword match, with penalties for low match.
  - Award levels (Gold, Silver, Bronze) based on score.
- **Industrial-Grade Prompt Rigor:**
  - Uses a strict external JSON template for Gemini prompts, enforcing format and evidence citation.
  - Flags fake, generic, or AI-generated resumes and incomplete job descriptions.
- **Keyword Cloud Visualization:**
  - Generates and displays keyword clouds for both resume and job description.
  - Calculates and shows keyword match percentage.
- **Skills Table Extraction:**
  - Extracts and displays hard and soft skills as a structured table with counts.
- **Comprehensive ATS Report:**
  - Bullet-pointed strengths, weaknesses, recommendations, and recruiter tips.
  - Candidate information, contact analysis, education, and measurable results.
- **Modern UI:**
  - Award card, skills table, and visual keyword clouds for clarity and impact.
Deployed here: (https://gemini-ats-codingcruella.streamlit.app/)


## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Logic](#logic)
- [Capabilities](#capabilities)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites
- [VS Code](https://code.visualstudio.com/)
- [Python 3.11](https://www.python.org/downloads/)

### Steps

1. **Clone the repository:**
    ```sh
    git clone https://github.com/yourusername/ats_project.git
    cd ats_project
    ```

2. **(Recommended) Create a virtual environment:**
    ```sh
    python -m venv .venv
    # Activate the environment
    # On Windows:
    .venv\Scripts\activate
    # On macOS/Linux:
    source .venv/bin/activate
    ```

3. **Install the required packages:**
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up the environment variables:**
    - Create a `.env` file in the root directory of the project.
    - Add your Google Generative AI API key to the `.env` file:
      ```env
      GEMINI_API_KEY=your_api_key_here
      ```

## Usage

1. **Open the project in VS Code.**
2. **Run the Streamlit app:**
    ```sh
    streamlit run ats_app_v3.py
    ```
3. **Interact with the app:**
    - Upload a resume in PDF, DOCX, or TXT format.
    - Enter the job requirements in the provided text area.
    - Click the "Calculate Score" button to get the ATS score and suggestions.

## Project Structure
ats_project/ 
│ ├── .conda/ 
│ ├── .gitignore 
│ ├── .nonadmin 
│ ├── api-ms-win-core-console-l1-1-0.dll 
│ ├── ... 
│ 
├── .env 
├── ats_app.py 
├── requirements.txt 
└── README.md


## Logic

The project is built using Streamlit for the web interface and Google Generative AI for generating the ATS score and suggestions. Below is a brief explanation of the logic:

1. **Page Configuration:**
    - The page is configured using `st.set_page_config` to set the title and layout.

2. **Environment Variables:**
    - The API key for Google Generative AI is loaded from the `.env` file using `load_dotenv`.

3. **Class `ApplicantTrackingSystem`:**
    - **`__init__` Method:** Initializes the class with `resume_text` set to `None`.
    - **`upload_resume` Method:** Handles file upload and extracts text from the uploaded resume using helper methods (`extract_text_from_pdf`, `extract_text_from_docx`).
    - **`extract_text_from_pdf` Method:** Extracts text from a PDF file using `PyPDF2`.
    - **`extract_text_from_docx` Method:** Extracts text from a DOCX file using `docx`.
    - **`calculate_score` Method:** Generates a comprehensive ATS assessment report using Google Generative AI based on the uploaded resume and job requirements.

4. **Streamlit Layout:**
    - The layout includes a title, sidebar for uploading resumes, and a main content area for entering job requirements and displaying the ATS score.

## Capabilities

### Industrial-Grade ATS Logic
- **Strict Format Enforcement:**
  - Gemini prompt uses a JSON template enforcing section order, evidence citation, and error handling.
- **Mathematical Scoring:**
  - Final ATS score = 70% Gemini AI score + 30% keyword match, with penalties for low match (<40%).
- **Award System:**
  - Gold, Silver, Bronze, or No Award based on score thresholds.
- **Keyword Analysis:**
  - Keyword clouds and match percentage for resume vs. job description.
- **Skills Table:**
  - Hard and soft skills extracted and displayed with counts.
- **Fake/Generic Resume Detection:**
  - Flags and explains if resume or job description is fake, generic, or incomplete.
- **Recruiter Tips:**
  - Experience, measurable results, paragraph length, and tone analysis.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License


This project is licensed under the MIT License.

