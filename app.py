import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
import random

st.set_page_config(page_title="HomeBudget", page_icon="🏠", layout="centered")

MODES = {
    "Dark": {
        "bg": "#040814",
        "bg2": "#0B1220",
        "card": "rgba(15, 23, 42, 0.72)",
        "text": "#F8FAFC",
        "muted": "#94A3B8",
        "border": "rgba(148, 163, 184, 0.24)",
        "input": "rgba(255,255,255,0.04)",
    },
    "Light": {
        "bg": "#F5F7FB",
        "bg2": "#FFFFFF",
        "card": "rgba(255,255,255,0.84)",
        "text": "#0F172A",
        "muted": "#475569",
        "border": "rgba(15, 23, 42, 0.10)",
        "input": "rgba(15,23,42,0.03)",
    },
}

THEMES = {
    "Emerald": "#34D399",
    "Blue": "#60A5FA",
    "Purple": "#C084FC",
}

DEFAULT_AFFIRMATIONS = [
    "Every dollar has a job.",
    "We are building peace, not pressure.",
    "Small progress still counts.",
    "Our budget creates freedom.",
    "We are in control of our money.",
]

def inject_css(mode, accent):
    m = MODES[mode]
    css = f"""
    <style>
    .stApp {{
        background:
            radial-gradient(circle at top left, {accent}22 0%, transparent 28%),
            radial-gradient(circle at top right, #ffffff10 0%, transparent 20%),
            linear-gradient(180deg, {m['bg2']} 0%, {m['bg']} 75%);
        color: {m['text']};
    }}
    div[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {m['bg2']} 0%, {m['bg']} 100%);
    }}
    .glass-card {{
        background: {m['card']};
        border: 1px solid {m['border']};
        border-radius: 26px;
        padding: 1.05rem 1.05rem 1rem 1.05rem;
        box-shadow: 0 18px 50px rgba(0,0,0,0.20);
        backdrop-filter: blur(18px);
        margin-bottom: 1rem;
    }}
    .hero-title {{
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.05;
        margin-bottom: 0.25rem;
        color: {m['text']};
    }}
    .hero-sub {{
        color: {m['muted']};
        font-size: 0.95rem;
        margin-bottom: 0.85rem;
    }}
    .pill-row {{
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-bottom: 0.6rem;
    }}
    .pill {{
        display: inline-block;
        padding: 0.42rem 0.8rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.06);
        border: 1px solid {m['border']};
        color: {m['text']};
        font-size: 0.82rem;
    }}
    .pill.active {{
        border-color: {accent};
        color: {accent};
        box-shadow: 0 0 0 1px {accent}33 inset;
    }}
    .affirmation-card {{
        margin-top: 0.75rem;
        padding: 0.85rem 0.95rem;
        border-radius: 18px;
        border: 1px solid {accent}55;
        color: {m['text']};
        background: linear-gradient(180deg, {accent}18, transparent);
        font-size: 0.95rem;
    }}
    .tiny-label {{
        color: {m['muted']};
        font-size: 0.74rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def money(x):
    return f"${x:,.2f}"

if "profiles" not in st.session_state:
    st.session_state["profiles"] = {"Julius": {}, "Peyton": {}}

if "affirmations" not in st.session_state:
    st.session_state["affirmations"] = DEFAULT_AFFIRMATIONS.copy()

if "current_affirmation" not in st.session_state:
    st.session_state["current_affirmation"] = DEFAULT_AFFIRMATIONS[0]

if "random_affirmation_seed" not in st.session_state:
    st.session_state["random_affirmation_seed"] = 0

with st.sidebar:
    st.markdown("## HomeBudget")
    profile = st.selectbox("Profile", ["Julius", "Peyton"])
    mode = st.radio("Mode", ["Dark", "Light"], horizontal=True)
    theme_name = st.selectbox("Theme", ["Emerald", "Blue", "Purple"])
    accent = THEMES[theme_name]
    inject_css(mode, accent)

    st.markdown("### Profile tools")
    new_aff = st.text_input("Add affirmation", placeholder="We are in control of our money.")
    if new_aff and new_aff not in st.session_state["affirmations"]:
        st.session_state["affirmations"].append(new_aff)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Random affirmation"):
            st.session_state["random_affirmation_seed"] += 1
            st.session_state["current_affirmation"] = random.choice(st.session_state["affirmations"])
    with c2:
        if st.button("Next affirmation"):
            current = st.session_state["current_affirmation"]
            vals = st.session_state["affirmations"]
            if current in vals:
                idx = vals.index(current)
                st.session_state["current_affirmation"] = vals[(idx + 1) % len(vals)]
            else:
                st.session_state["current_affirmation"] = vals[0]

    st.caption("Stored affirmations:")
    st.write(st.session_state["affirmations"])

months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
current_month = st.selectbox("Month", months, index=months.index(date.today().strftime("%B")))
year = date.today().year
month_key = f"{year}-{current_month}"

profile_store = st.session_state["profiles"][profile]

if month_key not in profile_store:
    profile_store[month_key] = {
        "income": 5833.33 if profile == "Julius" else 4500.0,
        "bills": [
            {"name": "Rent", "amount": 1275.0 if profile == "Julius" else 1200.0, "due": date.today(), "paid": False, "notes": "", "auto": True},
            {"name": "Phone", "amount": 200.0 if profile == "Julius" else 150.0, "due": date.today(), "paid": False, "notes": "", "auto": True},
            {"name": "Water & Electricity", "amount": 180.0, "due": date.today(), "paid": False, "notes": "", "auto": False},
            {"name": "Groceries", "amount": 600.0 if profile == "Julius" else 500.0, "due": date.today(), "paid": False, "notes": "", "auto": False},
        ],
        "sav

