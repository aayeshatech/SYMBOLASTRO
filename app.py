import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from io import BytesIO
from market_feed import nse_equity_master, yahoo_cash_candles

st.set_page_config(page_title="Aayeshatech Astro Analysis and Chart Education", layout="wide")
st.title("Aayeshatech Astro Analysis and Chart Education")
st.caption("Universal NSE sector and symbol scanner • official NSE equity master + Yahoo cash candles or CSV • Asia/Kolkata")

SECTORS = ["Private Banks","PSU Banks","Small Finance Banks","NBFC","Insurance","Broking","Housing Finance","IT","Pharma","Hospitals","Diagnostics","FMCG","Retail","Consumer Durables","Auto","Auto Ancillaries","Tyres","Metals","Mining","Oil & Gas","Power","Renewables","Realty","Cement","Infrastructure","Capital Goods","Engineering","Defence","Chemicals","Fertilizers","Sugar","Tea","Textiles","Paper","Packaging","Telecom","Media","Shipping","Logistics","Aviation","Railways","Other"]
st.info("No simulated prices or planetary signals. Auto mode loads NSE cash symbols and best-effort Yahoo candles; futures require contract-specific data.")
with st.expander("Required CSV formats", expanded=False):
    st.code("symbol,sector\nRELIANCE,Oil & Gas\nTCS,IT\nHDFCBANK,Private Banks", language="csv")
    st.code("datetime,symbol,open,high,low,close,volume,instrument,expiry\n2026-10-30 09:15:00,RELIANCE,1200,1203,1195,1198,10000,FUTURES,2026-11-26", language="csv")
    st.code("datetime,planet,sign,nakshatra,pada,sign_lord,star_lord,sub_lord,aspect\n2026-11-02 12:50:19,Moon,Cancer,Ashlesha,2,Moon,Mercury,Sun,", language="csv")
mode=st.radio("Market data source",["Automatic NSE + Yahoo (cash)","Uploaded CSV"],horizontal=True)
master_file = None
prices_file = None
if mode == "Uploaded CSV":
    master_file = st.file_uploader("Sector/symbol master CSV", type="csv", key="master")
    prices_file = st.file_uploader("Timestamped OHLCV CSV", type="csv", key="prices")
else:
    @st.cache_data(ttl=86400,show_spinner=False)
    def get_nse_master():
        return nse_equity_master()
    @st.cache_data(ttl=900,show_spinner=False)
    def get_yahoo(symbols,period,interval):
        return yahoo_cash_candles(symbols,period,interval)
    try:
        auto_master=get_nse_master()
        st.success(f"NSE equity master loaded: {len(auto_master)} EQ symbols (not futures).")
    except Exception as e:
        st.error(f"Automatic NSE master unavailable: {e}. Upload CSV instead.")
        auto_master=None
    sectors_csv=st.file_uploader("Optional accurate symbol-to-sector CSV (symbol,sector)",type="csv",key="sector_map")
    if auto_master is not None and sectors_csv is not None:
        sectors=pd.read_csv(sectors_csv,dtype=str)
        sectors.columns=sectors.columns.str.strip().str.lower()
        if {"symbol","sector"}.issubset(sectors.columns):
            sectors["symbol"]=sectors.symbol.str.upper().str.strip()
            auto_master=auto_master.drop(columns="sector").merge(
                sectors[["symbol","sector"]].drop_duplicates("symbol"),on="symbol",how="left")
            auto_master["sector"]=auto_master.sector.fillna("Unclassified")
    if auto_master is not None:
        choice=st.selectbox("Select symbols to fetch",["Manual ticker selection","All symbols (slow, rate limits possible)"])
        if choice=="All symbols (slow, rate limits possible)":
            selected=auto_master.symbol.tolist()
            st.warning("Full NSE fetch may take a long time or be rate-limited. Data gaps are expected; no guaranteed continuous coverage.")
        else:
            defaults=[s for s in ["RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK","SBIN"] if s in set(auto_master.symbol)]
            selected=st.multiselect("Select NSE cash symbols",auto_master.symbol.tolist(),default=defaults)
        interval=st.selectbox("Candle interval",["1d","1h","30m","15m","5m"])
        period=st.selectbox("History",["5d","1mo","3mo","6mo","1y"],index=1)
        if interval!="1d" and period in ["3mo","6mo","1y"]:
            st.warning("Yahoo intraday history is limited. Choose 5d or 1mo.")
            period="1mo"
        if st.button("Fetch selected Yahoo candles",type="primary"):
            with st.spinner("Fetching actual Yahoo cash candles..."):
                st.session_state["auto_candles"]=get_yahoo(tuple(selected),period,interval)
                st.session_state["auto_selection"]=tuple(selected)
        if "auto_candles" in st.session_state and st.session_state.get("auto_selection")==tuple(selected):
            auto_prices=st.session_state["auto_candles"]
            st.caption(f"Yahoo returned {len(auto_prices)} actual candles across {auto_prices.symbol.nunique() if len(auto_prices) else 0} symbols. Source may be delayed.")
        else:
            auto_prices=None

