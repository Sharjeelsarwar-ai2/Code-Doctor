# 🩺 CodeDoctor

**Your AI-powered coding clinic.** Diagnose bugs, understand code, and ship better software — powered by Streamlit and Groq.

CodeDoctor takes a snippet of code, runs it through a local static scan plus an LLM-driven "full diagnosis," and returns a structured report: root cause, a corrected version of your code, a beginner-friendly explanation, performance/security improvements, and generated tests. You can then keep asking follow-up questions about the same code and report in a lightweight chat panel.

---

## ✨ Features

- **🩺 Full Diagnosis mode** — root cause analysis, fixed code, explanation, improvements, tests, and a final verdict (`HEALTHY` / `NEEDS FIXES` / `CRITICAL ISSUES`)
- **🐛 Focused modes** — Debug, Optimize, Explain, Tests, or Security, so the AI concentrates on exactly what you need
- **🔎 Quick Scan** — instant local static checks (unbalanced brackets/quotes, hard-coded secrets, `eval()` usage, tautological SQL conditions, overly long lines/files) with **no API call required**
- **💻 Multi-language support** — Python, C++, C, C#, Java, JavaScript, TypeScript, PHP, SQL, HTML/CSS, Go, Rust
- **💬 Follow-up chat** — ask CodeDoctor clarifying questions about your code or its own report, with full conversation context
- **⬇️ Download fixed code** — export the corrected snippet with the right file extension for your language
- **💡 Built-in examples** — buggy sample snippets to try the tool instantly, per language
- **🎨 Polished glassmorphic UI** — dark theme, blurred glass cards, gradient accents, and a floating chat dock

---

## 🛠️ Tech stack

| Layer        | Technology                          |
|--------------|--------------------------------------|
| UI           | [Streamlit](https://streamlit.io)    |
| AI inference | [Groq API](https://groq.com) (`openai/gpt-oss-120b`) |
| Language     | Python 3.9+                          |

---

## 📦 Getting started

### 1. Clone / download the project

Make sure you have `app.py` (the CodeDoctor source) in your project folder.

### 2. Install dependencies

```bash
pip install streamlit groq
```

### 3. Add your Groq API key

Get a free key from the [Groq Console](https://console.groq.com/keys), then configure it one of two ways:

**Option A — Streamlit secrets (recommended for Streamlit Cloud)**

Create `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "your-groq-api-key-here"
```

**Option B — Environment variable (recommended for local/Colab use)**

```bash
export GROQ_API_KEY="your-groq-api-key-here"
```

> The app checks `st.secrets` first and falls back to the `GROQ_API_KEY` environment variable, so either method works out of the box.

### 4. Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## ☁️ Running in Google Colab

```python
!pip install streamlit groq pyngrok -q

import os
os.environ["GROQ_API_KEY"] = "your-groq-api-key-here"

from pyngrok import ngrok
ngrok.set_auth_token("your-ngrok-authtoken")  # from https://dashboard.ngrok.com

!streamlit run app.py &>/content/logs.txt &
public_url = ngrok.connect(8501)
print(public_url)
```

Click the printed URL to open CodeDoctor in your browser.

---

## 🚀 Usage

1. **Pick a language** and **doctor mode** in the sidebar (Full Diagnosis, Debug, Optimize, Explain, Tests, or Security).
2. **Paste your code** into the workspace, or click **💡 Load example** to try a sample buggy snippet.
3. Click **🩺 Diagnose My Code** for a full AI-generated report, or **🔎 Quick Scan** for an instant local static check with no API usage.
4. Review the report across tabs: Diagnosis, Fixed Code, Explanation, Improvements, Tests, and Full Report.
5. **⬇️ Download** the corrected code once a diagnosis is ready.
6. Use the **chat dock** at the bottom to ask follow-up questions — CodeDoctor keeps your current code and the latest report in context.
7. **🧹 Clear workspace** to reset everything and start fresh.

---

## 🩻 Doctor modes

| Mode              | Focus                                                              |
|-------------------|----------------------------------------------------------------------|
| 🩺 Full Diagnosis | Bugs, logic errors, security issues, performance, maintainability   |
| 🐛 Debug          | Errors, bugs, root causes, corrected code                           |
| ⚡ Optimize        | Performance, efficiency, readability, cleaner implementation        |
| 🧠 Explain        | Clear explanation of code and key concepts for learners             |
| 🧪 Tests          | Useful tests, edge cases, and expected results                      |
| 🔒 Security       | Vulnerabilities, unsafe input handling, injection risks, secrets    |

---

## 📁 Project structure

```
.
├── app.py               # Full Streamlit application (UI + logic)
└── .streamlit/
    └── secrets.toml     # (optional) GROQ_API_KEY for local/cloud deployment
```

CodeDoctor is intentionally a single-file app for easy deployment (e.g. Streamlit Cloud, Colab, or a quick local demo).

---

## ⚠️ Notes

- CodeDoctor **never executes your code**. All analysis is static — either simple pattern-based checks run locally, or reasoning performed by the LLM. No compiler/interpreter is invoked.
- Keep your `GROQ_API_KEY` out of source control. Use `secrets.toml` or environment variables, and add `.streamlit/secrets.toml` to `.gitignore`.

---

## 📄 License

Add your preferred license here (e.g. MIT).
