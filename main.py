import os
import re
import streamlit as st
from groq import Groq

APP_NAME = "CodeDoctor"
MODEL_NAME = "openai/gpt-oss-120b"

LANGUAGES = ["Python", "C++", "C", "C#", "Java", "JavaScript", "TypeScript", "PHP", "SQL", "HTML/CSS", "Go", "Rust"]
MODES = {
    "🩺 Full Diagnosis": "Find bugs, logic errors, security issues, performance problems, and maintainability issues.",
    "🐛 Debug": "Focus on errors, bugs, root causes, and corrected code.",
    "⚡ Optimize": "Focus on performance, efficiency, readability, and cleaner implementation.",
    "🧠 Explain": "Explain the code and important concepts clearly for a learner.",
    "🧪 Tests": "Create useful tests, edge cases, and expected results.",
    "🔒 Security": "Find security vulnerabilities, unsafe input handling, injection risks, and secrets.",
}

SAMPLES = {
    "Python": '''def calculate_average(numbers):
    total = 0
    for i in range(len(numbers) + 1):
        total += numbers[i]
    return total / len(numbers)

print(calculate_average([10, 20, 30]))''',
    "C++": '''#include <iostream>
using namespace std;

int main() {
    int numbers[] = {10, 20, 30};
    int size = 3;
    for (int i = 0; i <= size; i++) {
        cout << numbers[i] << endl;
    }
    return 0;
}''',
    "C#": '''using System;
class Program {
    static void Main() {
        int[] numbers = {10, 20, 30};
        for (int i = 0; i <= numbers.Length; i++) {
            Console.WriteLine(numbers[i]);
        }
    }
}''',
    "JavaScript": '''function getUserName(user) {
    return user.profile.name.toUpperCase();
}
const user = { name: "Alex" };
console.log(getUserName(user));''',
    "Java": '''public class Main {
    public static void main(String[] args) {
        int[] numbers = {10, 20, 30};
        for (int i = 0; i <= numbers.length; i++) {
            System.out.println(numbers[i]);
        }
    }
}''',
    "SQL": "SELECT * FROM users WHERE username = 'admin' OR 1=1;",
}

st.set_page_config(page_title="CodeDoctor", page_icon="💉", layout="wide", initial_sidebar_state="auto")