events_file = st.file_uploader("Verified Lahiri / KP event calendar CSV (optional)", type="csv", key="events")
if mode=="Uploaded CSV" and (master_file is None or prices_file is None):
    st.warning("Upload both NSE symbol master and timestamped candles.")
    st.stop()
if mode!="Uploaded CSV" and (auto_master is None or auto_prices is None or auto_prices.empty):
    st.warning("Fetch price candles to start the scanner. NSE coverage and Yahoo price coverage are different.")
    st.stop()
try:
    master = pd.read_csv(master_file,dtype=str) if mode=="Uploaded CSV" else auto_master.copy()
    prices = pd.read_csv(prices_file) if mode=="Uploaded CSV" else auto_prices.copy()
    master.columns = master.columns.str.lower().str.strip()
    prices.columns = prices.columns.str.lower().str.strip()
    required_master = {"symbol","sector"}
    required_prices = {"datetime","symbol","open","high","low","close"}
    if not required_master.issubset(master.columns) or not required_prices.issubset(prices.columns):
        raise ValueError("CSV headers missing. Review required formats above.")
    master = master[["symbol","sector"]].fillna({"sector":"Unclassified"}).drop_duplicates()
    master["symbol"] = master["symbol"].str.upper().str.strip()
    prices["symbol"] = prices["symbol"].astype(str).str.upper().str.strip()
    prices["datetime"] = pd.to_datetime(prices["datetime"], errors="coerce")
    for c in ("open","high","low","close"):
        prices[c] = pd.to_numeric(prices[c], errors="coerce")
    prices = prices.dropna(subset=["datetime","symbol","open","high","low","close"])
    if "instrument" not in prices:
        prices["instrument"] = "UNSPECIFIED"
    prices["instrument"] = prices["instrument"].fillna("UNSPECIFIED").astype(str).str.upper()
    if "expiry" not in prices:
        prices["expiry"] = ""
    prices["expiry"] = prices["expiry"].fillna("").astype(str)
    prices = prices.sort_values("datetime")
except Exception as e:
    st.error(f"Unable to load source data: {e}")
    st.stop()

c1,c2,c3 = st.columns(3)
c1.metric("Master symbols",master.symbol.nunique())
c2.metric("Symbols with prices",prices.symbol.nunique())
c3.metric("Sectors mapped",master.sector.nunique())
uncovered = sorted(set(master.symbol)-set(prices.symbol))
if uncovered:
    st.warning(f"{len(uncovered)} master symbols do not have price candles. Unavailable, not scored.")

universe = master.merge(prices, on="symbol", how="left", validate="one_to_many")
universe["sector"] = universe["sector"].fillna("Unmapped")
sector_options = ["ALL"] + sorted(master.sector.unique().tolist())
sector = st.selectbox("Sector",sector_options)
scope = universe if sector == "ALL" else universe[universe.sector == sector]
instrument = st.selectbox("Instrument",["ALL"]+sorted(prices.instrument.unique().tolist()))
if instrument != "ALL":
    scope = scope[scope.instrument == instrument]
