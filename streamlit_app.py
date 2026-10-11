"""Consumer Complaints dashboard (Streamlit). Run: streamlit run streamlit_app.py
Set COMPLAINTS_CSV to the real CFPB file; defaults to data/complaints.csv (demo)."""
import os
import pandas as pd
import plotly.express as px
import streamlit as st
from pipeline import load_clean

st.set_page_config(page_title="Consumer Complaints EDA", page_icon="📊", layout="wide")
CSV = os.environ.get("COMPLAINTS_CSV", os.path.join(os.path.dirname(__file__), "data", "complaints.csv"))
GOLD, TEAL, BLUE, ROSE, SAGE, VIOLET = "#d4af6a", "#3fb6a8", "#7b9ad6", "#d1707c", "#a3b36b", "#a98bd9"
COLORWAY = [GOLD, TEAL, BLUE, ROSE, VIOLET, SAGE]
TIMELY = {"Yes": TEAL, "No": ROSE}
GOLD_SCALE = [[0, "#14110b"], [.5, "#8a6d33"], [1, "#f1d9a0"]]
DIV_SCALE = [[0, ROSE], [.5, "#2a2f3a"], [1, TEAL]]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap');
html, body, [class*="css"], .stApp {font-family:'Inter',sans-serif;}
.stApp {background:radial-gradient(1200px 600px at 85% -10%, rgba(212,175,106,.10), transparent 60%), #0a0c11;}
h1, h2, h3, h4 {font-family:'Fraunces',Georgia,serif !important; letter-spacing:-.01em; font-weight:600 !important;}
h1 {font-size:2.5rem !important; background:linear-gradient(90deg,#f1d9a0,#d4af6a 60%,#b98f45); -webkit-background-clip:text; -webkit-text-fill-color:transparent;}
h1 + div {margin-top:-.4rem}
h4 {color:#e9d3a1 !important}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#10131a,#0b0d12); border-right:1px solid rgba(212,175,106,.18);}
[data-testid="stSidebar"] h2 {background:linear-gradient(90deg,#f1d9a0,#d4af6a); -webkit-background-clip:text; -webkit-text-fill-color:transparent;}
[data-testid="stSidebar"] h3 {font-size:.8rem !important; text-transform:uppercase; letter-spacing:.16em; color:#9a8556 !important; font-family:'Inter',sans-serif !important;}
[data-testid="stMetric"] {background:linear-gradient(145deg,#161a23,#10131a); border:1px solid rgba(212,175,106,.20); border-radius:14px; padding:16px 18px; box-shadow:0 6px 24px rgba(0,0,0,.35);}
[data-testid="stMetricLabel"] p {color:#9a9aa5; font-size:.78rem; text-transform:uppercase; letter-spacing:.12em;}
[data-testid="stMetricValue"] {font-family:'Fraunces',serif; color:#f1d9a0;}
[data-testid="stPlotlyChart"], [data-testid="stDataFrame"] {background:#11141b; border:1px solid rgba(255,255,255,.06); border-radius:14px; padding:6px; box-shadow:0 6px 24px rgba(0,0,0,.30);}
.stTabs [data-baseweb="tab-list"] {gap:6px; border-bottom:1px solid rgba(212,175,106,.18);}
.stTabs [data-baseweb="tab"] {color:#8b8f9a; padding:8px 16px;}
.stTabs [aria-selected="true"] {color:#f1d9a0 !important;}
.stTabs [data-baseweb="tab-highlight"] {background:#d4af6a;}
span[data-baseweb="tag"] {background:linear-gradient(135deg,#d4af6a,#a8823f) !important; color:#14110b !important; border-radius:8px;}
span[data-baseweb="tag"] span {color:#14110b !important;}
[data-baseweb="select"] > div {background:#161a23 !important; border:1px solid rgba(255,255,255,.08) !important; border-radius:10px;}
code {color:#d4af6a !important; background:rgba(212,175,106,.10) !important;}
hr {border-color:rgba(212,175,106,.18) !important;}
#MainMenu, footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner="Loading and cleaning data…")
def get_data():
    d = load_clean(CSV)
    d["Year"] = d["Date received"].dt.year
    return d


def style(fig, h=380):
    fig.update_layout(height=h, margin=dict(l=10, r=10, t=50, b=10), legend_title_text="", colorway=COLORWAY,
                      font=dict(family="Inter, sans-serif", color="#cfc9bb"),
                      title_font=dict(family="Fraunces, Georgia, serif", size=17, color="#ece7dc"),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      hoverlabel=dict(bgcolor="#161a23", bordercolor=GOLD, font_color="#ece7dc"))
    fig.update_xaxes(gridcolor="rgba(255,255,255,.06)", zerolinecolor="rgba(255,255,255,.10)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,.06)", zerolinecolor="rgba(255,255,255,.10)")
    return fig


def top_bar(s, title, n=10, color=GOLD):
    vc = s.value_counts().head(n).iloc[::-1]
    fig = px.bar(x=vc.values, y=vc.index, orientation="h", title=title, labels={"x": "Complaints", "y": ""})
    fig.update_traces(marker_color=color)
    return style(fig)


def monthly(d, col="Date received"):
    return d.set_index(col).resample("ME").size().rename("Complaints").reset_index()


df = get_data()

# ---------------- Sidebar ----------------
st.sidebar.markdown("## Consumer Complaints")
page = st.sidebar.radio("Navigate", ["🏠 Home", "📈 Univariate", "🔗 Bivariate", "🧩 Multivariate"])
st.sidebar.divider()
st.sidebar.markdown("### Filters")
years = sorted(df["Year"].unique())
sel_years = st.sidebar.multiselect("Year", years, default=years)
sel_prod = st.sidebar.multiselect("Product", df["Product"].value_counts().index.tolist(), placeholder="All products")
sel_state = st.sidebar.multiselect("State", sorted(df["State"].unique()), placeholder="All states")
sel_chan = st.sidebar.multiselect("Submitted via", df["Submitted via"].value_counts().index.tolist(), placeholder="All channels")
sel_timely = st.sidebar.radio("Timely response?", ["All", "Yes", "No"], horizontal=True)

d = df[df["Year"].isin(sel_years)]
if sel_prod:
    d = d[d["Product"].isin(sel_prod)]
if sel_state:
    d = d[d["State"].isin(sel_state)]
if sel_chan:
    d = d[d["Submitted via"].isin(sel_chan)]
if sel_timely != "All":
    d = d[d["Timely response?"] == sel_timely]
st.sidebar.caption(f"**{len(d):,}** of {len(df):,} complaints selected")

# ---------------- Home ----------------
if page.endswith("Home"):
    st.title("Consumer Complaint Database — EDA Dashboard")
    st.caption("Interactive version of Final_Consumer_Complaints_EDA.ipynb · Source: CFPB Consumer Complaint Database")
    left, right = st.columns([3, 2], gap="large")
    with left:
        st.markdown("#### 🎯 Key questions")
        st.markdown("""
- How has complaint volume moved over time, and which **products** and **companies** drive it?
- Do **channels** or **states** change how likely a complaint is answered on time?
- Is routing delay (`days_to_send`) what separates **timely** from **late** responses?
- How are complaints **resolved**, and does that differ by product or state?""")
    with right:
        st.markdown("#### Dataset snapshot")
        snap = pd.DataFrame({"Item": ["Rows (after cleaning)", "Columns used", "Years covered", "Products", "Companies", "States",
                                      "Target-like fields", "Source file"],
                             "Value": [f"{len(df):,}", "13 (+ derived)", f"{years[0]}–{years[-1]}", df["Product"].nunique(),
                                       df["Company"].nunique(), df["State"].nunique(),
                                       "Timely response?, Company response to consumer", os.path.basename(CSV)]})
        st.dataframe(snap, hide_index=True, use_container_width=True)
    k = st.columns(5)
    k[0].metric("Complaints", f"{len(d):,}")
    k[1].metric("Timely response", f"{d['timely_flag'].mean()*100:.2f}%" if len(d) else "–")
    k[2].metric("Avg days to send", f"{d['days_to_send'].mean():.2f}" if len(d) else "–")
    k[3].metric("With narrative", f"{(d['Consumer complaint narrative']!='Not Provided').mean()*100:.1f}%" if len(d) else "–")
    k[4].metric("Monetary relief", f"{(d['Company response to consumer']=='Closed with monetary relief').mean()*100:.2f}%" if len(d) else "–")

    st.markdown("#### 📋 Column Information")
    cols = pd.DataFrame([
        ("Date received", "Date", "Date the CFPB received the complaint"),
        ("Product / Sub-product", "Categorical", "Financial product the complaint is about"),
        ("Issue / Sub-issue", "Categorical", "Specific problem the consumer reported"),
        ("Company", "Categorical", "Company the complaint is against"),
        ("State", "Categorical", "US state of the consumer"),
        ("Submitted via", "Categorical", "Web, Referral, Phone, Postal mail, Email or Fax"),
        ("Date sent to company", "Date", "Date the complaint was routed to the company"),
        ("Company response to consumer", "Target (multi-class)", "How the company closed the complaint"),
        ("Timely response?", "Target (Yes/No)", "Whether the company responded on time"),
        ("Complaint ID", "Identifier", "Unique id — not analysed numerically"),
        ("Consumer complaint narrative", "Text", "Optional free text; 'Not Provided' when missing"),
        ("days_to_send", "Numeric (derived)", "Days between received and sent-to-company, outliers capped"),
    ], columns=["Column", "Type", "Description"])
    st.dataframe(cols, hide_index=True, use_container_width=True, height=300)

    a, b = st.columns(2, gap="large")
    with a:
        st.markdown("#### 🧹 Data Preparation")
        st.markdown("""
- Random sample of **120,000** rows from the raw file (seed 42), 13 columns kept
- Missing narrative / sub-product / sub-issue filled with *Not Provided* / *Not Specified*
- Rows missing a core field dropped; duplicate rows and Complaint IDs removed
- `days_to_send` derived and outliers capped (IQR rule, 1st/99th percentile fallback when IQR = 0)""")
    with b:
        st.markdown("#### 🧭 How to Use This Dashboard")
        st.markdown("""
- **Univariate** — distribution of every individual variable
- **Bivariate** — pairs of variables, including timeliness and routing delay
- **Multivariate** — heatmaps, three-way views and pivot tables
- Use the **sidebar filters**; every page and chart updates instantly""")
    st.stop()

if d.empty:
    st.warning("No complaints match the current filters.")
    st.stop()

top5p = d["Product"].value_counts().head(5).index
top5s = d["State"].value_counts().head(5).index

# ---------------- Univariate ----------------
if page.endswith("Univariate"):
    st.title("Univariate Analysis")
    t1, t2, t3 = st.tabs(["Time", "Categories", "Outcomes & text"])
    with t1:
        c1, c2 = st.columns(2)
        c1.plotly_chart(style(px.line(monthly(d), x="Date received", y="Complaints", title="Complaints received (monthly)")), use_container_width=True)
        c2.plotly_chart(style(px.line(monthly(d, "Date sent to company"), x="Date sent to company", y="Complaints",
                                      title="Complaints sent to company (monthly)", color_discrete_sequence=[BLUE])), use_container_width=True)
    with t2:
        c1, c2 = st.columns(2)
        c1.plotly_chart(top_bar(d["Product"], "Top 10 products"), use_container_width=True)
        c2.plotly_chart(top_bar(d["Company"], "Top 10 companies", color=VIOLET), use_container_width=True)
        c1.plotly_chart(top_bar(d["Issue"], "Top 10 issues", color=BLUE), use_container_width=True)
        c2.plotly_chart(top_bar(d["State"], "Top 10 states", color=TEAL), use_container_width=True)
        c1.plotly_chart(top_bar(d["Sub-product"], "Top 10 sub-products (Not Specified = missing)", color=TEAL), use_container_width=True)
        c2.plotly_chart(top_bar(d["Sub-issue"], "Top 10 sub-issues (Not Specified = missing)", color=ROSE), use_container_width=True)
        ch = d["Submitted via"].value_counts()
        small = ch[ch / ch.sum() < .02]
        ch = ch[ch / ch.sum() >= .02]
        if small.sum():
            ch["Other"] = small.sum()
        st.plotly_chart(style(px.pie(values=ch.values, names=ch.index, hole=.45, title="Submission channel (<2% grouped as Other)")), use_container_width=True)
    with t3:
        c1, c2 = st.columns(2)
        c1.plotly_chart(top_bar(d["Company response to consumer"], "Company response", 20, SAGE), use_container_width=True)
        tc = d["Timely response?"].value_counts()
        c2.plotly_chart(style(px.bar(x=tc.index, y=tc.values, color=tc.index, color_discrete_map=TIMELY,
                                     title="Timely response (class imbalance)", labels={"x": "", "y": "Complaints"})), use_container_width=True)
        wc = d["word_count"].dropna()
        if len(wc):
            st.plotly_chart(style(px.histogram(wc, nbins=40, title="Narrative word count (narratives provided)", labels={"value": "Words"})), use_container_width=True)
        st.caption(f"Complaint IDs: {d['Complaint ID'].nunique():,} unique of {len(d):,} rows — an identifier, so no distribution to plot.")

# ---------------- Bivariate ----------------
elif page.endswith("Bivariate"):
    st.title("Bivariate Analysis")

    def pct_bar(rowcol, other, top=None, horizontal=False, title=""):
        x = d if top is None else d[d[rowcol].isin(d[rowcol].value_counts().head(top).index)]
        ct = (pd.crosstab(x[rowcol], x[other], normalize="index") * 100).reset_index().melt(rowcol, var_name=other, value_name="%")
        fig = px.bar(ct, x="%" if horizontal else rowcol, y=rowcol if horizontal else "%", color=other, title=title,
                     orientation="h" if horizontal else "v", color_discrete_map=TIMELY if other == "Timely response?" else None)
        return style(fig)

    def days_box(cat, top=5, title=""):
        x = d[d[cat].isin(d[cat].value_counts().head(top).index)]
        return style(px.box(x, x=cat, y="days_to_send", title=title))

    t1, t2, t3 = st.tabs(["Timeliness", "Days to send", "Responses & trend"])
    with t1:
        c1, c2 = st.columns(2)
        c1.plotly_chart(pct_bar("Product", "Timely response?", 5, title="Timely response by product (top 5)"), use_container_width=True)
        c2.plotly_chart(pct_bar("State", "Timely response?", 5, title="Timely response by state (top 5)"), use_container_width=True)
        c1.plotly_chart(pct_bar("Submitted via", "Timely response?", title="Timely response by channel"), use_container_width=True)
        c2.plotly_chart(pct_bar("Issue", "Timely response?", 10, True, "Timely response by issue (top 10)"), use_container_width=True)
    with t2:
        c1, c2 = st.columns(2)
        c1.plotly_chart(days_box("Product", title="Days to send by product (top 5)"), use_container_width=True)
        c2.plotly_chart(days_box("State", title="Days to send by state (top 5)"), use_container_width=True)
        c1.plotly_chart(days_box("Submitted via", 6, "Days to send by channel"), use_container_width=True)
        c2.plotly_chart(days_box("Company response to consumer", 8, "Days to send by company response"), use_container_width=True)
    with t3:
        st.plotly_chart(pct_bar("Product", "Company response to consumer", 5, title="Company response by product (top 5)"), use_container_width=True)
        st.plotly_chart(style(px.line(monthly(d), x="Date received", y="Complaints", title="Complaint volume over time")), use_container_width=True)

# ---------------- Multivariate ----------------
else:
    st.title("Multivariate Analysis")
    t1, t2, t3 = st.tabs(["Heatmaps", "Over time", "Pivot tables"])
    with t1:
        c1, c2 = st.columns(2)
        m = d[d["Product"].isin(top5p) & d["State"].isin(top5s)]
        c1.plotly_chart(style(px.imshow(pd.crosstab(m["Product"], m["State"]), text_auto=True, color_continuous_scale=GOLD_SCALE,
                                        title="Product × State (counts)", aspect="auto")), use_container_width=True)
        s5 = d[d["State"].isin(top5s)]
        c2.plotly_chart(style(px.imshow(pd.crosstab(s5["State"], s5["Company response to consumer"]), text_auto=True,
                                        color_continuous_scale=GOLD_SCALE, title="State × Company response (counts)", aspect="auto")), use_container_width=True)
        p5 = d[d["Product"].isin(top5p)]
        rate = pd.pivot_table(p5, index="Product", columns="Submitted via", values="timely_flag", aggfunc="mean") * 100
        c1.plotly_chart(style(px.imshow(rate.round(1), text_auto=True, color_continuous_scale=DIV_SCALE,
                                        title="% timely: Product × Channel", aspect="auto")), use_container_width=True)
        avg = p5.groupby(["Product", "Timely response?"])["days_to_send"].mean().reset_index()
        c2.plotly_chart(style(px.bar(avg, x="Product", y="days_to_send", color="Timely response?", barmode="group",
                                     color_discrete_map=TIMELY, title="Avg days to send: Product × Timely?")), use_container_width=True)
    with t2:
        top3 = d["Product"].value_counts().head(3).index
        mp = d[d["Product"].isin(top3)].groupby("Product").resample("ME", on="Date received").size().rename("Complaints").reset_index()
        st.plotly_chart(style(px.line(mp, x="Date received", y="Complaints", color="Product", title="Monthly volume, top 3 products"), 460), use_container_width=True)
    with t3:
        p1 = pd.pivot_table(d, index="Product", columns="Timely response?", values="Complaint ID", aggfunc="count", fill_value=0)
        p1["Total"] = p1.sum(axis=1)
        st.markdown("**Product × Timely response**")
        st.dataframe(p1.sort_values("Total", ascending=False), use_container_width=True)
        p2 = pd.pivot_table(d, index="State", columns="Company response to consumer", values="Complaint ID", aggfunc="count", fill_value=0)
        p2["Total"] = p2.sum(axis=1)
        st.markdown("**State × Company response (top 10)**")
        st.dataframe(p2.sort_values("Total", ascending=False).head(10), use_container_width=True)
        p3 = d.groupby("Product")["days_to_send"].agg(avg_days_to_send="mean", median_days_to_send="median", complaint_count="count")
        st.markdown("**Days to send by product**")
        st.dataframe(p3.sort_values("avg_days_to_send", ascending=False), use_container_width=True)
