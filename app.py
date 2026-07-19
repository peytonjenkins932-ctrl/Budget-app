import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
import json

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="HomeBudget",
    page_icon="💰",
    layout="centered",
)

# ---------- THEME & STYLING ----------
THEMES = {
    "Emerald": {
        "accent": "#34D399",
        "bg": "#020617",
        "card_bg": "rgba(15, 23, 42, 0.65)",
    },
    "Blue": {
        "accent": "#3B82F6",
        "bg": "#020617",
        "card_bg": "rgba(15, 23, 42, 0.65)",
    },
    "Purple": {
        "accent": "#A855F7",
        "bg": "#020617",
        "card_bg": "rgba(15, 23, 42, 0.65)",
    },
}

def apply_theme(theme_name: str):
    theme = THEMES[theme_name]
    accent = theme["accent"]
    bg = theme["bg"]
    card_bg = theme["card_bg"]

    css = f"""
    <style>
    .stApp {{
        background: radial-gradient(circle at top left, #0F172A 0%, {bg} 40%, #000000 90%);
        color: #E5E7EB;
    }}
    .glass-card {{
        background: {card_bg};
        border-radius: 20px;
        border: 1px solid rgba(148, 163, 184, 0.5);
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(22px);
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .glass-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 26px 70px rgba(15, 23, 42, 0.9);
    }}
    .accent-text {{
        color: {accent};
        font-weight: 600;
    }}
    .pill {{
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        border: 1px solid rgba(148, 163, 184, 0.6);
        font-size: 0.8rem;
        color: #CBD5F5;
    }}
    .pill-strong {{
        border-color: {accent};
        color: {accent};
        font-weight: 600;
    }}
    .affirmation {{
        font-size: 0.95rem;
        font-style: italic;
        color: #A5B4FC;
        margin-top: 0.5rem;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    return accent

# ---------- SAVE/LOAD HOOKS ----------
def load_profiles():
    """
    Load profiles from persistent storage into st.session_state["profiles"].
    Right now, this uses an in-memory default.
    Later, you can hook this into browser local storage or a file/database.
    """
    if "profiles" in st.session_state:
        return

    # Default in-memory initialization
    st.session_state["profiles"] = {
        "Julius": {},
        "Peyton": {},
    }

def save_profiles():
    """
    Save st.session_state["profiles"] to persistent storage.
    For now, this is a placeholder. Later you can connect it to local storage.

    Example for future:
        storage.set(json.dumps(st.session_state["profiles"]))
    """
    # Placeholder: no-op for now
    pass

# ---------- INIT PROFILES ----------
load_profiles()

# Sidebar: profile & theme
with st.sidebar:
    st.markdown("## HomeBudget")
    profile = st.selectbox("Profile", ["Julius", "Peyton"])
    theme_choice = st.selectbox("Theme", ["Emerald", "Blue", "Purple"])
    accent_color = apply_theme(theme_choice)

    # Affirmations
    default_affirmations = [
        "Every dollar we earn moves us closer to freedom.",
        "We are building wealth one wise choice at a time.",
        "Our budget is a tool, not a restriction.",
    ]
    if "affirmations" not in st.session_state:
        st.session_state["affirmations"] = default_affirmations

    st.markdown("### Affirmations")
    affirmation_choice = st.selectbox(
        "Daily affirmation",
        options=st.session_state["affirmations"],
        index=0,
    )
    custom_affirmation = st.text_input(
        "Add your own affirmation",
        value="",
        placeholder="E.g. ‘We deserve financial peace.’",
    )
    if custom_affirmation:
        if custom_affirmation not in st.session_state["affirmations"]:
            st.session_state["affirmations"].append(custom_affirmation)
            affirmation_choice = custom_affirmation
    st.markdown(f"<div class='affirmation'>“{affirmation_choice}”</div>", unsafe_allow_html=True)

# ---------- MONTH SELECTION ----------
months = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
current_month = st.selectbox("Month", months, index=months.index(date.today().strftime("%B")))
year = date.today().year
month_key = f"{year}-{current_month}"

# ---------- PROFILE-SPECIFIC DATA ----------
profile_store = st.session_state["profiles"][profile]

if month_key not in profile_store:
    # Initialize fresh month data for this profile
    default_income = 5833.33 if profile == "Julius" else 4500.0
    profile_store[month_key] = {
        "income": default_income,
        "bills": [],
        "savings": {
            "Rainy Day": {"goal": 10000.0, "balance": 2000.0, "monthly": 500.0},
            "Vehicle": {"goal": 30000.0, "balance": 5000.0, "monthly": 1000.0},
            "Vacation": {"goal": 5000.0, "balance": 1000.0, "monthly": 300.0},
        },
        "sinking_funds": {
            "Christmas": 100.0,
            "Birthdays": 75.0,
            "Car maintenance": 50.0,
            "Insurance": 120.0,
        },
        "net_worth": {
            "Cash": 2000.0,
            "Savings": 5000.0,
            "Vehicle": 15000.0,
            "Debt": 0.0,
        },
    }

month_data = profile_store[month_key]

# ---------- DASHBOARD ----------
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.markdown("### 🏠 Dashboard")

monthly_income = st.number_input(
    "Monthly take-home pay",
    min_value=0.0,
    step=100.0,
    value=month_data["income"],
    key=f"income_{profile}_{month_key}",
)
month_data["income"] = monthly_income

# Bills setup
st.markdown("#### 💸 Bills overview")

if not month_data["bills"]:
    # Seed recurring bills (per profile, per month)
    month_data["bills"] = [
        {"name": "Rent", "amount": 1275.0, "due": date(year, date.today().month, 1), "paid": False, "variable": False},
        {"name": "Phone", "amount": 200.0, "due": date(year, date.today().month, 5), "paid": False, "variable": False},
        {"name": "Water & Electricity", "amount": 180.0, "due": date(year, date.today().month, 10), "paid": False, "variable": True},
        {"name": "Groceries", "amount": 600.0, "due": date(year, date.today().month, 28), "paid": False, "variable": True},
    ]

updated_bills = []
for idx, bill in enumerate(month_data["bills"]):
    cols = st.columns([3, 2, 2, 1, 1])
    with cols[0]:
        name = st.text_input("Name", value=bill["name"], key=f"bill_name_{profile}_{month_key}_{idx}")
    with cols[1]:
        amount = st.number_input(
            "Amount",
            min_value=0.0,
            step=10.0,
            value=bill["amount"],
            key=f"bill_amt_{profile}_{month_key}_{idx}",
        )
    with cols[2]:
        due = st.date_input("Due", value=bill["due"], key=f"bill_due_{profile}_{month_key}_{idx}")
    with cols[3]:
        paid = st.checkbox("Paid", value=bill["paid"], key=f"bill_paid_{profile}_{month_key}_{idx}")
    with cols[4]:
        variable = st.checkbox("Variable", value=bill.get("variable", False), key=f"bill_var_{profile}_{month_key}_{idx}")
    updated_bills.append({"name": name, "amount": amount, "due": due, "paid": paid, "variable": variable})

month_data["bills"] = updated_bills

total_bills = sum(b["amount"] for b in month_data["bills"])
total_paid = sum(b["amount"] for b in month_data["bills"] if b["paid"])
savings_total_monthly = sum(v["monthly"] for v in month_data["savings"].values())

budget_assigned = total_bills + savings_total_monthly
budget_left = monthly_income - budget_assigned
cash_flow = monthly_income - total_bills

col_dash = st.columns(4)
col_dash[0].metric("Monthly income", f"${monthly_income:,.2f}")
col_dash[1].metric("Budget left to assign", f"${budget_left:,.2f}")
col_dash[2].metric("Total bills", f"${total_bills:,.2f}")
col_dash[3].metric("Monthly savings", f"${savings_total_monthly:,.2f}")

st.markdown(
    f"<span class='pill pill-strong'>Monthly cash flow: ${cash_flow:,.2f}</span> "
    f"<span class='pill'>Paid bills: ${total_paid:,.2f}</span>",
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)

# ---------- SAVINGS GOALS ----------
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.markdown("### 💰 Savings Goals")

for name, info in month_data["savings"].items():
    cols = st.columns([2, 2, 2, 2])
    with cols[0]:
        goal = st.number_input(
            f"{name} goal",
            min_value=0.0,
            step=500.0,
            value=info["goal"],
            key=f"{name}_goal_{profile}_{month_key}",
        )
    with cols[1]:
        balance = st.number_input(
            f"{name} current balance",
            min_value=0.0,
            step=100.0,
            value=info["balance"],
            key=f"{name}_bal_{profile}_{month_key}",
        )
    with cols[2]:
        monthly_contrib = st.number_input(
            f"{name} monthly contrib",
            min_value=0.0,
            step=50.0,
            value=info["monthly"],
            key=f"{name}_monthly_{profile}_{month_key}",
        )
    with cols[3]:
        progress = min(balance / goal, 1.0) if goal > 0 else 0.0
        st.progress(progress)
        if goal > 0 and monthly_contrib > 0:
            remaining = max(goal - balance, 0.0)
            months_to_goal = int(remaining / monthly_contrib)
            est_date = date.today() + timedelta(days=30 * months_to_goal)
            st.caption(f"Est. completion: {est_date.strftime('%b %Y')}")
        else:
            st.caption("Set a goal and monthly contribution to see timeline.")
    info["goal"], info["balance"], info["monthly"] = goal, balance, monthly_contrib

st.markdown("</div>", unsafe_allow_html=True)

# ---------- SINKING FUNDS ----------
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.markdown("### 💳 Sinking Funds")

for fund_name, monthly_amount in month_data["sinking_funds"].items():
    cols = st.columns([3, 2])
    with cols[0]:
        st.markdown(f"**{fund_name}**")
    with cols[1]:
        new_amount = st.number_input(
            f"{fund_name} monthly",
            min_value=0.0,
            step=25.0,
            value=monthly_amount,
            key=f"sinking_{fund_name}_{profile}_{month_key}",
        )
        month_data["sinking_funds"][fund_name] = new_amount

st.markdown("</div>", unsafe_allow_html=True)

# ---------- SPENDING INSIGHTS ----------
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.markdown("### 📊 Spending Insights")

pie_labels = []
pie_values = []

pie_labels.append("Bills")
pie_values.append(total_bills)

for name, info in month_data["savings"].items():
    pie_labels.append(name + " savings")
    pie_values.append(info["monthly"])

fig_pie = px.pie(
    names=pie_labels,
    values=pie_values,
    title=f"Where money goes — {profile} — {current_month}",
    hole=0.3,
    color_discrete_sequence=[accent_color] + ["#64748B", "#94A3B8", "#0EA5E9"],
)
st.plotly_chart(fig_pie, use_container_width=True)

housing = next((b["amount"] for b in month_data["bills"] if b["name"].lower() == "rent"), 0.0)
savings_rate = (savings_total_monthly / monthly_income) if monthly_income > 0 else 0.0
housing_pct = (housing / monthly_income) if monthly_income > 0 else 0.0

col_ins = st.columns(3)
col_ins[0].metric("Savings rate", f"{savings_rate*100:.1f}%")
col_ins[1].metric("Housing %", f"{housing_pct*100:.1f}%")
col_ins[2].metric("Recommended savings", "20%+ suggested", help="Aim for ~20%+ savings rate when possible.")

st.markdown("</div>", unsafe_allow_html=True)

# ---------- MONTH-TO-MONTH / YTD ----------
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.markdown("### 📆 Month-to-month / YTD")

history_months = []
history_income = []
history_bills = []
history_savings_monthly = []

for mk, data in profile_store.items():
    if mk.startswith(str(year)):
        history_months.append(mk.split("-")[1])
        history_income.append(data["income"])
        b_total = sum(b["amount"] for b in data["bills"])
        s_total = sum(v["monthly"] for v in data["savings"].values())
        history_bills.append(b_total)
        history_savings_monthly.append(s_total)

if history_months:
    fig_bar = go.Figure()
    fig_bar.add_bar(name="Bills", x=history_months, y=history_bills, marker_color="#64748B")
    fig_bar.add_bar(name="Savings", x=history_months, y=history_savings_monthly, marker_color=accent_color)
    fig_bar.update_layout(
        barmode="group",
        title=f"{profile} — Bills vs Savings by month ({year})",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=40, b=0, l=0, r=0),
    )
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.caption("Once you set up more months for this profile, trends will show here.")

st.markdown("</div>", unsafe_allow_html=True)

# ---------- NET WORTH ----------
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.markdown("### 📈 Net Worth")

nw = month_data["net_worth"]
cols_nw = st.columns(4)
cash_val = cols_nw[0].number_input("Cash", min_value=0.0, step=100.0, value=nw["Cash"], key=f"nw_cash_{profile}_{month_key}")
sav_val = cols_nw[1].number_input("Savings", min_value=0.0, step=100.0, value=nw["Savings"], key=f"nw_sav_{profile}_{month_key}")
veh_val = cols_nw[2].number_input("Vehicle value", min_value=0.0, step=500.0, value=nw["Vehicle"], key=f"nw_vehicle_{profile}_{month_key}")
debt_val = cols_nw[3].number_input("Debt", min_value=0.0, step=100.0, value=nw["Debt"], key=f"nw_debt_{profile}_{month_key}")

nw["Cash"], nw["Savings"], nw["Vehicle"], nw["Debt"] = cash_val, sav_val, veh_val, debt_val
net_worth_total = nw["Cash"] + nw["Savings"] + nw["Vehicle"] - nw["Debt"]
st.metric("Net worth", f"${net_worth_total:,.2f}")

st.markdown("</div>", unsafe_allow_html=True)

# ---------- ZERO-BASED CHECK ----------
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.markdown("### ✅ Zero-Based Budget Check")

assigned_total = total_bills + savings_total_monthly
remaining = monthly_income - assigned_total

col_zb = st.columns(3)
col_zb[0].metric("Income", f"${monthly_income:,.2f}")
col_zb[1].metric("Assigned", f"${assigned_total:,.2f}")
col_zb[2].metric("Remaining", f"${remaining:,.2f}")

if abs(remaining) < 0.01:
    st.success("This month is a true zero-based budget — every dollar has a job.")
elif remaining > 0:
    st.info("You still have unassigned money. Add to savings, sinking funds, or other goals.")
else:
    st.error("Your plan spends more than the income. Reduce bills or savings until remaining is $0.")

st.markdown("</div>", unsafe_allow_html=True)

# ---------- SAVE PROFILES (HOOK) ----------
# For now this does nothing persistent, but you can later wire it to local storage.
save_profiles()
