import streamlit as st
from transformers import pipeline
import json, os, hashlib
from datetime import datetime

st.set_page_config(page_title="AI News Summarizer", page_icon="📰", layout="wide")

USERS_FILE = "users.json"
st.markdown("""
    <style>
    html, body, [class*="css"] { font-size: 17px !important; }
    textarea { font-size: 16px !important; }
    .stMetric label { font-size: 15px !important; }
    .stMetric [data-testid="stMetricValue"] { font-size: 26px !important; }
    </style>
""", unsafe_allow_html=True)
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "summaries_done" not in st.session_state:
    st.session_state.summaries_done = 0
if "article_text" not in st.session_state:
    st.session_state.article_text = ""
if "load_sample" not in st.session_state:
    st.session_state.load_sample = False

SAMPLE_ARTICLE = """The Reserve Bank of India on Thursday kept its key interest rate unchanged for the third consecutive policy meeting, citing concerns over inflation despite signs of slowing economic growth. The central bank's monetary policy committee voted five to one in favor of holding the repo rate steady, maintaining borrowing costs at their current level. The RBI governor said that while inflation had eased in recent months, it remained above the target range, and premature rate cuts could risk reversing the progress made so far. Economists had been divided ahead of the announcement, with some expecting a modest cut given weaker manufacturing output and slowing consumer spending. Industry bodies expressed disappointment, arguing that lower rates were needed to stimulate investment and job creation."""

# ---------------- Login / Register ----------------
if not st.session_state.logged_in:
    st.title("📰 AI News Summarizer")
    st.caption("Sign in or create an account to start summarizing news articles with deep learning.")
    st.divider()

    left, right = st.columns([1, 1], gap="large")

    with left:
        tab_login, tab_register = st.tabs(["Login", "Register"])

        with tab_login:
            with st.container(border=True):
                users = load_users()
                username = st.text_input("Username", key="login_user")
                password = st.text_input("Password", type="password", key="login_pass")
                st.checkbox("Remember me on this device")
                if st.button("Login", key="login_btn", use_container_width=True):
                    if username in users and users[username] == hash_pw(password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

        with tab_register:
            with st.container(border=True):
                new_user = st.text_input("Choose a username", key="reg_user")
                new_pass = st.text_input("Choose a password", type="password", key="reg_pass")
                confirm_pass = st.text_input("Confirm password", type="password", key="reg_confirm")
                agree = st.checkbox("I agree this is a demo account for project purposes")
                if st.button("Create Account", key="reg_btn", use_container_width=True):
                    users = load_users()
                    if not new_user or not new_pass:
                        st.warning("Please fill in all fields.")
                    elif new_user in users:
                        st.warning("Username already exists.")
                    elif new_pass != confirm_pass:
                        st.warning("Passwords do not match.")
                    elif not agree:
                        st.warning("Please check the agreement box.")
                    else:
                        users[new_user] = hash_pw(new_pass)
                        save_users(users)
                        st.success("Account created! You can log in now.")

    with right:
        with st.container(border=True):
            st.subheader("Why this project?")
            st.write("This tool uses a pretrained deep learning transformer model (DistilBART) to read a full news article and generate a short, fluent, human-like summary — built as an AI Career for Women Engineering Spoke project.")
            st.markdown("✅ Deep learning powered")
            st.markdown("✅ Evaluated with ROUGE metrics")
            st.markdown("✅ Works on real CNN/DailyMail news data")

    st.stop()

# ---------------- Main app ----------------
@st.cache_resource
def load_model():
    return pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", framework="pt")

summarizer = load_model()

top_l, top_r = st.columns([5, 1])
with top_l:
    st.title("📰 AI News Summarizer")
    st.caption(f"Welcome back, **{st.session_state.username}** — paste an article below to generate a summary.")
with top_r:
    st.write("")
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

st.divider()

stat1, stat2, stat3 = st.columns(3)
with stat1:
    with st.container(border=True):
        st.metric("Summaries generated", st.session_state.summaries_done)
with stat2:
    with st.container(border=True):
        st.metric("Model in use", "DistilBART")
with stat3:
    with st.container(border=True):
        st.metric("Avg ROUGE-1 score", "0.401")

st.write("")

# Handle sample-load BEFORE the text_area widget is created
if st.session_state.load_sample:
    st.session_state.article_text = SAMPLE_ARTICLE
    st.session_state.load_sample = False

main_l, main_r = st.columns([3, 1], gap="medium")
with main_l:
    with st.container(border=True):
        st.subheader("Input Article")
        article = st.text_area("Paste your news article here:", height=260,
                                key="article_text", label_visibility="collapsed")
        if article.strip():
            st.caption(f"📝 {len(article.split())} words")
        show_scores = st.checkbox("Show evaluation details after summarizing")
        go = st.button("Summarize Article", use_container_width=True)

with main_r:
    with st.container(border=True):
        st.subheader("Quick Actions")
        if st.button("Load Sample Article", use_container_width=True):
            st.session_state.load_sample = True
            st.rerun()
        st.caption("Loads a real RBI news article to try instantly.")
        st.divider()
        st.markdown("**How it works**")
        st.caption("1. Paste or load an article")
        st.caption("2. Click Summarize Article")
        st.caption("3. Read your AI-generated summary below")

if go:
    if not article.strip():
        st.warning("Please paste an article first.")
    else:
        with st.spinner("Generating summary..."):
            summary = summarizer(article, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
        st.session_state.summaries_done += 1

        with st.container(border=True):
            st.subheader("Generated Summary")
            st.success(summary)
            st.caption(f"Compressed from {len(article.split())} words to {len(summary.split())} words")
            if show_scores:
                st.info("Evaluation metric used in this project: ROUGE-1, ROUGE-2, ROUGE-L (see project report, Chapter 4).")

st.divider()
st.caption(f"© {datetime.now().year} AI News Summarizer — AICW Engineering Spoke Project")