# resume-analyser-project

# Resume Analyzer

An AI-powered Resume Analyzer built with **Python, Flask, and OpenRouter
AI**.\
The application allows users to upload their resume in **PDF or DOCX
format** and receive an AI-generated analysis of their resume.

## 🚀 Features

-   Upload resumes in PDF and DOCX formats
-   Extract text from uploaded resumes
-   AI-powered resume analysis
-   Identify strengths and weaknesses
-   Suggest improvements
-   Analyze skills and experience
-   Provide actionable resume recommendations
-   Simple Flask-based web interface
-   Environment-variable based API key configuration

## 🛠️ Technologies Used

-   **Python**
-   **Flask**
-   **HTML5**
-   **CSS3**
-   **OpenRouter API**
-   **PyPDF2 / PDF text extraction**
-   **python-docx**
-   **python-dotenv**

## 📁 Project Structure

``` text
resume-analyzer/
│
├── app.py
├── ask_ai.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
│
├── templates/
│   ├── index.html
│   └── result.html
│
└── static/
    └── style.css
```

> The exact structure may vary depending on your project version.

## ⚙️ Installation

### 1. Clone the repository

``` bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

### 2. Create a virtual environment

Windows:

``` bash
python -m venv venv
```

Activate it:

``` bash
venv\Scripts\activate
```

### 3. Install dependencies

``` bash
pip install -r requirements.txt
```

If you do not have a requirements file yet, install the main packages:

``` bash
pip install flask python-dotenv openai PyPDF2 python-docx
```

## 🔑 API Key Configuration

Create a `.env` file in the project root:

``` env
OPENROUTER_API_KEY=your_api_key_here
MODEL_NAME=your_model_name
```

**Never upload your real API key to GitHub.**

Add `.env` to `.gitignore`:

``` text
.env
venv/
__pycache__/
```

## ▶️ Run the Application

Activate the virtual environment:

``` bash
venv\Scripts\activate
```

Start Flask:

``` bash
python app.py
```

Then open the local URL shown in the terminal, usually:

``` text
http://127.0.0.1:5000
```

## 📄 How It Works

``` text
User
  ↓
Upload Resume
  ↓
Flask Application
  ↓
PDF / DOCX Text Extraction
  ↓
AI Resume Analysis
  ↓
OpenRouter API
  ↓
Analysis Result
  ↓
User
```

## 📊 Example Analysis

The application can provide feedback such as:

-   Resume strengths
-   Missing or weak sections
-   Technical skills identified
-   Experience analysis
-   Project relevance
-   Suggestions for improvement
-   ATS-related recommendations
-   Overall resume feedback

## 🔒 Security

-   Keep API keys in `.env`
-   Do not commit `.env` to GitHub
-   Do not hard-code API keys in Python files
-   Use `.gitignore` for sensitive files

If an API key was accidentally uploaded to a public GitHub repository,
revoke it and create a new one.

## 🔮 Future Improvements

-   ATS score calculation
-   Job-description matching
-   Skill-gap analysis
-   Resume keyword optimization
-   Multiple resume comparison
-   Downloadable analysis report
-   User authentication
-   Database support
-   Improved UI/UX

## 👩‍💻 Author

**Amrutha J S**

Engineering Student \| Web Developer \| AI Enthusiast

## ⭐ Project Purpose

This project was developed as a learning project to explore **AI
integration, Flask web development, file processing, and resume
analysis** using an external AI API.

If you find this project useful, consider giving the repository a ⭐ on
GitHub.
