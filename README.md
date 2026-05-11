<<<<<<< HEAD
# Career Guidance Chatbot

A professional **Career Guidance Chatbot** built with **Python**, **Streamlit**, **CrewAI**, **LangChain**, **Google Gemini API**, and **Groq fallback**.

It collects a user profile (skills, interests, education, experience, goals) and generates a complete personalized career plan:

- Profile Analysis
- Career Options (best-fit paths + future scope)
- Study Roadmap (3 or 6 months, weekly plan, mini-projects)
- Courses & Certifications (resources + platforms)
- Job Preparation Tips (resume/LinkedIn/GitHub/interviews)

---

## Project Structure

```
career_guidance_chatbot/
├── app.py
├── agents.py
├── llm_config.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## 1) Installation (Local)

### Prerequisites
- Python **3.10+** (your system can be newer; Streamlit Cloud usually uses 3.10/3.11)

### Steps

```bash
cd career_guidance_chatbot
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

---

## 2) Add API Keys

1. Create a `.env` file in the same folder as `app.py`.
2. Copy from `.env.example` and add your keys:

```bash
GEMINI_API_KEY=...
GROQ_API_KEY=...
```

Notes:
- **Gemini is used first** (primary).
- If Gemini fails or is missing, the app **falls back to Groq** (if configured).
- Keys are loaded via `python-dotenv`.

---

## 3) Run the App

```bash
cd career_guidance_chatbot
streamlit run app.py
```

---

## 4) Deploy on Streamlit Cloud

1. Push this project to a GitHub repository.
2. In Streamlit Cloud, click **New app** → select the repo/branch.
3. Set:
   - **Main file path**: `career_guidance_chatbot/app.py`
4. Add secrets (recommended):
   - Go to **App settings → Secrets**
   - Add:

```toml
GEMINI_API_KEY="your_key"
GROQ_API_KEY="your_key"
```

Streamlit Cloud automatically exposes these as environment variables.

---

## Troubleshooting

- **No API keys found**: create `.env` and set `GEMINI_API_KEY` and/or `GROQ_API_KEY`.
- **Install errors on Windows**: upgrade pip first:

```bash
python -m pip install --upgrade pip
```

- **Unexpected formatting**: the UI will show the raw output if section parsing fails.

=======
# career-guidance-chatbot
>>>>>>> b3f4719aa73fc6b0f2ea74033f2f10fc8d891322
