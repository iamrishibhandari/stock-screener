import streamlit as st
import requests
import pandas as pd

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
    <p>Built by Rishi Bhandari &nbsp;|&nbsp; Filter stocks by key financial ratios across global indices</p>
</div>
""", unsafe_allow_html=True)

API_KEY = st.secrets["FMP_API_KEY"]

INDICES = {
    "S&P 500 (US Large Cap)": [
        "AAPL","MSFT","GOOGL","AMZN","NVDA","META","TSLA","BRK-B","JPM","V",
        "JNJ","WMT","PG","MA","HD","DIS","BAC","XOM","PFE","KO",
        "PEP","CSCO","ADBE","NFLX","INTC","T","VZ","CVX","ABT","NKE",
        "MRK","CRM","ORCL","AMD","QCOM","COST","MCD","TXN","UPS","HON",
        "IBM","GE","CAT","BA","GS","SBUX","LMT","MMM","AXP","DE",
        "UNH","LLY","AVGO","TMO","ACN","DHR","NEE","PM","RTX","LOW",
        "INTU","AMGN","SPGI","UNP","BKNG","ISRG","NOW","PLD","SYK","MDT",
        "GILD","ADI","VRTX","REGN","TJX","CB","MO","ZTS","MMC","CI"
    ],
    "Nasdaq 100 (US Tech-Heavy)": [
        "AAPL","MSFT","GOOGL","AMZN","NVDA","META","TSLA","AVGO","COST","ADBE",
        "NFLX","AMD","PEP","CSCO","INTC","QCOM","INTU","TXN","AMGN","HON",
        "BKNG","ISRG","REGN","VRTX","GILD","ADI","MU","LRCX","PANW","SNPS",
        "CDNS","MAR","ORLY","KLAC","MELI","CSX","CTAS","ABNB","FTNT","ADP",
        "MNST","PAYX","ROST","ODFL","KDP","EXC","XEL","CHTR","DXCM","BIIB"
    ],
    "Nifty 50 (India Large Cap)": [
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
}

@st.cache_data(ttl=3600)
def get_data(symbol):
    profile_url = f"https://financialmodelingprep.com/stable/profile?symbol={symbol}&apikey={API_KEY}"
    ratios_url = f"https://financialmodelingprep.com/stable/ratios-ttm?symbol={symbol}&apikey={API_KEY}"

    profile_r = requests.get(profile_url)
    ratios_r = requests.get(ratios_url)

    profile = profile_r.json()
    ratios = ratios_r.json()

    profile_data = profile[0] if profile and isinstance(profile, list) else {}
    ratios_data = ratios[0] if ratios and isinstance(ratios, list) else {}

    return profile_data, ratios_data

st.sidebar.header("Screening Filters")

index_choice = st.sidebar.selectbox("Index / Market", list(INDICES.keys()))
TICKERS = INDICES[index_choice]

st.sidebar.markdown("---")
st.sidebar.markdown("**Valuation**")
max_pe = st.sidebar.slider("Max P/E Ratio", 0, 100, 30)
max_pb = st.sidebar.slider("Max P/B Ratio", 0, 20, 5)

st.sidebar.markdown("**Profitability**")
min_roe = st.sidebar.slider("Min ROE (%)", 0, 50, 10) / 100
min_margin = st.sidebar.slider("Min Net Margin (%)", 0, 40, 5) / 100

st.sidebar.markdown("**Size**")
min_cap = st.sidebar.slider("Min Market Cap ($B)", 0, 100, 1) * 1e9
max_cap = st.sidebar.slider("Max Market Cap ($B)", 1, 4000, 500) * 1e9

st.sidebar.markdown("**Debt**")
max_debt_equity = st.sidebar.slider("Max Debt/Equity", 0.0, 5.0, 2.0)

st.sidebar.markdown("---")
run = st.sidebar.button("Run Screener", type="primary", use_container_width=True)

if run:
    with st.spinner(f"Fetching data for {len(TICKERS)} stocks in {index_choice}..."):
        results = []
        skipped = 0
        progress = st.progress(0)

        for i, symbol in enumerate(TICKERS):
            profile, ratios = get_data(symbol)
            progress.progress((i + 1) / len(TICKERS))

            if not profile or not ratios:
                skipped += 1
                continue

            pe = ratios.get("priceToEarningsRatioTTM", None)
            pb = ratios.get("priceToBookRatioTTM", None)
            roe = ratios.get("returnOnEquityTTM", None)
            net_margin = ratios.get("netProfitMarginTTM", None)
            debt_equity = ratios.get("debtToEquityRatioTTM", None)
            market_cap = profile.get("marketCap", 0)
            price = profile.get("price", 0)
            currency = profile.get("currency", "USD")

            if None in [pe, pb, roe, net_margin, debt_equity]:
                skipped += 1
                continue
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
                "Company": profile.get("companyName", ""),
                "Sector": profile.get("sector", ""),
                "Price": f"{price:,.2f} {currency}",
                "Market Cap": f"${market_cap/1e9:.2f}B",
                "P/E": f"{pe:.1f}",
                "P/B": f"{pb:.1f}",
                "ROE": f"{roe*100:.1f}%",
                "Net Margin": f"{net_margin*100:.1f}%",
                "Debt/Equity": f"{debt_equity:.2f}"
            })

        progress.empty()

        screened = len(TICKERS) - skipped

        if results:
            df = pd.DataFrame(results)
            col1, col2, col3 = st.columns(3)
            col1.metric("Stocks Screened", screened)
            col2.metric("Passed Filters", len(results))
            col3.metric("Filter Rate", f"{len(results)/screened*100:.1f}%" if screened else "0%")

            st.divider()
            st.subheader(f"{len(results)} Stocks Match Your Criteria — {index_choice}")
            st.markdown('<p class="section-label">Click column headers to sort</p>', unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True, hide_index=True)

            csv = df.to_csv(index=False)
            st.download_button("Download Results as CSV", csv, "screener_results.csv", "text/csv")
        else:
            st.warning(f"No stocks matched your filters. {skipped} stocks had incomplete data and were skipped. Try loosening the criteria.")
else:
    st.info("Select an index and adjust filters in the sidebar, then click **Run Screener** to begin.")