st.markdown(r"""
<style>
/* ============ CodeDoctor professional theme — dark violet/cyan glass ============ */
.stApp{
  background:
    radial-gradient(900px 480px at 12% -8%, rgba(124,58,237,.28), transparent 60%),
    radial-gradient(800px 420px at 96% 0%, rgba(6,182,212,.22), transparent 55%),
    radial-gradient(700px 500px at 50% 115%, rgba(124,58,237,.14), transparent 60%),
    #05070f;
  color:#eef2ff;
  font-family:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
}
.stApp::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
  background-image:linear-gradient(rgba(148,163,184,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(148,163,184,.05) 1px,transparent 1px);
  background-size:56px 56px;
  -webkit-mask-image:radial-gradient(ellipse 90% 55% at 50% 0%,#000 30%,transparent 75%);
  mask-image:radial-gradient(ellipse 90% 55% at 50% 0%,#000 30%,transparent 75%);
}
.block-container{max-width:1480px;padding:1.4rem 2rem 150px;position:relative;z-index:1}
h1,h2,h3{letter-spacing:-.02em}
p,li{color:#dbe4f3}
section[data-testid="stSidebar"]{width:330px!important;background:linear-gradient(180deg,#0b1122 0%,#070b16 100%);border-right:1px solid rgba(148,163,184,.16)}
section[data-testid="stSidebar"] .block-container{padding-top:1.2rem}
header[data-testid="stHeader"]{background:transparent!important;box-shadow:none!important;height:2.6rem!important;min-height:0!important}
header[data-testid="stHeader"] [data-testid="stToolbarActions"]{display:none!important}
header[data-testid="stHeader"] [data-testid="stDecoration"]{display:none!important}
#MainMenu{visibility:hidden!important}
footer{visibility:hidden!important}
[data-testid="stSidebarCollapsedControl"]{z-index:999999!important;opacity:1!important;visibility:visible!important}
@keyframes rise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
@media (prefers-reduced-motion: reduce){*{animation:none!important;transition:none!important}}

/* ---------- top bar ---------- */
.topbar{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;padding:10px 4px 14px}
.topbar-left{display:flex;align-items:center;gap:10px;font-size:.78rem;font-weight:800;letter-spacing:.16em;color:#e2e8f0}
.topbar-dot{width:9px;height:9px;border-radius:50%;background:linear-gradient(135deg,#a78bfa,#22d3ee);box-shadow:0 0 14px rgba(139,92,246,.8)}
.topbar-pill{padding:7px 12px;border-radius:999px;background:rgba(255,255,255,.06);border:1px solid rgba(148,163,184,.22);color:#cbd5e1;font-size:.75rem;font-weight:650;white-space:nowrap}
.topbar-pill b{color:#fff}

/* ---------- hero ---------- */
.hero{position:relative;overflow:hidden;isolation:isolate;display:flex;gap:28px;align-items:stretch;padding:38px 38px 32px;margin:0 0 20px;border-radius:28px;border:1px solid rgba(167,139,250,.35);background:linear-gradient(135deg,rgba(30,27,75,.72),rgba(8,47,73,.45) 55%,rgba(15,23,42,.78));box-shadow:0 28px 70px rgba(0,0,0,.38),inset 0 1px 0 rgba(255,255,255,.09);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);animation:rise .5s ease both}
.hero::before{content:"";position:absolute;left:0;right:0;top:0;height:3px;background:linear-gradient(90deg,#7c3aed,#22d3ee,#7c3aed)}
.hero::after{content:"";position:absolute;width:260px;height:260px;right:-90px;top:-130px;border-radius:50%;background:rgba(34,211,238,.14);filter:blur(10px);z-index:-1}
.hero-main{flex:1.55;min-width:280px}
.hero-eyebrow{margin:0 0 12px;font-size:.74rem;font-weight:800;letter-spacing:.18em;text-transform:uppercase;color:#a5f3fc}
.hero-title{margin:0!important;padding:0!important;font-size:clamp(2.5rem,5.4vw,4rem)!important;line-height:.98!important;font-weight:900!important;letter-spacing:-.05em;color:#fff}
.hero-title span{background:linear-gradient(90deg,#c4b5fd,#67e8f9);-webkit-background-clip:text;background-clip:text;color:transparent}
.hero-subtitle{margin:14px 0 0!important;max-width:640px;color:#cbd5e1!important;font-size:1.1rem!important;line-height:1.55}
.hero-meta{display:flex;gap:8px;flex-wrap:wrap;margin-top:20px}
.hero-meta span{padding:7px 12px;border-radius:999px;background:rgba(2,6,23,.55);border:1px solid rgba(148,163,184,.22);color:#e2e8f0;font-size:.78rem;font-weight:650;white-space:nowrap}
.hero-panel{flex:1;min-width:270px;max-width:360px;padding:20px 20px 16px;border-radius:20px;background:rgba(2,6,23,.55);border:1px solid rgba(148,163,184,.22);backdrop-filter:blur(10px)}
.hero-panel h4{margin:0 0 4px!important;font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;color:#94a3b8}
.hero-step{display:flex;gap:12px;padding:11px 0;border-bottom:1px solid rgba(148,163,184,.14)}
.hero-step:last-of-type{border-bottom:0}
.hero-num{flex:0 0 30px;width:30px;height:30px;display:grid;place-items:center;border-radius:9px;background:linear-gradient(135deg,#7c3aed,#0891b2);color:#fff;font-size:.8rem;font-weight:800}
.hero-step b{display:block;color:#f1f5f9;font-size:.92rem}
.hero-step span{color:#94a3b8;font-size:.82rem;line-height:1.4}
.status-pill{display:inline-flex;align-items:center;gap:7px;margin-top:14px;padding:7px 11px;border-radius:999px;font-size:.78rem;font-weight:700}
.status-ok{background:rgba(16,185,129,.14);border:1px solid rgba(52,211,153,.35);color:#a7f3d0}
.status-warn{background:rgba(245,158,11,.13);border:1px solid rgba(251,191,36,.35);color:#fde68a}
.status-note{margin:8px 0 0!important;color:#94a3b8!important;font-size:.78rem!important;line-height:1.45}

/* ---------- feature cards ---------- */
.mini{position:relative;min-height:132px;height:100%;box-sizing:border-box;padding:19px 18px 16px;border:1px solid rgba(148,163,184,.16);border-radius:19px;background:linear-gradient(180deg,rgba(30,41,59,.62),rgba(15,23,42,.58));box-shadow:0 14px 34px rgba(0,0,0,.18);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);transition:transform .18s ease,border-color .18s ease,box-shadow .18s ease;animation:rise .5s ease both;overflow:hidden}
.mini::before{content:"";position:absolute;left:0;right:0;top:0;height:3px;background:linear-gradient(90deg,#7c3aed,#22d3ee);opacity:.85}
.mini:hover{transform:translateY(-3px);border-color:rgba(167,139,250,.5);box-shadow:0 20px 44px rgba(0,0,0,.28)}
.mini-icon{width:46px;height:46px;display:grid;place-items:center;border-radius:13px;font-size:22px;line-height:1;background:linear-gradient(135deg,rgba(124,58,237,.38),rgba(34,211,238,.22));border:1px solid rgba(255,255,255,.12)}
.mini-title{font-weight:800;margin:12px 0 4px;color:#f1f5f9;font-size:1.02rem}
.mini-text{color:#a8b6cc;font-size:.85rem;line-height:1.5}
.label{color:#8fa0b8;font-size:.72rem;text-transform:uppercase;letter-spacing:.1em;font-weight:800}
.workspace-card,.doctor-panel{padding:22px;border:1px solid rgba(148,163,184,.16);border-radius:24px;background:linear-gradient(180deg,rgba(30,41,59,.5),rgba(15,23,42,.52));box-shadow:0 18px 44px rgba(0,0,0,.16);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);animation:rise .5s ease both}
.workspace-card h3,.doctor-panel h3{margin-top:6px!important;font-size:1.3rem}
.workspace-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;flex-wrap:wrap}
.chip-row{display:flex;gap:7px;flex-wrap:wrap;margin:10px 0 4px}
.chip{padding:6px 10px;border-radius:999px;background:rgba(2,6,23,.55);border:1px solid rgba(148,163,184,.2);color:#cbd5e1;font-size:.76rem;font-weight:650}
.stat-strip{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0 2px}
.stat-strip span{padding:6px 10px;border-radius:9px;background:rgba(2,6,23,.5);border:1px solid rgba(148,163,184,.16);color:#94a3b8;font-size:.76rem}
.stat-strip b{color:#e2e8f0}
.empty-state{margin-top:16px;padding:16px 17px;border-radius:16px;background:rgba(34,211,238,.06);border:1px dashed rgba(103,232,249,.35);color:#cbd5e1;font-size:.88rem;line-height:1.55}
.empty-state b{color:#fff}
div[data-testid="stTextArea"] textarea{font-family:"JetBrains Mono","Cascadia Code","Consolas",monospace!important;font-size:13.5px!important;line-height:1.6!important;background:rgba(2,6,23,.9)!important;border-radius:16px!important;border:1px solid rgba(148,163,184,.2)!important;color:#eef2ff!important}
div[data-testid="stTextArea"] textarea:focus{border-color:rgba(34,211,238,.7)!important;box-shadow:0 0 0 1px rgba(34,211,238,.2),0 0 28px rgba(34,211,238,.1)!important}
.stButton>button,.stDownloadButton>button{min-height:50px;border-radius:14px!important;font-weight:750!important;font-size:.95rem!important;border:1px solid rgba(148,163,184,.22)!important;background:rgba(255,255,255,.05)!important;color:#eef2ff!important;transition:transform .15s ease,border-color .15s ease,box-shadow .15s ease}
.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-1px);border-color:rgba(167,139,250,.55)!important}
button[kind="primary"]{background:linear-gradient(135deg,#7c3aed,#0891b2)!important;border:0!important;color:#fff!important;box-shadow:0 14px 32px rgba(124,58,237,.32)}
button[kind="primary"]:hover{box-shadow:0 18px 38px rgba(124,58,237,.42)}
.stButton>button:disabled,.stDownloadButton>button:disabled{opacity:.45}
/* sidebar controls */
section[data-testid="stSidebar"] label{color:#cbd5e1!important;font-weight:700!important}
section[data-testid="stSidebar"] [data-testid="stSelectbox"]>div>div{background:rgba(2,6,23,.6)!important;border:1px solid rgba(148,163,184,.22)!important;border-radius:12px!important;color:#eef2ff!important}
section[data-testid="stSidebar"] [data-testid="stSelectbox"] span{color:#eef2ff!important}
section[data-testid="stSidebar"] [data-testid="stSelectbox"] svg{color:#94a3b8!important}
.sidebar-brand{display:flex;align-items:center;gap:12px;padding:6px 2px 14px}
.sidebar-logo{flex:0 0 46px;width:46px;height:46px;display:grid;place-items:center;border-radius:14px;font-size:23px;background:linear-gradient(135deg,#7c3aed,#0891b2);box-shadow:0 10px 24px rgba(124,58,237,.35)}
.sidebar-brand b{display:block;color:#fff;font-size:1.15rem;letter-spacing:-.02em}
.sidebar-brand span{color:#94a3b8;font-size:.78rem}
.sidebar-section{margin:16px 0 8px;font-size:.72rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:#8fa0b8}
.model-card{margin-top:16px;padding:14px;border-radius:15px;background:rgba(2,6,23,.55);border:1px solid rgba(148,163,184,.18)}
.model-card .label{margin-bottom:5px}
.model-card b{color:#f1f5f9;font-size:.9rem;word-break:break-all}
.model-card p{margin:6px 0 0!important;color:#94a3b8!important;font-size:.78rem!important;line-height:1.45}
/* tabs + results */
div[data-testid="stTabs"]{margin-top:6px}
div[data-baseweb="tab-list"]{gap:6px;padding:6px;border-radius:16px;background:rgba(2,6,23,.6);border:1px solid rgba(148,163,184,.16);overflow-x:auto}
button[data-baseweb="tab"]{border-radius:11px!important;padding:9px 14px!important;color:#a8b6cc!important;font-weight:700!important}
button[data-baseweb="tab"][aria-selected="true"]{background:linear-gradient(135deg,#7c3aed,#0891b2)!important;color:#fff!important}
div[data-testid="stCodeBlock"] pre,div[data-testid="stCodeBlock"] code{border-radius:14px!important}
.result-head{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin:28px 0 14px;padding:16px 20px;border-radius:18px;border:1px solid rgba(148,163,184,.16);border-left:4px solid #22d3ee;background:linear-gradient(90deg,rgba(124,58,237,.14),rgba(15,23,42,.5))}
.result-title{font-size:1.25rem;font-weight:850;color:#fff}
.pill{padding:7px 12px;border-radius:999px;background:rgba(16,185,129,.12);border:1px solid rgba(52,211,153,.28);color:#a7f3d0;font-size:.78rem;font-weight:750;white-space:nowrap}
.pill-amber{background:rgba(245,158,11,.13);border-color:rgba(251,191,36,.35);color:#fde68a}
.pill-red{background:rgba(239,68,68,.13);border-color:rgba(248,113,113,.4);color:#fecaca}
.scan-panel{margin-top:16px;padding:17px;border-radius:18px;background:rgba(2,6,23,.58);border:1px solid rgba(148,163,184,.15);backdrop-filter:blur(10px)}
.scan-ok{color:#a7f3d0;padding:11px 13px;border-radius:12px;background:rgba(16,185,129,.09);border:1px solid rgba(52,211,153,.18);font-size:.9rem}
div[data-testid="stMetric"]{background:rgba(255,255,255,.04);border:1px solid rgba(148,163,184,.15);border-radius:14px;padding:10px 12px}
div[data-testid="stMetric"] label{color:#94a3b8!important}
div[data-testid="stMetric"] [data-testid="stMetricValue"]{color:#fff!important}
.footer{border-top:1px solid rgba(148,163,184,.15);margin-top:36px;padding:20px 4px 8px;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;text-align:left;color:#7c8aa5;font-size:.78rem}
.footer b{color:#cbd5e1}
/* chat dock */
div[data-testid="stBottom"]{z-index:960!important}
div[data-testid="stBottomBlockContainer"]{z-index:960!important;background:transparent!important;padding:0 0 45px!important}
div[data-testid="stBottom"]>div{background:transparent!important}
div[data-testid="stChatInput"]{max-width:900px;margin:0 auto;position:relative;z-index:960;border-radius:20px!important;border:1px solid rgba(96,165,250,.42)!important;background:linear-gradient(135deg,rgba(30,64,175,.42),rgba(88,28,135,.3) 55%,rgba(8,13,26,.95))!important;box-shadow:0 20px 60px rgba(0,0,0,.5),0 0 46px rgba(59,130,246,.16);backdrop-filter:blur(26px);-webkit-backdrop-filter:blur(26px)}
div[data-testid="stChatInput"]:focus-within{border-color:rgba(96,165,250,.75)!important;box-shadow:0 20px 60px rgba(0,0,0,.5),0 0 60px rgba(59,130,246,.3)}
div[data-testid="stChatInput"]::before{content:"💬";position:absolute;left:16px;top:50%;transform:translateY(-50%);font-size:15px;opacity:.85;pointer-events:none;z-index:2}
div[data-testid="stChatInput"]>div{background:transparent!important}
div[data-testid="stChatInput"] textarea{background:transparent!important;color:#eef2ff!important;padding-left:32px!important}
div[data-testid="stChatInput"] textarea::placeholder{color:#93a3bd!important}
div[data-testid="stChatInput"] button{color:#93c5fd!important;background:rgba(96,165,250,.12)!important;border-radius:12px!important}
.ask-label{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:4px 4px 12px;color:#cbd5e1}
.ask-label strong{color:#f1f5f9;font-size:1.05rem}
.ask-label span{color:#7c8aa5;font-size:.78rem}
@media(max-width:900px){
  .block-container{padding-left:1rem;padding-right:1rem}
  .hero{flex-direction:column;padding:28px 24px}
  .hero-panel{max-width:none}
  .hero-title{font-size:2.5rem!important}
  section[data-testid="stSidebar"]{width:300px!important}
  div[data-testid="stChatInput"]{max-width:calc(100vw - 24px)}
}
@media(max-width:480px){
  .hero{padding:24px 20px;border-radius:22px}
  .hero-title{font-size:2.05rem!important}
  .hero-subtitle{font-size:1rem!important}
  .workspace-card,.doctor-panel{padding:17px}
  .topbar-pill{display:none}
}
</style>
""", unsafe_allow_html=True)


