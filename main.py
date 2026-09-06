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

st.set_page_config(page_title="CodeDoctor", page_icon="🩺", layout="wide", initial_sidebar_state="expanded")

st.markdown(r"""
<style>
/* ---------- base app ---------- */
.stApp{background:radial-gradient(circle at 8% -5%,rgba(124,58,237,.18),transparent 28%),radial-gradient(circle at 92% 3%,rgba(6,182,212,.13),transparent 26%),#070b14;color:#eef2ff}
.block-container{max-width:1480px;padding:1.6rem 2rem 130px}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#0a1020,#070b14);border-right:1px solid rgba(148,163,184,.14)}

/* ---------- native Streamlit chrome: keep it FUNCTIONAL, just visually
   quiet. We do NOT display:none the header — that also removes the
   "expand sidebar" control when the sidebar is collapsed, leaving no way
   back in. Instead we make it transparent and compact, and only hide the
   specific decorative bits (menu, deploy toolbar, gradient bar). ---------- */
header[data-testid="stHeader"]{background:transparent!important;box-shadow:none!important;height:2.6rem!important;min-height:0!important}
header[data-testid="stHeader"] [data-testid="stToolbarActions"]{display:none!important}
header[data-testid="stHeader"] [data-testid="stDecoration"]{display:none!important}
#MainMenu{visibility:hidden!important}
footer{visibility:hidden!important}
/* make sure the collapsed-sidebar reopen control stays visible/clickable above everything */
[data-testid="stSidebarCollapsedControl"]{z-index:999999!important;opacity:1!important;visibility:visible!important}

/* ---------- hero ---------- */
.hero{position:relative;overflow:hidden;isolation:isolate;padding:28px 32px 25px;margin:0 0 18px;border-radius:26px;border:1px solid rgba(139,92,246,.25);background:radial-gradient(circle at 84% 15%,rgba(34,211,238,.13),transparent 25%),radial-gradient(circle at 18% 110%,rgba(139,92,246,.13),transparent 34%),rgba(15,23,42,.72);box-shadow:0 22px 60px rgba(0,0,0,.25);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px)}
.hero:after{content:"";position:absolute;width:170px;height:170px;right:-65px;top:-80px;border-radius:50%;background:rgba(139,92,246,.11);filter:blur(4px);z-index:-1}
.hero-row{display:flex;align-items:center;gap:17px;min-width:0}.hero-icon{flex:0 0 62px;width:62px;height:62px;display:grid;place-items:center;border-radius:18px;font-size:31px;background:linear-gradient(135deg,rgba(139,92,246,.3),rgba(34,211,238,.17));border:1px solid rgba(255,255,255,.1)}.hero-copy{min-width:0}
.hero-title{margin:0!important;padding:0!important;font-size:clamp(2.1rem,5vw,3.45rem)!important;line-height:1.02!important;font-weight:850!important;letter-spacing:-.05em}.hero-title span{background:linear-gradient(90deg,#c4b5fd,#67e8f9);-webkit-background-clip:text;background-clip:text;color:transparent}.hero-subtitle{margin-top:8px;color:#9aa8bd;font-size:.98rem;line-height:1.45}
.badges{display:flex;gap:7px;flex-wrap:wrap;margin-top:17px}.badge{padding:6px 10px;border-radius:999px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);color:#cbd5e1;font-size:.76rem;white-space:nowrap}

/* ---------- glass cards ---------- */
.mini{min-height:112px;height:100%;box-sizing:border-box;padding:15px;border:1px solid rgba(148,163,184,.14);border-radius:17px;background:rgba(15,23,42,.56);box-shadow:0 12px 30px rgba(0,0,0,.12);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);transition:transform .15s ease,border-color .15s ease}
.mini:hover{transform:translateY(-2px);border-color:rgba(139,92,246,.35)}
.mini-icon{font-size:22px;line-height:1}.mini-title{font-weight:750;margin:6px 0 3px;color:#e2e8f0}.mini-text{color:#94a3b8;font-size:.82rem;line-height:1.42}
.label{color:#94a3b8;font-size:.73rem;text-transform:uppercase;letter-spacing:.09em;font-weight:750}
.workspace-card,.doctor-panel{padding:19px;border:1px solid rgba(148,163,184,.14);border-radius:22px;background:rgba(15,23,42,.48);box-shadow:0 16px 40px rgba(0,0,0,.13);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px)}
.workspace-card h3,.doctor-panel h3{margin-top:5px!important}
div[data-testid="stTextArea"] textarea{font-family:"JetBrains Mono","Cascadia Code","Consolas",monospace!important;font-size:13px!important;line-height:1.55!important;background:rgba(2,6,23,.88)!important;border-radius:15px!important;border:1px solid rgba(148,163,184,.16)!important}
div[data-testid="stTextArea"] textarea:focus{border-color:rgba(139,92,246,.62)!important;box-shadow:0 0 0 1px rgba(139,92,246,.18),0 0 25px rgba(139,92,246,.08)!important}
.stButton>button,.stDownloadButton>button{min-height:43px;border-radius:12px!important;font-weight:650!important;border:1px solid rgba(148,163,184,.15)!important}.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-1px);border-color:rgba(139,92,246,.5)!important}
button[kind="primary"]{background:linear-gradient(135deg,#7c3aed,#0891b2)!important;border:0!important;color:#fff!important;box-shadow:0 10px 28px rgba(124,58,237,.2)}
div[data-baseweb="tab-list"]{gap:5px;padding:6px;border-radius:16px;background:rgba(15,23,42,.72);border:1px solid rgba(148,163,184,.14);overflow-x:auto}button[data-baseweb="tab"]{border-radius:10px!important}
.result-head{display:flex;justify-content:space-between;align-items:center;gap:10px;margin:24px 0 12px}.result-title{font-size:1.16rem;font-weight:800}.pill{padding:6px 10px;border-radius:999px;background:rgba(16,185,129,.09);border:1px solid rgba(52,211,153,.2);color:#a7f3d0;font-size:.75rem;white-space:nowrap}
.scan-panel{margin-top:14px;padding:15px;border-radius:16px;background:rgba(2,6,23,.55);border:1px solid rgba(148,163,184,.13);backdrop-filter:blur(10px)}.scan-ok{color:#a7f3d0;padding:9px 11px;border-radius:11px;background:rgba(16,185,129,.08);border:1px solid rgba(52,211,153,.14)}
.footer{text-align:center;color:#64748b;padding:26px 0 8px;font-size:.76rem}

/* ---------- the REAL st.chat_input, restyled as the floating glass dock ---------- */
div[data-testid="stBottom"]{z-index:960!important}
div[data-testid="stBottomBlockContainer"]{z-index:960!important;background:transparent!important;padding:0 0 18px!important}
div[data-testid="stBottom"]>div{background:transparent!important}
div[data-testid="stChatInput"]{max-width:900px;margin:0 auto;position:relative;z-index:960;border-radius:20px!important;border:1px solid rgba(96,165,250,.38)!important;background:linear-gradient(135deg,rgba(30,64,175,.4),rgba(88,28,135,.28) 55%,rgba(8,13,26,.94))!important;box-shadow:0 20px 60px rgba(0,0,0,.5),0 0 0 1px rgba(96,165,250,.06),0 0 46px rgba(59,130,246,.16);backdrop-filter:blur(26px);-webkit-backdrop-filter:blur(26px);transition:box-shadow .2s ease,border-color .2s ease}
div[data-testid="stChatInput"]:focus-within{border-color:rgba(96,165,250,.7)!important;box-shadow:0 20px 60px rgba(0,0,0,.5),0 0 0 1px rgba(96,165,250,.16),0 0 60px rgba(59,130,246,.3)}
div[data-testid="stChatInput"]::before{content:"💬";position:absolute;left:16px;top:50%;transform:translateY(-50%);font-size:15px;opacity:.85;pointer-events:none;z-index:2}
div[data-testid="stChatInput"] textarea{background:transparent!important;color:#eef2ff!important;padding-left:32px!important}
div[data-testid="stChatInput"] textarea::placeholder{color:#93a3bd!important}
div[data-testid="stChatInput"] button{color:#93c5fd!important;background:rgba(96,165,250,.12)!important;border-radius:12px!important}
div[data-testid="stChatInput"] button:hover{background:rgba(96,165,250,.22)!important}

/* ---------- Ask CodeDoctor label above the in-flow chat history ---------- */
.ask-label{display:flex;align-items:center;justify-content:space-between;padding:2px 4px 10px;color:#cbd5e1}
.ask-label strong{color:#f1f5f9;font-size:1rem}
.ask-label span{color:#7c8aa5;font-size:.78rem}

@media(max-width:900px){.block-container{padding-left:1rem;padding-right:1rem}div[data-testid="stChatInput"]{max-width:calc(100vw - 24px)}}
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
    st.markdown("## 🩺 CodeDoctor")
    st.caption("Your AI-powered coding clinic")
    language=st.selectbox("Programming language", LANGUAGES)
    mode=st.selectbox("Doctor mode", list(MODES))
    st.markdown("---")
    if st.button("💡 Load example", use_container_width=True):
        st.session_state.example=SAMPLES.get(language, "// Paste your code here")
        st.rerun()
    if st.button("🧹 Clear workspace", use_container_width=True):
        st.session_state.analysis=""; st.session_state.scan={}; st.session_state.chat=[]
        st.rerun()
    st.markdown("---")
    

st.markdown(
    """<div class="hero">
        <div class="hero-row">
            <div class="hero-icon">🩺</div>
            <div class="hero-copy">
                <h1 class="hero-title">Code<span>Doctor</span></h1>
                <div class="hero-subtitle">Diagnose bugs. Understand code. Ship better software.</div>
            </div>
        </div>
        <div class="badges">
            <span class="badge">🐛 Debugging</span>
            <span class="badge">🧠 Explanation</span>
            <span class="badge">⚡ Optimization</span>
            <span class="badge">🔒 Security</span>
            <span class="badge">🧪 Testing</span>
        </div>
    </div>""",
    unsafe_allow_html=True,
)

features=[("🐛","Find Bugs","Detect likely errors and explain their root cause."),("🧠","Understand","Turn confusing code into clear explanations."),("⚡","Improve","Get cleaner and more efficient implementations."),("🧪","Test","Generate useful tests and edge cases.")]
cols=st.columns(4)
for col,(icon,title,desc) in zip(cols,features):
    with col: st.markdown(f'<div class="mini"><div class="mini-icon">{icon}</div><div class="mini-title">{title}</div><div class="mini-text">{desc}</div></div>',unsafe_allow_html=True)

st.markdown("<div style='height:18px'></div>",unsafe_allow_html=True)

left, right = st.columns([1.45, 0.65], gap="large")

with left:
    st.markdown(
        '<div class="workspace-card"><div class="label">Code workspace</div><h3>💻 Paste your code</h3>',
        unsafe_allow_html=True,
    )

    default = st.session_state.pop("example", "")
    code = st.text_area(
        "Code",
        value=default,
        height=450,
        placeholder="Paste your code here...",
        label_visibility="collapsed",
        key="code_editor",
    )

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
    st.markdown('<div class="doctor-panel"><div class="label">Doctor settings</div><h3>🩺 Current setup</h3>', unsafe_allow_html=True)
    st.markdown(
        f"""<div class="mini">
        <div class="label">Language</div>
        <div style="font-size:21px;font-weight:800;margin:5px 0 16px">{language}</div>
        <div class="label">Mode</div>
        <div style="font-size:14px;font-weight:700;margin:5px 0 16px">{mode}</div>
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown("### ✨ Report includes")
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
    st.markdown('<div class="result-head"><div class="result-title">🩺 Doctor\'s Report</div><div class="pill">● Analysis ready</div></div>', unsafe_allow_html=True)
    report = st.session_state.analysis
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

st.markdown('<div class="footer">CodeDoctor • AI-assisted debugging and code review • Keep API keys out of source code.</div>',unsafe_allow_html=True)
