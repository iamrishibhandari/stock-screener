import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="Stock Screener", layout="wide", page_icon="🔍")

st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    h1 { color: #0f172a !important; font-weight: 700 !important; }
    h2, h3 { color: #1e293b !important; font-weight: 600 !important; }
    div[data-testid="stMetricLabel"] {
        color: #475569 !important; font-size: 0.8rem !important;
        font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.05em !important;
    }
    div[data-testid="stMetricValue"] { color: #0f172a !important; font-size: 1.6rem !important; font-weight: 700 !important; }
    div[data-testid="metric-container"] {
        background: #ffffff !important; border-radius: 12px !important;
        padding: 1.2rem 1.5rem !important; border: 1px solid #e2e8f0 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
    }
    .header-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
        padding: 2rem 2.5rem; border-radius: 16px; margin-bottom: 2rem;
    }
    .header-banner h1 { color: #ffffff !important; margin: 0 !important; }
    .header-banner p { color: #94a3b8 !important; margin: 0.3rem 0 0 0 !important; font-size: 0.9rem !important; font-weight: 500 !important; }
    .section-label {
        color: #64748b !important; font-size: 0.75rem !important;
        font-weight: 700 !important; text-transform: uppercase !important;
        letter-spacing: 0.08em !important; margin-bottom: 0.5rem !important;
    }
    thead tr th { background: #f1f5f9 !important; color: #334155 !important; font-weight: 700 !important; }
    tbody tr td { color: #1e293b !important; }
    tbody tr:nth-child(even) { background: #f8fafc !important; }
    tbody tr:nth-child(odd) { background: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-banner">
    <h1>Stock Screener</h1>
    <p>Built by Rishi Bhandari &nbsp;|&nbsp; Filter stocks across major US and Indian indices</p>
</div>
""", unsafe_allow_html=True)

DOW_30 = [
    "AAPL","AMGN","AXP","BA","CAT","CRM","CSCO","CVX","DIS","DOW",
    "GS","HD","HON","IBM","INTC","JNJ","JPM","KO","MCD","MMM",
    "MRK","MSFT","NKE","NVDA","PG","TRV","UNH","V","VZ","WMT"
]

NASDAQ_100 = [
    "AAPL","MSFT","GOOGL","AMZN","NVDA","META","TSLA","AVGO","COST","ADBE",
    "NFLX","AMD","PEP","CSCO","INTC","QCOM","INTU","TXN","AMGN","HON",
    "BKNG","ISRG","REGN","VRTX","GILD","ADI","MU","LRCX","PANW","SNPS",
    "CDNS","MAR","ORLY","KLAC","MELI","CSX","CTAS","ABNB","FTNT","ADP",
    "MNST","PAYX","ROST","ODFL","KDP","EXC","XEL","CHTR","DXCM","BIIB"
]

NIFTY_50 = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","ICICIBANK.NS","INFY.NS","HINDUNILVR.NS",
    "ITC.NS","SBIN.NS","BHARTIARTL.NS","KOTAKBANK.NS","LT.NS","BAJFINANCE.NS",
    "AXISBANK.NS","ASIANPAINT.NS","MARUTI.NS","SUNPHARMA.NS","TITAN.NS","ULTRACEMCO.NS",
    "WIPRO.NS","ONGC.NS","NTPC.NS","NESTLEIND.NS","POWERGRID.NS","M&M.NS",
    "TATAMOTORS.NS","TATASTEEL.NS","ADANIENT.NS","JSWSTEEL.NS","HCLTECH.NS","TECHM.NS",
    "BAJAJFINSV.NS","COALINDIA.NS","HINDALCO.NS","DRREDDY.NS","CIPLA.NS","GRASIM.NS",
    "BRITANNIA.NS","EICHERMOT.NS","DIVISLAB.NS","APOLLOHOSP.NS","BPCL.NS","INDUSINDBK.NS",
    "HEROMOTOCO.NS","SBILIFE.NS","HDFCLIFE.NS","UPL.NS","TATACONSUM.NS","BAJAJ-AUTO.NS",
    "SHREECEM.NS","ADANIPORTS.NS"
]

SENSEX_30 = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","ICICIBANK.NS","INFY.NS","HINDUNILVR.NS",
    "ITC.NS","SBIN.NS","BHARTIARTL.NS","KOTAKBANK.NS","LT.NS","BAJFINANCE.NS",
    "AXISBANK.NS","ASIANPAINT.NS","MARUTI.NS","SUNPHARMA.NS","TITAN.NS","ULTRACEMCO.NS",
    "WIPRO.NS","NTPC.NS","NESTLEIND.NS","POWERGRID.NS","M&M.NS","TATAMOTORS.NS",
    "TATASTEEL.NS","HCLTECH.NS","TECHM.NS","BAJAJFINSV.NS","INDUSINDBK.NS","JSWSTEEL.NS"
]

@st.cache_data(ttl=86400)
def get_sp500_tickers():
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        tables = pd.read_html(url)
        df = tables[0]
        tickers = df["Symbol"].tolist()
        return [t.replace(".", "-") for t in tickers]
    except Exception:
        return DOW_30

INDICES = {
    "S&P 500 (US — 500 stocks, ~5-8 min)": "SP500",
    "Nasdaq 100 (US Tech)": NASDAQ_100,
    "Dow Jones 30 (US Blue Chip)": DOW_30,
    "Nifty 50 (India Large Cap)": NIFTY_50,
    "Sensex 30 (India Blue Chip)": SENSEX_30
}

@st.cache_data(ttl=3600)
def get_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        return info
    except Exception:
        return {}

st.sidebar.header("Screening Filters")

index_choice = st.sidebar.selectbox("Index / Market", list(INDICES.keys()))

if INDICES[index_choice] == "SP500":
    TICKERS = get_sp500_tickers()
else:
    TICKERS = INDICES[index_choice]

st.sidebar.caption(f"{len(TICKERS)} stocks in this index")

st.sidebar.markdown("---")
st.sidebar.markdown("**Valuation**")
max_pe = st.sidebar.slider("Max P/E Ratio", 0, 100, 50)
max_pb = st.sidebar.slider("Max P/B Ratio", 0, 30, 15)

st.sidebar.markdown("**Profitability**")
min_roe = st.sidebar.slider("Min ROE (%)", -50, 50, 0) / 100
min_margin = st.sidebar.slider("Min Net Margin (%)", -50, 40, 0) / 100

st.sidebar.markdown("**Size**")
min_cap = st.sidebar.slider("Min Market Cap ($B)", 0, 100, 0) * 1e9
max_cap = st.sidebar.slider("Max Market Cap ($B)", 1, 4000, 4000) * 1e9

st.sidebar.markdown("**Debt**")
max_debt_equity = st.sidebar.slider("Max Debt/Equity", 0.0, 10.0, 10.0)

st.sidebar.markdown("---")
run = st.sidebar.button("Run Screener", type="primary", use_container_width=True)

if run:
    status_text = st.empty()
    progress = st.progress(0)
    results = []
    skipped = 0

    for i, symbol in enumerate(TICKERS):
        status_text.text(f"Screening {symbol}... ({i+1}/{len(TICKERS)})")
        info = get_data(symbol)
        progress.progress((i + 1) / len(TICKERS))
        time.sleep(0.2)

        if not info or "currentPrice" not in info:
            skipped += 1
            continue

        pe = info.get("trailingPE", None)
        pb = info.get("priceToBook", None)
        roe = info.get("returnOnEquity", None)
        net_margin = info.get("profitMargins", None)
        debt_equity = info.get("debtToEquity", None)
        market_cap = info.get("marketCap", 0)
        price = info.get("currentPrice", 0)
        currency = info.get("currency", "USD")

        if debt_equity is not None:
            debt_equity = debt_equity / 100

        if pe is None or pb is None or roe is None or net_margin is None:
            skipped += 1
            continue

        if debt_equity is None:
            debt_equity = 0

        if market_cap < min_cap or market_cap > max_cap:
            continue
        if pe > max_pe or pe < 0:
            continue
        if pb > max_pb or pb < 0:
            continue
        if roe < min_roe:
            continue
        if net_margin < min_margin:
            continue
        if debt_equity > max_debt_equity:
            continue

        results.append({
            "Symbol": symbol,
            "Company": info.get("longName", symbol),
            "Sector": info.get("sector", "N/A"),
            "Price": f"{price:,.2f} {currency}",
            "Market Cap": f"${market_cap/1e9:.2f}B",
            "P/E": f"{pe:.1f}",
            "P/B": f"{pb:.1f}",
            "ROE": f"{roe*100:.1f}%",
            "Net Margin": f"{net_margin*100:.1f}%",
            "Debt/Equity": f"{debt_equity:.2f}"
        })

    progress.empty()
    status_text.empty()

    screened = len(TICKERS) - skipped

    if results:
        df = pd.DataFrame(results)
        col1, col2, col3 = st.columns(3)
        col1.metric("Stocks with Complete Data", screened)
        col2.metric("Passed Filters", len(results))
        col3.metric("Filter Rate", f"{len(results)/screened*100:.1f}%" if screened else "0%")

        st.divider()
        st.subheader(f"{len(results)} Stocks Match Your Criteria — {index_choice}")
        st.markdown('<p class="section-label">Click column headers to sort</p>', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, hide_index=True)

        csv = df.to_csv(index=False)
        st.download_button("Download Results as CSV", csv, "screener_results.csv", "text/csv")
    else:
        st.warning(f"No stocks matched your filters out of {screened} screened ({skipped} skipped due to missing data). Try widening your filter ranges.")
else:
    st.info("Select an index and adjust filters in the sidebar, then click **Run Screener** to begin. Note: S&P 500 takes 5-8 minutes due to Yahoo Finance rate limits.")
