import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="Valuation Screener",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Styling ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .metric-card {
        background: #1a1f2e;
        border: 1px solid #2d3748;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        margin: 0.4rem 0;
    }
    .metric-label { color: #7a8499; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; }
    .metric-value { color: #e2e8f0; font-size: 1.8rem; font-weight: 700; margin: 0.2rem 0; }
    .metric-vs    { color: #718096; font-size: 0.8rem; }
    .cheap  { color: #48bb78 !important; }
    .fair   { color: #ecc94b !important; }
    .expensive { color: #fc8181 !important; }
    .header-tag { color: #667eea; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; }
    .company-name { font-size: 2rem; font-weight: 700; color: #e2e8f0; }
    .company-sub  { font-size: 1rem; color: #718096; margin-bottom: 1.5rem; }
    div[data-testid="stMetric"] label { color: #7a8499 !important; }
</style>
""", unsafe_allow_html=True)


# ── Sector peer tickers ────────────────────────────────────────────────────
SECTOR_PEERS = {
    "Technology": ["AAPL","MSFT","GOOGL","META","NVDA","ORCL","ADBE","CRM","INTC","AMD"],
    "Financial Services": ["JPM","BAC","WFC","C","GS","MS","BLK","SCHW","AXP","USB"],
    "Healthcare": ["JNJ","UNH","PFE","ABBV","MRK","TMO","ABT","DHR","BMY","AMGN"],
    "Consumer Cyclical": ["AMZN","TSLA","HD","MCD","NKE","LOW","SBUX","TGT","TJX","BKNG"],
    "Consumer Defensive": ["WMT","PG","KO","PEP","COST","PM","MO","CL","GIS","K"],
    "Energy": ["XOM","CVX","COP","SLB","EOG","PXD","MPC","VLO","PSX","OXY"],
    "Industrials": ["HON","UPS","CAT","DE","LMT","RTX","GE","MMM","ETN","EMR"],
    "Communication Services": ["GOOGL","META","NFLX","DIS","CMCSA","T","VZ","CHTR","WBD","PARA"],
    "Real Estate": ["AMT","PLD","CCI","EQIX","PSA","O","SPG","WELL","AVB","EQR"],
    "Materials": ["LIN","APD","SHW","FCX","NEM","NUE","VMC","MLM","CF","MOS"],
    "Utilities": ["NEE","DUK","SO","D","AEP","EXC","SRE","XEL","ED","ETR"],
}


# ── Data fetching ─────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def get_ticker_data(ticker: str):
    t = yf.Ticker(ticker)
    info = t.info
    return info

def safe(d, key, default=None):
    v = d.get(key, default)
    return v if v not in (None, "N/A", "", 0) else default

def compute_multiples(info: dict) -> dict:
    pe       = safe(info, "trailingPE")
    ev_ebitda= safe(info, "enterpriseToEbitda")
    price    = safe(info, "currentPrice") or safe(info, "regularMarketPrice")
    fcf      = safe(info, "freeCashflow")
    mktcap   = safe(info, "marketCap")

    p_fcf = None
    if price and fcf and mktcap and fcf > 0:
        shares = safe(info, "sharesOutstanding")
        if shares and shares > 0:
            fcf_per_share = fcf / shares
            p_fcf = round(price / fcf_per_share, 2)

    return {
        "P/E":        round(pe, 2)       if pe        else None,
        "EV/EBITDA":  round(ev_ebitda, 2) if ev_ebitda else None,
        "P/FCF":      p_fcf,
    }

@st.cache_data(ttl=3600, show_spinner=False)
def get_sector_medians(sector: str) -> dict:
    peers = SECTOR_PEERS.get(sector, [])
    rows = []
    for p in peers:
        try:
            info = get_ticker_data(p)
            m = compute_multiples(info)
            rows.append(m)
        except Exception:
            continue
    if not rows:
        return {}
    df = pd.DataFrame(rows)
    return {col: round(df[col].median(), 2) for col in df.columns if df[col].notna().sum() > 0}

def valuation_signal(value, median):
    if value is None or median is None:
        return "n/a", "—"
    ratio = value / median
    if ratio < 0.85:
        return "cheap", "🟢 Undervalued"
    elif ratio > 1.20:
        return "expensive", "🔴 Overvalued"
    else:
        return "fair", "🟡 Fair value"


# ── UI ────────────────────────────────────────────────────────────────────
st.markdown('<p class="header-tag">📊 Equity Research Tool</p>', unsafe_allow_html=True)
st.markdown('<p class="company-name">Valuation Screener</p>', unsafe_allow_html=True)
st.markdown('<p class="company-sub">Fundamental multiples vs. sector median — powered by Yahoo Finance</p>', unsafe_allow_html=True)

col_input, col_btn = st.columns([3, 1])
with col_input:
    ticker_input = st.text_input(
        "Ticker symbol",
        value="AAPL",
        placeholder="e.g. AAPL, MSFT, ENI.MI",
        label_visibility="collapsed"
    )
with col_btn:
    run = st.button("Analyze →", use_container_width=True)

st.divider()

if run or ticker_input:
    ticker = ticker_input.strip().upper()

    with st.spinner(f"Fetching data for {ticker}…"):
        try:
            info = get_ticker_data(ticker)
        except Exception as e:
            st.error(f"Could not fetch data for **{ticker}**. Check the ticker symbol.")
            st.stop()

    name    = safe(info, "longName", ticker)
    sector  = safe(info, "sector", "Technology")
    industry= safe(info, "industry", "—")
    country = safe(info, "country", "—")
    currency= safe(info, "currency", "USD")
    price   = safe(info, "currentPrice") or safe(info, "regularMarketPrice", 0)
    mktcap  = safe(info, "marketCap", 0)
    beta    = safe(info, "beta")

    # Company header
    st.markdown(f"### {name}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sector",   sector)
    c2.metric("Industry", industry[:30] if industry else "—")
    c3.metric("Country",  country)
    c4.metric("Price",    f"{currency} {price:,.2f}" if price else "—")

    st.divider()

    # Multiples
    multiples = compute_multiples(info)

    with st.spinner("Computing sector medians…"):
        medians = get_sector_medians(sector)

    st.subheader("📐 Valuation Multiples")

    cols = st.columns(3)
    metrics = ["P/E", "EV/EBITDA", "P/FCF"]
    descriptions = {
        "P/E":       "Price / Earnings",
        "EV/EBITDA": "Enterprise Value / EBITDA",
        "P/FCF":     "Price / Free Cash Flow",
    }

    chart_data = []
    for i, metric in enumerate(metrics):
        val    = multiples.get(metric)
        median = medians.get(metric)
        signal, label = valuation_signal(val, median)

        with cols[i]:
            val_str    = f"{val:.1f}x"    if val    else "N/A"
            median_str = f"{median:.1f}x" if median else "N/A"
            signal_class = signal if signal != "n/a" else ""

            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-label">{descriptions[metric]}</div>
              <div class="metric-value {signal_class}">{val_str}</div>
              <div class="metric-vs">Sector median: {median_str}</div>
              <div style="margin-top:0.5rem; font-size:0.85rem;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

        if val and median:
            chart_data.append({"Metric": metric, "Company": val, "Sector Median": median})

    # Chart
    if chart_data:
        st.divider()
        st.subheader("📊 Visual Comparison")

        df_chart = pd.DataFrame(chart_data)
        fig = go.Figure()

        fig.add_trace(go.Bar(
            name=name[:20],
            x=df_chart["Metric"],
            y=df_chart["Company"],
            marker_color="#667eea",
            text=[f"{v:.1f}x" for v in df_chart["Company"]],
            textposition="outside"
        ))
        fig.add_trace(go.Bar(
            name="Sector Median",
            x=df_chart["Metric"],
            y=df_chart["Sector Median"],
            marker_color="#4a5568",
            text=[f"{v:.1f}x" for v in df_chart["Sector Median"]],
            textposition="outside"
        ))

        fig.update_layout(
            barmode="group",
            template="plotly_dark",
            plot_bgcolor="#0e1117",
            paper_bgcolor="#0e1117",
            font=dict(color="#e2e8f0"),
            legend=dict(orientation="h", y=-0.15),
            margin=dict(t=20, b=60),
            height=380,
        )
        st.plotly_chart(fig, use_container_width=True)

    # Additional info
    st.divider()
    st.subheader("🏦 Key Financials")
    k1, k2, k3, k4, k5 = st.columns(5)

    def fmt_bn(v):
        if v is None: return "N/A"
        if abs(v) >= 1e12: return f"${v/1e12:.2f}T"
        if abs(v) >= 1e9:  return f"${v/1e9:.2f}B"
        if abs(v) >= 1e6:  return f"${v/1e6:.2f}M"
        return f"${v:,.0f}"

    k1.metric("Market Cap",   fmt_bn(safe(info, "marketCap")))
    k2.metric("Revenue (TTM)",fmt_bn(safe(info, "totalRevenue")))
    k3.metric("Net Income",   fmt_bn(safe(info, "netIncomeToCommon")))
    k4.metric("Free Cash Flow",fmt_bn(safe(info, "freeCashflow")))
    k5.metric("Beta",         f"{beta:.2f}" if beta else "N/A")

    # Disclaimer
    st.divider()
    st.caption("⚠️ Data sourced from Yahoo Finance via yfinance. This tool is for educational and research purposes only. Not financial advice.")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
