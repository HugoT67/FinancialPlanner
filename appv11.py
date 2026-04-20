import random
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

#####Overview
#Browser page config
#CSS

#Session states
#Sidebar
#Simulation logic

#Main Page
#Metric cards
#Chart
#Controls
#Dataframe and export



###Page configurations
#Name on browser tab
st.set_page_config(
    page_title="Financial Planner",
    page_icon=None,
    layout="wide",
)

###CSS
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&family=DM+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;600;700&family=Cormorant+Garamond:wght@600;700&display=swap');

  html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: #0d0f14;
    color: #e8e8e0;
  }

  .main { background-color: #0d0f14; }
  section[data-testid="stSidebar"] {
    background-color: #13151c;
    border-right: 1px solid #1f2230;
  }
  section[data-testid="stSidebar"] > div:first-child {
    padding-top: 0rem !important;
  }
  section[data-testid="stSidebar"] .stSidebarContent,
  section[data-testid="stSidebar"] [data-testid="stSidebarContent"],
  section[data-testid="stSidebar"] .css-1d391kg,
  section[data-testid="stSidebar"] .css-hxt7ib {
    padding-top: 0 !important;
    margin-top: 0 !important;
  }

  h1, h2, h3 { font-family: 'Syne', sans-serif; font-weight: 800; }

  .metric-card {
    background: #13151c;
    border: 1px solid #1f2230;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
  }
  .metric-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #6b7280;
    margin-bottom: 8px;
  }
  .metric-value {
    font-family: 'DM Mono', monospace;
    font-size: 28px;
    font-weight: 500;
    color: #e8e8e0;
  }
  .metric-value.positive { color: #4ade80; }
  .metric-value.negative { color: #f87171; }
  .metric-value.neutral  { color: #60a5fa; }

  .vol-btn-row { display: flex; gap: 10px; margin-top: 4px; }

  div[data-testid="stButton"] button {
    background: #1f2230;
    color: #9ca3af;
    border: 1px solid #2d3147;
    border-radius: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.5px;
    width: 100%;
    padding: 8px 0;
    transition: all 0.2s;
  }
  div[data-testid="stButton"] button:hover {
    background: #2d3147;
    color: #e8e8e0;
    border-color: #c9922a;
  }

  .sidebar-section {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #c9922a;
    margin: 0px 0 8px 0;
  }

  .app-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 42px;
    font-weight: 700;
    letter-spacing: 0px;
    margin-bottom: 4px;
    margin-top: 0;
  }

  .block-container {
    padding-top: 1.5rem !important;
  }
  .app-subtitle {
    font-family: 'Cormorant Garamond', serif;
    font-size: 12px;
    color: #FFFFFF;
    letter-spacing: 2px;
    margin-bottom: 32px;
  }
</style>
""", unsafe_allow_html=True)



###Session states
#starting session states. When you change something in streamlit it reruns the script

#Volatility state
if "volatility" not in st.session_state:
    st.session_state.volatility = "Normal"

#Hiring state
if "hires" not in st.session_state:
    st.session_state.hires = [{"month": 7, "cost": 30_000}]

#Shock state
if "shocks" not in st.session_state:
    st.session_state.shocks = [{"start": 20, "severity": 35, "duration": 6}]

#Unexpected costs state
if "unexpected_costs" not in st.session_state:
    st.session_state.unexpected_costs = [{"name": "New equipment", "month": 32, "amount": 50_000}]


###Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-section">Cost Structure</div>', unsafe_allow_html=True)
    fixed_costs = st.number_input("Fixed Costs (DKK/month)", min_value=0, value=80_000, step=5_000)
    variable_cost = st.number_input("Variable Cost per Unit (DKK)", min_value=0, value=50, step=5)

    st.markdown('<div class="sidebar-section">Revenue</div>', unsafe_allow_html=True)
    price = st.number_input("Selling Price per Unit (DKK)", min_value=0, value=125, step=5)
    start_volume = st.number_input("Starting Monthly Volume (units)", min_value=1, value=750, step=50)

    st.markdown('<div class="sidebar-section">Growth</div>', unsafe_allow_html=True)
    growth_rate = st.slider("Monthly Volume Growth (%)", min_value=-5.0, max_value=20.0, value=5.0, step=0.5)

    st.markdown('<div class="sidebar-section">Time Horizon</div>', unsafe_allow_html=True)
    time_horizon = st.slider("Months to simulate", min_value=1, max_value=60, value=36, step=1)


###Simulation
volatility_ranges = {
    "Low":    0.02,
    "Normal": 0.06,
    "High":   0.15,
}
magnitude = volatility_ranges[st.session_state.volatility]

random.seed(42)
months, revenues, total_costs, profits, volumes = [], [], [], [], []
vol = start_volume

for i in range(time_horizon):
    if i > 0:
        vol = vol * (1 + growth_rate / 100)
    noise = random.uniform(-magnitude, +magnitude)#volatility is drawn from an uniform distribution within volatility ranges
    vol_adj = vol * (1 + noise)

    #Apply any active shocks 
    active_severity = sum(
        shock["severity"]
        for shock in st.session_state.shocks
        if shock["start"] <= i + 1 <= shock["start"] + shock["duration"] - 1#shock counts the start month as a month
    )
    if active_severity:
        vol_adj = vol_adj * (1 - min(active_severity, 100) / 100)#note shock is additive and not multiplicative

    rev  = vol_adj * price
    
    #Add any hire costs this month and forward
    extra_fixed = sum(h["cost"] for h in st.session_state.hires if h["month"] <= i + 1)
    
    #Add any unexpected one time costs hitting this month
    unexpected = sum(u["amount"] for u in st.session_state.unexpected_costs if u["month"] == i + 1)
    cost = fixed_costs + extra_fixed + unexpected + vol_adj * variable_cost
    pnl  = rev - cost

    #append values from simulation
    months.append(i + 1)
    volumes.append(round(vol_adj))
    revenues.append(rev)
    total_costs.append(cost)
    profits.append(pnl)

#values goes into dataframe
df = pd.DataFrame({
    "Month": months,
    "Revenue": revenues,
    "Total Costs": total_costs,
    "Profit": profits,
    "Cumulative Profit": pd.Series(profits).cumsum().tolist(),
    "Volume": volumes,
})


#Metrics
final_profit      = profits[-1]
cumulative_profit = sum(profits)
worst_profit      = min(profits)

total_hire_costs = sum(
    h["cost"] * (time_horizon - h["month"] + 1)
    for h in st.session_state.hires
    if h["month"] <= time_horizon
)



###Main Page
st.markdown('<div class="app-title">Financial Planner</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">By Hugo Tam</div>', unsafe_allow_html=True)

#Metrics cards
c1, c2, c3, c4 = st.columns(4)

def metric_card(label, value, cls="neutral"):
    return f"""
    <div class="metric-card">
      <div class="metric-label">{label}</div>
      <div class="metric-value {cls}">{value}</div>
    </div>"""

with c1:
    fp_cls = "positive" if final_profit >= 0 else "negative"
    st.markdown(metric_card("Final Month Profit", f"{final_profit:,.0f} DKK", fp_cls), unsafe_allow_html=True)

with c2:
    cp_cls = "positive" if cumulative_profit >= 0 else "negative"
    st.markdown(metric_card("Cumulative Profit", f"{cumulative_profit:,.0f} DKK", cp_cls), unsafe_allow_html=True)

with c3:
    st.markdown(metric_card("Total Hire Costs", f"{total_hire_costs:,.0f} DKK", "neutral"), unsafe_allow_html=True)

with c4:
    wp_cls = "positive" if worst_profit >= 0 else "negative"
    st.markdown(metric_card("Worst Month Profit", f"{worst_profit:,.0f} DKK", wp_cls), unsafe_allow_html=True)

st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

###Chart###long section
#first you have the figure
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df["Month"], y=df["Revenue"],
    name="Revenue", mode="lines",
    line=dict(color="#60a5fa", width=1.5),
    fill="none",
))

fig.add_trace(go.Scatter(
    x=df["Month"], y=df["Total Costs"],
    name="Total Costs", mode="lines",
    line=dict(color="#f87171", width=1.5),
))

#This collects all events since if they stack, you can not see 
#the previous ones when annotated. So we collect them and make them
#float on top of each other
all_events = []

for shock in st.session_state.shocks:
    if shock["start"] <= time_horizon:
        all_events.append((
            shock["start"],
            f"Shock -{shock['severity']}%",
            "#f87171",
            "#f87171",
            "shock",
            shock,
        ))

for uc in st.session_state.unexpected_costs:
    if uc["month"] <= time_horizon:
        all_events.append((
            uc["month"],
            f"{uc['name']} -{uc['amount']:,}",
            "#fb923c",
            "#fb923c",
            "cost",
            uc,
        ))

for hire in st.session_state.hires:
    if hire["month"] <= time_horizon:
        all_events.append((
            hire["month"],
            f"Hire -{hire['cost']:,}",
            "#c084fc",
            "#c084fc",
            "hire",
            hire,
        ))

#Count how many events have already been placed at each month
month_counter = {}
for event in all_events:
    m = event[0]
    month_counter[m] = month_counter.get(m, 0) + 1
###maybe fragile logic with index
month_index = {}###be careful if adding features using index and not unique id might cause problems. currently no problems

LABEL_STEP_PX = 22  #vertical pixel gap between stacked labels

for month, label, line_color, ann_color, kind, data in all_events:
    idx = month_index.get(month, 0)
    month_index[month] = idx + 1

    yshift = idx * LABEL_STEP_PX  

    #Draw shock shaded region separately 
    if kind == "shock":
        s_end = min(data["start"] + data["duration"] - 1, time_horizon)#note we are treating months as indexes so no time inbetween months
        fig.add_vrect(
            x0=data["start"], x1=s_end,
            fillcolor="rgba(248, 113, 113, 0.12)",
            layer="below", line_width=0,
        )

    fig.add_vline(
        x=month,
        line_width=1.5,
        line_dash="dot",
        line_color=line_color,
        annotation_text=label,
        annotation_position="top",
        annotation_yshift=yshift,
        annotation_font_color=ann_color,
        annotation_font_size=11,
    )#vertical annotation lines

# Zero line
fig.add_hline(y=0, line_width=1, line_color="#3d4460")

#Figure
fig.update_layout(
    paper_bgcolor="#0d0f14",
    plot_bgcolor="#0d0f14",
    font=dict(family="JetBrains Mono, monospace", color="#9ca3af", size=11),
    legend=dict(
        orientation="h",
        yanchor="top", y=-0.18,
        xanchor="left", x=0,
        font=dict(size=12, color="#e8e8e0"),
        bgcolor="rgba(0,0,0,0)",
    ),
    xaxis=dict(
        title="Month",
        gridcolor="#2d3147",
        showline=False,
        zeroline=False,
    ),
    yaxis=dict(
        title="DKK",
        gridcolor="#2d3147",
        showline=False,
        zeroline=False,
        tickformat=",.0f",
    ),
    margin=dict(l=10, r=10, t=60, b=50),
    height=420,
    hovermode="x unified",
)

st.plotly_chart(fig, use_container_width=True)
#End of chart section

###Controls below chart
#Controls for Volatility and Hiring
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
ctrl_col1, ctrl_col2 = st.columns(2)

with ctrl_col1:
    st.markdown('<div class="sidebar-section">Volatility</div>', unsafe_allow_html=True)
    st.markdown("<div style='font-size:14px; color:#e8e8e0; margin-bottom:8px;'>Choose volatility level</div>", unsafe_allow_html=True)
    st.selectbox(
        "Volatility Level",
        options=["Low", "Normal", "High"],
        key="volatility",
        label_visibility="collapsed",
    )
    st.markdown(
        f"<div style='font-family:JetBrains Mono,monospace; font-size:11px; "
        f"color:#c9922a; margin-top:4px;'>● {st.session_state.volatility} volatility active</div>",
        unsafe_allow_html=True
    )

with ctrl_col2:
    st.markdown('<div class="sidebar-section">Hiring</div>', unsafe_allow_html=True)
    h_col1, h_col2, h_col3 = st.columns([2, 3, 2])
    with h_col1:
        hire_month = st.number_input("Month", min_value=1, max_value=60, value=7, step=1)
    with h_col2:
        hire_cost = st.number_input("Monthly Cost (DKK)", min_value=0, value=30_000, step=1_000)
    with h_col3:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("ADD HIRE"):
            st.session_state.hires.append({"month": hire_month, "cost": hire_cost})
            st.rerun()

    if st.session_state.hires:
        for idx, hire in enumerate(st.session_state.hires):
            h_a, h_b = st.columns([4, 1])
            with h_a:
                st.markdown(
                    f"<div style='font-family:JetBrains Mono,monospace; font-size:11px; color:#9ca3af; padding:4px 0;'>"
                    f"Month {hire['month']} — {hire['cost']:,} DKK/mo</div>",
                    unsafe_allow_html=True
                )
            with h_b:
                if st.button("✕", key=f"remove_hire_{idx}"):
                    st.session_state.hires.pop(idx)
                    st.rerun()

st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True)

#Economic shock on its own row
shock_col, _ = st.columns([2, 1])
with shock_col:
    st.markdown('<div class="sidebar-section">Economic Shock</div>', unsafe_allow_html=True)
    s_col1, s_col2, s_col3, s_col4 = st.columns([2, 2, 2, 2])
    with s_col1:
        shock_start = st.number_input("Start Month", min_value=1, max_value=60, value=20, step=1)
    with s_col2:
        shock_severity = st.number_input("Volume Drop (%)", min_value=1, max_value=100, value=35, step=5)
    with s_col3:
        shock_duration = st.number_input("Duration (mo)", min_value=1, max_value=60, value=6, step=1)
    with s_col4:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("ADD SHOCK"):
            st.session_state.shocks.append({
                "start": shock_start,
                "severity": shock_severity,
                "duration": shock_duration,
            })
            st.rerun()

    if st.session_state.shocks:
        for idx, shock in enumerate(st.session_state.shocks):
            s_a, s_b = st.columns([4, 1])
            with s_a:
                st.markdown(
                    f"<div style='font-family:JetBrains Mono,monospace; font-size:11px; color:#9ca3af; padding:4px 0;'>"
                    f"Month {shock['start']} — -{shock['severity']}% for {shock['duration']} mo</div>",
                    unsafe_allow_html=True
                )
            with s_b:
                if st.button("✕", key=f"remove_shock_{idx}"):
                    st.session_state.shocks.pop(idx)
                    st.rerun()

st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True)

#Unexpected costs on its own row
uc_col, _ = st.columns([2, 1])
with uc_col:
    st.markdown('<div class="sidebar-section">Unexpected Costs</div>', unsafe_allow_html=True)
    u_col1, u_col2, u_col3, u_col4 = st.columns([3, 2, 2, 2])
    with u_col1:
        uc_name = st.text_input("Name", value="New equipment", label_visibility="visible")
    with u_col2:
        uc_month = st.number_input("Month ", min_value=1, max_value=60, value=32, step=1)
    with u_col3:
        uc_amount = st.number_input("Amount (DKK)", min_value=0, value=50_000, step=5_000)
    with u_col4:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("ADD COST"):
            st.session_state.unexpected_costs.append({
                "name": uc_name,
                "month": uc_month,
                "amount": uc_amount,
            })
            st.rerun()

    if st.session_state.unexpected_costs:
        for idx, uc in enumerate(st.session_state.unexpected_costs):
            u_a, u_b = st.columns([4, 1])
            with u_a:
                st.markdown(
                    f"<div style='font-family:JetBrains Mono,monospace; font-size:11px; color:#9ca3af; padding:4px 0;'>"
                    f"Month {uc['month']} — {uc['name']} — {uc['amount']:,} DKK</div>",
                    unsafe_allow_html=True
                )
            with u_b:
                if st.button("✕", key=f"remove_uc_{idx}"):
                    st.session_state.unexpected_costs.pop(idx)
                    st.rerun()

###Dataframe below the controls
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Revenue":     st.column_config.NumberColumn("Revenue", format="%d DKK"),
        "Total Costs": st.column_config.NumberColumn("Total Costs", format="%d DKK"),
        "Profit":            st.column_config.NumberColumn("Profit", format="%d DKK"),
        "Cumulative Profit": st.column_config.NumberColumn("Cumulative Profit", format="%d DKK"),
        "Volume":            st.column_config.NumberColumn("Volume", format="%d units"),
    }
)#for streamlit sorting function you need numbers. they are numbers then added dkk after

###export option
csv = df.to_csv(index=False)
st.download_button("Export CSV", csv, "Financial_plan.csv", "text/csv")