import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
import random
import math

st.set_page_config(page_title="HomeBudget", page_icon="🏠", layout="centered")

MODES = {
    "Dark": {
        "bg": "#040814",
        "bg2": "#0B1220",
        "card": "rgba(15, 23, 42, 0.72)",
        "text": "#F8FAFC",
        "muted": "#94A3B8",
        "border": "rgba(148, 163, 184, 0.24)",
    },
    "Light": {
        "bg": "#F5F7FB",
        "bg2": "#FFFFFF",
        "card": "rgba(255,255,255,0.84)",
        "text": "#0F172A",
        "muted": "#475569",
        "border": "rgba(15, 23, 42, 0.10)",
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

def money(x):
    return f"${x:,.2f}"

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

if "profiles" not in st.session_state:
    st.session_state["profiles"] = {"Julius": {}, "Peyton": {}}

if "affirmations" not in st.session_state:
    st.session_state["affirmations"] = DEFAULT_AFFIRMATIONS.copy()

if "current_affirmation" not in st.session_state:
    st.session_state["current_affirmation"] = DEFAULT_AFFIRMATIONS[0]

if "force_random_affirmation" not in st.session_state:
    st.session_state["force_random_affirmation"] = False

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
        if st.button("Random"):
            st.session_state["current_affirmation"] = random.choice(st.session_state["affirmations"])
    with c2:
        if st.button("Next"):
            current = st.session_state["current_affirmation"]
            vals = st.session_state["affirmations"]
            if current in vals:
                idx = vals.index(current)
                st.session_state["current_affirmation"] = vals[(idx + 1) % len(vals)]
            else:
                st.session_state["current_affirmation"] = vals[0]

months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
current_month = st.selectbox("Month", months, index=months.index(date.today().strftime("%B")))
year = date.today().year
month_key = f"{year}-{current_month}"

profile_store = st.session_state["profiles"][profile]

if month_key not in profile_store:
    profile_store[month_key] = {
        "income": 5833.33 if profile == "Julius" else 4500.0,
        "bills": [
            {"name": "Rent", "amount": 1275.0 if profile == "Julius" else 1200.0, "due": date.today(), "paid": False},
            {"name": "Phone", "amount": 200.0 if profile == "Julius" else 150.0, "due": date.today(), "paid": False},
            {"name": "Water & Electricity", "amount": 180.0, "due": date.today(), "paid": False},
            {"name": "Groceries", "amount": 600.0 if profile == "Julius" else 500.0, "due": date.today(), "paid": False},
        ],
        "savings": {
            "Rainy Day": {"goal": 10000.0, "balance": 2000.0, "monthly": 500.0},
            "Vehicle": {"goal": 30000.0, "balance": 5000.0, "monthly": 1000.0},
            "Vacation": {"goal": 5000.0, "balance": 1000.0, "monthly": 300.0},
        },
        "sinking": {
            "Christmas": 100.0,
            "Birthdays": 75.0,
            "Car Maintenance": 50.0,
            "Insurance": 120.0,
        },
        "net_worth": {"Cash": 2000.0, "Savings": 5000.0, "Vehicle": 15000.0, "Debt": 0.0},
    }

month_data = profile_store[month_key]
m = MODES[mode]
affirmation = st.session_state["current_affirmation"]

st.markdown(
    f"""
    <div class="glass-card">
        <div class="hero-title">🏠 HomeBudget</div>
        <div class="hero-sub">{profile} • {current_month} • {mode} mode • {theme_name}</div>
        <div class="pill-row">
            <span class="pill active">{theme_name} accent</span>
            <span class="pill">{mode} mode</span>
            <span class="pill">Mobile ready</span>
            <span class="pill">No ads</span>
        </div>
        <div class="affirmation-card">
            <div class="tiny-label">Affirmation</div>
            <div>{affirmation}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown("### Monthly payoff")

income = st.number_input("Monthly take-home pay", min_value=0.0, step=100.0, value=month_data["income"])
month_data["income"] = income

st.markdown("#### Bills")
bills_total = 0.0
paid_total = 0.0
for i, bill in enumerate(month_data["bills"]):
    c1, c2, c3 = st.columns([3, 2, 1])
    with c1:
        bill["name"] = st.text_input("Bill", value=bill["name"], key=f"{profile}_{month_key}_billname_{i}")
    with c2:
        bill["amount"] = st.number_input("Amount", min_value=0.0, step=10.0, value=bill["amount"], key=f"{profile}_{month_key}_billamt_{i}")
    with c3:
        bill["paid"] = st.checkbox("Paid", value=bill["paid"], key=f"{profile}_{month_key}_billpaid_{i}")
    bills_total += bill["amount"]
    if bill["paid"]:
        paid_total += bill["amount"]

savings_monthly = sum(v["monthly"] for v in month_data["savings"].values())
left_to_assign = income - bills_total - savings_monthly
cash_flow = income - bills_total

c1, c2, c3, c4 = st.columns(4)
c1.metric("Monthly income", money(income))
c2.metric("Budget left to assign", money(left_to_assign))
c3.metric("Total bills", money(bills_total))
c4.metric("Monthly savings", money(savings_monthly))

st.markdown(
    f"""
    <div style="margin-top:0.5rem; padding:0.85rem 1rem; border-radius:18px; border:1px solid {accent}66; background: {accent}12; color: {m['text']};">
        <b>Monthly cash flow:</b> {money(cash_flow)} &nbsp;&nbsp; <b>Paid bills:</b> {money(paid_total)}
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown("### Savings goals")
for name, info in month_data["savings"].items():
    row1, row2, row3 = st.columns([2, 2, 2])
    with row1:
        info["goal"] = st.number_input(f"{name} goal", min_value=0.0, step=500.0, value=info["goal"], key=f"{profile}_{month_key}_{name}_goal")
    with row2:
        info["balance"] = st.number_input(f"{name} balance", min_value=0.0, step=100.0, value=info["balance"], key=f"{profile}_{month_key}_{name}_balance")
    with row3:
        info["monthly"] = st.number_input(f"{name} monthly", min_value=0.0, step=50.0, value=info["monthly"], key=f"{profile}_{month_key}_{name}_monthly")
    progress = min(info["balance"] / info["goal"], 1.0) if info["goal"] > 0 else 0.0
    st.progress(progress)
    if info["goal"] > 0 and info["monthly"] > 0:
        rem = max(info["goal"] - info["balance"], 0.0)
        months_to_goal = math.ceil(rem / info["monthly"])
        est = date.today() + timedelta(days=30 * months_to_goal)
        st.caption(f"Goal progress: {progress:.0%} • Est. completion: {est.strftime('%b %Y')}")
    else:
        st.caption(f"Goal progress: {progress:.0%}")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown("### Sinking funds")
for fund, amount in list(month_data["sinking"].items()):
    new_amt = st.number_input(fund, min_value=0.0, step=25.0, value=amount, key=f"{profile}_{month_key}_sink_{fund}")
    month_data["sinking"][fund] = new_amt
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown("### Spending insights")

pie_labels = ["Bills"] + [f"{k} savings" for k in month_data["savings"].keys()]
pie_values = [bills_total] + [v["monthly"] for v in month_data["savings"].values()]
fig_pie = px.pie(names=pie_labels, values=pie_values, hole=0.34, color_discrete_sequence=[accent, "#94A3B8", "#60A5FA", "#C084FC"])
fig_pie.update_layout(
    margin=dict(t=20, b=0, l=0, r=0),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color=m["text"],
    showlegend=True,
)
st.plotly_chart(fig_pie, use_container_width=True)

chart = go.Figure()
chart.add_bar(x=[current_month], y=[bills_total], name="Bills", marker_color=accent)
chart.add_bar(x=[current_month], y=[savings_monthly], name="Savings", marker_color="#64748B")
chart.update_layout(
    barmode="group",
    margin=dict(t=10, b=0, l=0, r=0),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color=m["text"],
    height=300,
)
st.plotly_chart(chart, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown("### Month-to-month / YTD")
history_months = []
history_bills = []
history_savings = []
for mk, data in profile_store.items():
    if mk.startswith(str(year)):
        history_months.append(mk.split("-")[1])
        history_bills.append(sum(b["amount"] for b in data["bills"]))
        history_savings.append(sum(v["monthly"] for v in data["savings"].values()))

if history_months:
    hist = go.Figure()
    hist.add_bar(x=history_months, y=history_bills, name="Bills", marker_color="#64748B")
    hist.add_bar(x=history_months, y=history_savings, name="Savings", marker_color=accent)
    hist.update_layout(
        barmode="group",
        margin=dict(t=10, b=0, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=m["text"],
        height=300,
    )
    st.plotly_chart(hist, use_container_width=True)
else:
    st.caption("No month history yet.")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown("### Net worth")
nw = month_data["net_worth"]
a, b, c, d = st.columns(4)
nw["Cash"] = a.number_input("Cash", min_value=0.0, step=100.0, value=nw["Cash"], key=f"{profile}_{month_key}_nw_cash")
nw["Savings"] = b.number_input("Savings", min_value=0.0, step=100.0, value=nw["Savings"], key=f"{profile}_{month_key}_nw_savings")
nw["Vehicle"] = c.number_input("Vehicle", min_value=0.0, step=500.0, value=nw["Vehicle"], key=f"{profile}_{month_key}_nw_vehicle")
nw["Debt"] = d.number_input("Debt", min_value=0.0, step=100.0, value=nw["Debt"], key=f"{profile}_{month_key}_nw_debt")
net_worth = nw["Cash"] + nw["Savings"] + nw["Vehicle"] - nw["Debt"]
st.metric("Net worth", money(net_worth))
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown("### Zero-based check")
assigned = bills_total + savings_monthly
remaining = income - assigned
z1, z2, z3 = st.columns(3)
z1.metric("Income", money(income))
z2.metric("Assigned", money(assigned))
z3.metric("Remaining", money(remaining))
if abs(remaining) < 0.01:
    st.success("This month is a true zero-based budget.")
elif remaining > 0:
    st.info("You still have money to assign.")
else:
    st.error("This budget is overallocated. Reduce spending or savings.")
st.markdown("</div>", unsafe_allow_html=True)
