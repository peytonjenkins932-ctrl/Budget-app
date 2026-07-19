import streamlit as st
import plotly.express as px

st.set_page_config(
    page_title="Zero-Based Budget",
    page_icon="💰",
    layout="centered",
)

st.title("Zero-Based Budget Planner")

# 0. Profile selector
profile = st.selectbox("Select profile", ["Julius", "Peyton"])

st.caption("Each profile can have its own income and bills, but the budgeting logic stays the same.")

# Default values per profile (you can change these)
if profile == "Julius":
    default_income = 5833.33  # 70k/year ≈ 5833.33/month
    default_rent = 1275.0
    default_phone = 200.0
    default_utilities = 180.0
    default_groceries = 600.0
    default_gas = 25.0 * 52 / 12  # weekly → monthly
else:  # Peyton
    # Put whatever makes sense for you now; these are just placeholders
    default_income = 4500.0
    default_rent = 1200.0
    default_phone = 150.0
    default_utilities = 160.0
    default_groceries = 500.0
    default_gas = 100.0

st.markdown(f"### 1. Income — {profile}")
monthly_income = st.number_input(
    "Monthly take-home income ($)",
    min_value=0.0,
    step=100.0,
    value=default_income,
)

st.markdown(f"### 2. Fixed expenses — {profile}")
col1, col2 = st.columns(2)

with col1:
    rent = st.number_input("Rent", min_value=0.0, step=50.0, value=default_rent)
    phone = st.number_input("Phone bill", min_value=0.0, step=25.0, value=default_phone)
    utilities = st.number_input("Water & electricity", min_value=0.0, step=25.0, value=default_utilities)

with col2:
    other_fixed = st.number_input("Other fixed bills", min_value=0.0, step=25.0, value=0.0)
    subscriptions = st.number_input("Subscriptions", min_value=0.0, step=10.0, value=0.0)
    debt_payments = st.number_input("Debt payments", min_value=0.0, step=25.0, value=0.0)

fixed_total = rent + phone + utilities + other_fixed + subscriptions + debt_payments

st.markdown(f"### 3. Variable expenses — {profile}")
groceries = st.number_input("Groceries", min_value=0.0, step=25.0, value=default_groceries)
gas = st.number_input("Gas / fuel", min_value=0.0, step=10.0, value=default_gas)
other_variable = st.number_input("Other variable spending", min_value=0.0, step=25.0, value=0.0)

variable_total = groceries + gas + other_variable

st.markdown("### 4. Savings goals")
st.caption("Choose how you want to split whatever is left after bills.")

col_s1, col_s2, col_s3 = st.columns(3)
with col_s1:
    rainy_pct = st.slider("Rainy day %", 0, 100, 40)
with col_s2:
    vacation_pct = st.slider("Vacation %", 0, 100, 25)
with col_s3:
    vehicle_pct = st.slider("New vehicle %", 0, 100, 35)

total_pct = rainy_pct + vacation_pct + vehicle_pct

if total_pct != 100:
    st.warning(f"Savings percentages add up to {total_pct}%. For a clean split, set them to 100% total.")
    
remaining_after_bills = monthly_income - fixed_total - variable_total
remaining_after_bills = max(remaining_after_bills, 0.0)

if total_pct > 0:
    rainy_amount = remaining_after_bills * (rainy_pct / total_pct)
    vacation_amount = remaining_after_bills * (vacation_pct / total_pct)
    vehicle_amount = remaining_after_bills * (vehicle_pct / total_pct)
else:
    rainy_amount = vacation_amount = vehicle_amount = 0.0

savings_total = rainy_amount + vacation_amount + vehicle_amount
total_assigned = fixed_total + variable_total + savings_total
difference = monthly_income - total_assigned

st.markdown("### 5. Summary")
st.write("---")

col_sum1, col_sum2 = st.columns(2)
with col_sum1:
    st.metric("Monthly income", f"${monthly_income:,.2f}")
    st.metric("Fixed expenses", f"${fixed_total:,.2f}")
    st.metric("Variable expenses", f"${variable_total:,.2f}")

with col_sum2:
    st.metric("Savings total", f"${savings_total:,.2f}")
    st.metric("Total assigned", f"${total_assigned:,.2f}")
    st.metric("Unassigned (should be $0)", f"${difference:,.2f}")

st.write("---")
st.markdown("### Savings breakdown")

col_sb1, col_sb2, col_sb3 = st.columns(3)
with col_sb1:
    st.subheader("Rainy day")
    st.write(f"${rainy_amount:,.2f} / month")
with col_sb2:
    st.subheader("Vacations")
    st.write(f"${vacation_amount:,.2f} / month")
with col_sb3:
    st.subheader("New vehicle")
    st.write(f"${vehicle_amount:,.2f} / month")

st.write("---")

if abs(difference) < 0.01:
    st.success("Nice! This is a true zero-based budget — every dollar has a job.")
elif difference > 0:
    st.info("You still have unassigned money. Increase savings, add a category, or review your estimates.")
else:
    st.error("Your plan spends more than the income. Lower some expenses or savings until the difference is $0.")

# 6. Visual chart: where the money goes
st.markdown("### 6. Where the money goes (pie chart)")

labels = [
    "Fixed expenses",
    "Variable expenses",
    "Rainy day savings",
    "Vacation savings",
    "Vehicle savings",
]
values = [
    fixed_total,
    variable_total,
    rainy_amount,
    vacation_amount,
    vehicle_amount,
]

fig = px.pie(
    names=labels,
    values=values,
    title=f"Monthly money flow — {profile}",
    hole=0.2,  # donut style for readability
)

st.plotly_chart(fig, use_container_width=True)