def api_key():
    try:
        key = str(st.secrets.get("GROQ_API_KEY", "")).strip()
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("GROQ_API_KEY", "").strip()


@st.cache_resource(show_spinner=False)
def client():
    key = api_key()
    return Groq(api_key=key) if key else None


def local_scan(code, language):
    findings = {"errors": [], "warnings": [], "info": []}
    if not code.strip():
        findings["warnings"].append("No code has been entered.")
        return findings
    lines = code.splitlines()
    long_lines = [str(i + 1) for i, x in enumerate(lines) if len(x) > 120]
    if long_lines:
        findings["warnings"].append("Long lines detected at line(s): " + ", ".join(long_lines[:10]))
    if len(lines) > 400:
        findings["warnings"].append(f"Large snippet detected ({len(lines)} lines). Smaller modules can produce more focused diagnoses.")
    if language in {"Python","C++","C","C#","Java","JavaScript","TypeScript","PHP","Go","Rust"}:
        pairs={"(":")","[":"]","{":"}"}; stack=[]; quote=None; escaped=False
        for ch in code:
            if quote:
                if escaped: escaped=False
                elif ch=='\\': escaped=True
                elif ch==quote: quote=None
                continue
            if ch in "'\"`": quote=ch
            elif ch in pairs: stack.append(ch)
            elif ch in pairs.values():
                if not stack or pairs[stack[-1]] != ch:
                    findings["errors"].append(f"Possibly unbalanced delimiter near '{ch}'."); break
                stack.pop()
        if stack: findings["errors"].append("Possibly unclosed delimiter(s): " + " ".join(stack))
    low=code.lower()
    if re.search(r"(?i)(api[_-]?key|password|secret[_-]?key)\s*=\s*['\"]", code):
        findings["warnings"].append("Possible hard-coded credential/secret detected. Use environment variables or a secret manager.")
    if language == "SQL" and re.search(r"(?i)\b(or|and)\s+1\s*=\s*1\b", code):
        findings["warnings"].append("SQL contains a tautological condition. If input is user-controlled, use parameterized queries.")
    if language in {"Python","JavaScript","TypeScript"} and re.search(r"\beval\s*\(", code):
        findings["warnings"].append("eval() detected; it can introduce serious security and maintainability risks.")
    if "todo" in low or "fixme" in low: findings["info"].append("TODO/FIXME marker detected.")
    findings["info"].append(f"Local scan completed for {language}.")
    return findings


