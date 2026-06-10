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
    <p>Built by Rishi Bhandari &nbsp;|&nbsp; Filter stocks by key financial ratios</p>
</div>
""", unsafe_allow_html=True)

API_KEY = st.secrets["FMP_API_KEY"]

@st.cache_data(ttl=3600)
def get_stocks(exchange):
    url = f"https://financialmodelingprep.com/api/v3/stock-screener?exchange={exchange}&limit=200&apikey={API_KEY}"
    r = requests.get(url)
    return r.json() if r.status_code == 200 else []

@st.cache_data(ttl=3600)
def get_ratios(symbol):
    url = f"https://financialmodelingprep.com/api/v3/ratios-ttm/{symbol}?apikey={API_KEY}"
    r = requests.get(url)
    data = r.json()
    return data[0] if data and isinstance(data, list) else {}

st.sidebar.header("Screening Filters")

exchange = st.sidebar.selectbox("Exchange", ["NASDAQ", "NYSE", "AMEX"])

st.sidebar.markdown("---")
st.sidebar.markdown("**Valuation**")
max_pe = st.sidebar.slider("Max P/E Ratio", 0, 100, 30)
max_pb = st.sidebar.slider("Max P/B Ratio", 0, 20, 5)

st.sidebar.markdown("**Profitability**")
min_roe = st.sidebar.slider("Min ROE (%)", 0, 50, 10) / 100
min_margin = st.sidebar.slider("Min Net Margin (%)", 0, 40, 5) / 100

st.sidebar.markdown("**Size**")
min_cap = st.sidebar.slider("Min Market Cap ($B)", 0, 100, 1) * 1e9
max_cap = st.sidebar.slider("Max Market Cap ($B)", 1, 3000, 500) * 1e9

st.sidebar.markdown("**Debt**")
max_debt_equity = st.sidebar.slider("Max Debt/Equity", 0.0, 5.0, 2.0)

st.sidebar.markdown("---")
run = st.sidebar.button("Run Screener", type="primary", use_container_width=True)

if run:
    with st.spinner("Fetching stocks and ratios..."):
        stocks = get_stocks(exchange)

        if not stocks:
            st.error("Could not fetch stock data. Check your API key.")
        else:
            results = []
            progress = st.progress(0)
            total = min(len(stocks), 100)

            for i, stock in enumerate(stocks[:100]):
                symbol = stock.get("symbol", "")
                ratios = get_ratios(symbol)

                if not ratios:
                    continue

                pe = ratios.get("peRatioTTM", None)
                pb = ratios.get("priceToBookRatioTTM", None)
                roe = ratios.get("returnOnEquityTTM", None)
                net_margin = ratios.get("netProfitMarginTTM", None)
                debt_equity = ratios.get("debtEquityRatioTTM", None)
                market_cap = stock.get("marketCap", 0)

                if None in [pe, pb, roe, net_margin, debt_equity]:
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
                    "Company": stock.get("companyName", ""),
                    "Sector": stock.get("sector", ""),
                    "Price": f"${stock.get('price', 0):,.2f}",
                    "Market Cap": f"${market_cap/1e9:.2f}B",
                    "P/E": f"{pe:.1f}",
                    "P/B": f"{pb:.1f}",
                    "ROE": f"{roe*100:.1f}%",
                    "Net Margin": f"{net_margin*100:.1f}%",
                    "Debt/Equity": f"{debt_equity:.2f}"
                })

                progress.progress((i + 1) / total)

            progress.empty()

            if results:
                df = pd.DataFrame(results)
                col1, col2, col3 = st.columns(3)
                col1.metric("Stocks Screened", total)
                col2.metric("Passed Filters", len(results))
                col3.metric("Filter Rate", f"{len(results)/total*100:.1f}%")

                st.divider()
                st.subheader(f"{len(results)} Stocks Match Your Criteria")
                st.markdown('<p class="section-label">Click column headers to sort</p>', unsafe_allow_html=True)
                st.dataframe(df, use_container_width=True, hide_index=True)

                csv = df.to_csv(index=False)
                st.download_button("Download Results as CSV", csv, "screener_results.csv", "text/csv")
            else:
                st.warning("No stocks matched your filters. Try loosening the criteria.")