# Note: do not aggregate different futures expiries into a continuous price series.
def summarize(g):
    g=g.dropna(subset=["close"]).sort_values("datetime")
    if len(g)<2:
        return pd.Series({"Last":np.nan,"Change %":np.nan,"Trend":"UNAVAILABLE","Bars":len(g),"Last timestamp":pd.NaT})
    close=g.close.to_numpy(dtype=float)
    ret=100*(close[-1]/close[-2]-1) if close[-2] else np.nan
    ema9=pd.Series(close).ewm(span=9,adjust=False).mean().iloc[-1]
    ema21=pd.Series(close).ewm(span=21,adjust=False).mean().iloc[-1]
    trend="BULLISH" if len(close)>=21 and close[-1]>ema9>ema21 else ("BEARISH" if len(close)>=21 and close[-1]<ema9<ema21 else "UNCONFIRMED")
    return pd.Series({"Last":close[-1],"Change %":ret,"Trend":trend,"Bars":len(g),"Last timestamp":g.datetime.iloc[-1]})
groups=["symbol","sector","instrument","expiry"]
report=scope.groupby(groups,dropna=False).apply(summarize).reset_index()
tab1,tab2,tab3=st.tabs(["Symbol scanner","Sector breadth","Astro event matcher"])
with tab1:
    st.dataframe(report.sort_values(["sector","symbol"]),use_container_width=True,hide_index=True)
    symbol_options=sorted(report.symbol.unique().tolist())
    if symbol_options:
        chosen=st.selectbox("Inspect symbol",symbol_options)
        rows=scope[scope.symbol==chosen].dropna(subset=["close"]).copy()
        if len(rows):
            # Different contracts must not be spliced together.
            contract=st.selectbox("Instrument / contract",sorted((rows.instrument+" / "+rows.expiry).unique()))
            rows=rows[(rows.instrument+" / "+rows.expiry)==contract].sort_values("datetime")
            st.line_chart(rows.set_index("datetime")["close"])
            st.caption("Chart uses recorded candles only. Source timeframe equals uploaded candle interval.")
with tab2:
    valid=report[report.Trend.isin(["BULLISH","BEARISH","UNCONFIRMED"])]
    breadth=valid.groupby("sector").agg(available=("symbol","nunique"),bullish=("Trend",lambda s:(s=="BULLISH").sum()),bearish=("Trend",lambda s:(s=="BEARISH").sum())).reset_index()
    if not breadth.empty:
        breadth["bullish_breadth_%"]=np.round(100*breadth.bullish/breadth.available,1)
    st.dataframe(breadth.sort_values("bullish_breadth_%",ascending=False),use_container_width=True,hide_index=True)
    st.caption("Sector results are breadth of uploaded constituent trends, not independently verified sector index prices.")
with tab3:
    if events_file:
        events=pd.read_csv(events_file)
        events.columns=events.columns.str.lower().str.strip()
        if "datetime" in events:
            events["datetime"]=pd.to_datetime(events.datetime,errors="coerce")
            events=events.dropna(subset=["datetime"])
            st.dataframe(events,use_container_width=True)
            st.caption("Events are supplied observation timestamps, not validated directional signals. Match them with 5/15/30/60-minute post-event returns only when compatible intraday candles are provided; do not infer causation.")
        else:
            st.error("Astro event CSV must contain datetime column.")
    else:
        st.info("Upload verified planetary events to view the event schedule alongside your real price dataset.")
st.download_button("Export scanner results", report.to_csv(index=False).encode(),file_name="nse_symbol_sector_scan.csv",mime="text/csv")
st.caption("Yahoo is a best-effort delayed cash feed, not an exchange guaranteed real-time service. TradingView connector is not active inside this app. Futures require expiry-specific licensed or uploaded data. KP event backtests and Telegram delivery are not yet implemented.")