def extract(text, heading, next_headings):
    stop = "|".join(re.escape(x) for x in next_headings)
    m = re.search(rf"(?is)^##\s*{re.escape(heading)}\s*$\n?(.*?)(?=^##\s*(?:{stop})\s*$|\Z)", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def fixed_code(text):
    m=re.search(r"```[^\n]*\n(.*?)```", text, re.S)
    return m.group(1).strip() if m else text.strip()


def analyze(code, language, mode):
    scan=local_scan(code, language)
    scan_text="\n".join(f"- {x}" for group in scan.values() for x in group) or "- No local findings."
    prompt=f'''You are CodeDoctor, an expert software engineer and debugging mentor.

Language: {language}
Mode: {mode}

Local scan:
{scan_text}

Code:
```{language.lower()}
{code}
```

Analyze the supplied code. Do not pretend to execute it. Do not invent runtime/compiler results. If context is missing, say so.
Return EXACTLY these headings:

## Diagnosis
## Root Cause
## Fixed Code
## Explanation
## Improvements
## Tests
## Verdict

Under Fixed Code provide a complete corrected version of the supplied code when a fix is possible. Under Verdict use exactly HEALTHY, NEEDS FIXES, or CRITICAL ISSUES.'''
    c=client()
    if not c: raise RuntimeError("GROQ_API_KEY is not configured.")
    r=c.chat.completions.create(model=MODEL_NAME,messages=[
        {"role":"system","content":"You are CodeDoctor: precise, practical, security-aware, and beginner-friendly."},
        {"role":"user","content":prompt}],temperature=.2,max_completion_tokens=10000)
    return r.choices[0].message.content, scan


def ask(question, code, language, report):
    c=client()
    if not c: raise RuntimeError("GROQ_API_KEY is not configured.")
    prompt=f'''Continue this CodeDoctor session.
Language: {language}
Current code:
```{language.lower()}
{code}
```
Previous report:
{report[-12000:] if report else "No report yet."}

User question: {question}
Answer directly and accurately. Explain reasoning. Include corrected code when useful. Never claim that you executed the code.'''
    r=c.chat.completions.create(model=MODEL_NAME,messages=[
        {"role":"system","content":"You are CodeDoctor, an expert programming mentor."},
        {"role":"user","content":prompt}],temperature=.25,max_completion_tokens=7000)
    return r.choices[0].message.content


if "analysis" not in st.session_state: st.session_state.analysis=""
if "scan" not in st.session_state: st.session_state.scan={}
if "chat" not in st.session_state: st.session_state.chat=[]

with st.sidebar:
    st.markdown('<div class="sidebar-brand"><div class="sidebar-logo">🩺</div><div><b>CodeDoctor</b><span>AI-powered coding clinic</span></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section">Setup</div>', unsafe_allow_html=True)
    language=st.selectbox("Programming language", LANGUAGES)
    mode=st.selectbox("Doctor mode", list(MODES))
    st.markdown('<div class="sidebar-section">Actions</div>', unsafe_allow_html=True)
    if st.button("💡 Load example", use_container_width=True):
        st.session_state.code_editor = SAMPLES.get(language, "// Paste your code here")
        st.rerun()
    if st.button("🧹 Clear workspace", use_container_width=True):
        st.session_state.analysis=""; st.session_state.scan={}; st.session_state.chat=[]
        st.rerun()
    _key_ok = bool(api_key())
    st.markdown(
        f"""<div class="model-card"><div class="label">Powered by Groq</div><b>{MODEL_NAME}</b>
        <p>{'● API key configured — diagnosis is ready.' if _key_ok else '● API key not set — add GROQ_API_KEY in Secrets. Quick Scan works without a key.'}</p></div>""",
        unsafe_allow_html=True,
    )
    

st.markdown(
    """<div class="topbar"><div class="topbar-left"><span class="topbar-dot"></span>CODEDOCTOR &nbsp;·&nbsp; AI CODING CLINIC</div><div class="topbar-pill">Powered by <b>Groq</b> &nbsp;·&nbsp; GPT-OSS-120B</div></div>
    <div class="hero">
        <div class="hero-main">
            <p class="hero-eyebrow">Your AI-powered coding clinic</p>
            <h1 class="hero-title">Code<span>Doctor</span></h1>
            <p class="hero-subtitle">Diagnose bugs. Understand code. Ship better software — with a clear root cause, a corrected version, and tests you can trust.</p>
            <div class="hero-meta">
                <span>🐛 Debugging</span><span>🧠 Explanation</span><span>⚡ Optimization</span><span>🔒 Security</span><span>🧪 Testing</span>
            </div>
        </div>
        <div class="hero-panel">
            <h4>How it works</h4>
            <div class="hero-step"><div class="hero-num">1</div><div><b>Paste your code</b><span>Pick a language, or load a built-in example.</span></div></div>
            <div class="hero-step"><div class="hero-num">2</div><div><b>Scan or diagnose</b><span>Quick Scan is instant and needs no key. Full Diagnosis uses Groq.</span></div></div>
            <div class="hero-step"><div class="hero-num">3</div><div><b>Fix, learn, ask</b><span>Review the fixed code, then ask follow-up questions.</span></div></div>
            <span class="status-pill status-ok" id="hero-status-ok">● Groq ready</span>
            <span class="status-pill status-warn" id="hero-status-warn">● Groq key not set</span>
            <p class="status-note">Your code is never executed. Analysis is static checks plus model reasoning only.</p>
        </div>
    </div>""",
    unsafe_allow_html=True,
)

_hero_ok = bool(api_key())
st.markdown(f"<style>{'#hero-status-warn{display:none!important}' if _hero_ok else '#hero-status-ok{display:none!important}'}</style>", unsafe_allow_html=True)
features=[("🐛","Find Bugs","Detect likely errors and explain their root cause."),("🧠","Understand","Turn confusing code into clear explanations."),("⚡","Improve","Get cleaner and more efficient implementations."),("🧪","Test","Generate useful tests and edge cases.")]
cols=st.columns(4)
for col,(icon,title,desc) in zip(cols,features):
    with col: st.markdown(f'<div class="mini"><div class="mini-icon">{icon}</div><div class="mini-title">{title}</div><div class="mini-text">{desc}</div></div>',unsafe_allow_html=True)

st.markdown("<div style='height:18px'></div>",unsafe_allow_html=True)

left, right = st.columns([1.45, 0.65], gap="large")

with left:
    st.markdown(
        '<div class="workspace-card"><div class="workspace-head"><div><div class="label">Code workspace</div><h3>💻 Paste your code</h3></div><div class="chip-row"><span class="chip">12 languages</span><span class="chip">6 doctor modes</span></div></div>',
        unsafe_allow_html=True,
    )

    code = st.text_area(
        "Code",
        height=450,
        placeholder="Paste your code here...",
        label_visibility="collapsed",
        key="code_editor",
    )

    _lines = len(code.splitlines()) if code.strip() else 0
    st.markdown(f'<div class="stat-strip"><span><b>{_lines}</b> lines</span><span><b>{len(code)}</b> characters</span><span>Language: <b>{language}</b></span><span>Mode: <b>{mode}</b></span></div>', unsafe_allow_html=True)
    a, b, c = st.columns([2.15, 1, 1])
    with a:
        diagnose = st.button("🩺 Diagnose My Code", type="primary", use_container_width=True)
    with b:
        quick = st.button("🔎 Quick Scan", use_container_width=True)
    with c:
        ext = {"Python":"py","C++":"cpp","C":"c","C#":"cs","Java":"java","JavaScript":"js","TypeScript":"ts","PHP":"php","SQL":"sql","HTML/CSS":"html","Go":"go","Rust":"rs"}.get(language,"txt")
        st.download_button(
            "⬇️ Fixed Code",
            data=fixed_code(extract(st.session_state.analysis,"Fixed Code",["Explanation","Improvements","Tests","Verdict"])),
            file_name=f"codedoctor_fixed.{ext}",
            mime="text/plain",
            use_container_width=True,
            disabled=not st.session_state.analysis,
        )

    if not st.session_state.analysis and not st.session_state.scan and not quick:
        st.markdown('<div class="empty-state"><b>Ready when you are.</b><br>Paste your code above, then run <b>Quick Scan</b> for instant static checks — or <b>Diagnose My Code</b> for the full Groq report. No key is needed for Quick Scan.</div>', unsafe_allow_html=True)

    if quick:
        st.session_state.scan = local_scan(code, language)
        st.session_state.scan_open = True

    if st.session_state.get("scan_open") and st.session_state.scan:
        s = st.session_state.scan
        errors, warnings, info = s.get("errors",[]), s.get("warnings",[]), s.get("info",[])
        st.markdown('<div class="scan-panel">', unsafe_allow_html=True)
        q1,q2,q3 = st.columns(3)
        q1.metric("Potential errors",len(errors))
        q2.metric("Warnings",len(warnings))
        q3.metric("Notes",len(info))
        if not errors and not warnings:
            st.markdown('<div class="scan-ok">✓ Quick Scan complete — no obvious static issues were detected.</div>', unsafe_allow_html=True)
        for item in errors: st.error(item)
        for item in warnings: st.warning(item)
        for item in info: st.info(item)
        st.markdown("</div>", unsafe_allow_html=True)

    if diagnose:
        if not code.strip():
            st.warning("Paste some code first.")
        elif not api_key():
            st.error("GROQ_API_KEY is not configured. Add it in Streamlit Cloud → Settings → Secrets.")
        else:
            try:
                with st.spinner("🩺 CodeDoctor is examining your code..."):
                    report, scan = analyze(code, language, MODES[mode])
                st.session_state.analysis = report
                st.session_state.scan = scan
                st.session_state.scan_open = True
                st.success("Diagnosis complete.")
            except Exception as e:
                st.error(f"CodeDoctor could not complete the analysis: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="doctor-panel"><div class="label">Your check-up</div><h3>🩺 Current setup</h3>', unsafe_allow_html=True)
    st.markdown(
        f"""<div class="mini">
        <div class="label">Language</div>
        <div style="font-size:21px;font-weight:800;margin:5px 0 16px">{language}</div>
        <div class="label">Mode</div>
        <div style="font-size:14px;font-weight:700;margin:5px 0 16px">{mode}</div>
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown("### ✨ Every full report includes")
    for x in ["Diagnosis and root cause","Complete corrected code","Beginner-friendly explanation","Performance and security improvements","Tests and edge cases"]:
        st.markdown("• " + x)
    if st.session_state.scan:
        s = st.session_state.scan
        st.markdown("### 🔎 Latest scan")
        m1,m2 = st.columns(2)
        m1.metric("Errors",len(s.get("errors",[])))
        m2.metric("Warnings",len(s.get("warnings",[])))
    st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.analysis:
    report = st.session_state.analysis
    _verdict = extract(report, "Verdict", []).strip().upper()
    _pill_cls = "pill" if _verdict == "HEALTHY" else ("pill pill-amber" if _verdict == "NEEDS FIXES" else ("pill pill-red" if _verdict == "CRITICAL ISSUES" else "pill"))
    _pill_txt = f"● Verdict: {_verdict.title()}" if _verdict else "● Analysis ready"
    st.markdown(f'<div class="result-head"><div class="result-title">🩺 Doctor\'s Report</div><div class="{_pill_cls}">{_pill_txt}</div></div>', unsafe_allow_html=True)
    tabs = st.tabs(["🩻 Diagnosis","🛠️ Fixed Code","🧠 Explanation","⚡ Improvements","🧪 Tests","📋 Full Report"])
    with tabs[0]:
        st.markdown("### Diagnosis")
        st.markdown(extract(report,"Diagnosis",["Root Cause","Fixed Code"]) or "No diagnosis section returned.")
        st.markdown("### Root Cause")
        st.markdown(extract(report,"Root Cause",["Fixed Code"]) or "No root-cause section returned.")
    with tabs[1]:
        st.code(fixed_code(extract(report,"Fixed Code",["Explanation","Improvements","Tests","Verdict"])),language=language.lower())
    with tabs[2]:
        st.markdown(extract(report,"Explanation",["Improvements","Tests","Verdict"]) or report)
    with tabs[3]:
        st.markdown(extract(report,"Improvements",["Tests","Verdict"]) or "No improvement section returned.")
    with tabs[4]:
        st.markdown(extract(report,"Tests",["Verdict"]) or "No tests section returned.")
    with tabs[5]:
        st.markdown(report)

# Chat history renders in-flow, in the normal page scroll, directly above
# the input — no floating/fixed panel, no unfolding overlay.
if st.session_state.chat:
    st.markdown(
        f'<div class="ask-label"><strong>💬 Ask CodeDoctor</strong>'
        f'<span>{len(st.session_state.chat)} message(s)</span></div>',
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        for m in st.session_state.chat:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

question = st.chat_input("Ask about your code, bug, fix, or diagnosis...")

if question:
    st.session_state.chat.append({"role":"user","content":question})
    try:
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("CodeDoctor is thinking..."):
                reply = ask(question,code,language,st.session_state.analysis)
            st.markdown(reply)
        st.session_state.chat.append({"role":"assistant","content":reply})
        st.rerun()
    except Exception as e:
        reply = f"I couldn't answer that right now: {e}"
        st.session_state.chat.append({"role":"assistant","content":reply})
        st.error(reply)

st.markdown('<div class="footer"><div><b>CodeDoctor</b> &nbsp;·&nbsp; AI-assisted debugging and code review, powered by Groq</div><div>Your code is never executed &nbsp;·&nbsp; Keep API keys out of source code</div></div>',unsafe_allow_html=True)
