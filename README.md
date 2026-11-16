# 🎓 Lab Report Lagbe!

AI-powered lab report generator. Fill in your info, describe your tasks — get a complete PDF lab report with code, output, and proper formatting.

## ✨ Features

- 🤖 **AI Code Generation** — Groq (Llama 3.3 70B) writes code from task descriptions
- ▶️ **Auto Code Execution** — Piston API runs code in a safe sandbox (15+ languages)
- 📄 **LaTeX PDF Report** — Professional cover page, code listings, execution output
- 🌐 **Web Interface** — Clean, modern form — no technical knowledge needed
- 💰 **100% Free** — Groq API + Piston API + free deployment

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.10+
- `pdflatex` installed (`sudo apt install texlive-base texlive-latex-extra texlive-fonts-recommended`)
- Groq API key ([get free key](https://console.groq.com/keys))

### Setup
```bash
git clone https://github.com/Masud744/Lab-Report-Lagbe-.git
cd Lab-Report-Lagbe-

pip install -r requirements.txt

# Set your Groq API key (or enter it in the web UI)
cp .env.example .env
# Edit .env and add your key

# Run the server
uvicorn app:app --reload --port 7860
```

Open http://localhost:7860 in your browser.

### Docker
```bash
docker compose up --build
```

## 📋 Supported Languages

Python, Dart, C++, C, Java, JavaScript, TypeScript, Go, Rust, Kotlin, Ruby, PHP, Swift, R, Bash

## 🏗️ Tech Stack

| Component | Technology |
|---|---|
| Backend | Python FastAPI |
| AI | Groq API (Llama 3.3 70B) |
| Code Execution | Piston API |
| PDF | LaTeX (pdflatex) |
| Frontend | Vanilla HTML/CSS/JS |

## 📁 Project Structure

```
├── app.py                  # FastAPI server
├── services/
│   ├── ai_service.py       # Groq AI integration
│   ├── code_runner.py      # Piston API integration
│   └── latex_generator.py  # LaTeX template engine
├── templates/
│   └── report_template.tex # LaTeX Jinja2 template
├── static/                 # Frontend
│   ├── index.html
│   ├── css/style.css
│   ├── js/app.js
│   └── images/logo.png
├── Dockerfile
└── docker-compose.yml
```

## 📄 License

MIT

---

Made with ❤️ by Shahriar Alom Masud
