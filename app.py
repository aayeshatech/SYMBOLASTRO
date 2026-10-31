import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="Aayeshatech Astro Analysis and Chart Education", layout="wide")
st.title("Aayeshatech Astro Analysis and Chart Education")
st.caption("Universal NSE sector and symbol scanner • genuine uploaded prices only • Asia/Kolkata")

SECTORS = ["Private Banks","PSU Banks","Small Finance Banks","NBFC","Insurance","Broking","Housing Finance","IT","Pharma","Hospitals","Diagnostics","FMCG","Retail","Consumer Durables","Auto","Auto Ancillaries","Tyres","Metals","Mining","Oil & Gas","Power","Renewables","Realty","Cement","Infrastructure","Capital Goods","Engineering","Defence","Chemicals","Fertilizers","Sugar","Tea","Textiles","Paper","Packaging","Telecom","Media","Shipping","Logistics","Aviation","Railways","Other"]
st.info("No simulated market prices or random planetary signals. Upload timestamped OHLCV and sector mapping. Missing data are explicitly marked UNAVAILABLE.")
with st.expander("Required CSV formats", expanded=False):
    st.code("symbol,sector\nRELIANCE,Oil & Gas\nTCS,IT\nHDFCBANK,Private Banks", language="csv")
    st.code("datetime,symbol,open,high,low,close,volume,instrument,expiry\n2026-10-30 09:15:00,RELIANCE,1200,1203,1195,1198,10000,FUTURES,2026-11-26", language="csv")
    st.code("datetime,planet,sign,nakshatra,pada,sign_lord,star_lord,sub_lord,aspect\n2026-11-02 12:50:19,Moon,Cancer,Ashlesha,2,Moon,Mercury,Sun,", language="csv")
master_file = st.file_uploader("Sector/symbol master CSV (all NSE symbols)", type="csv", key="master")
prices_file = st.file_uploader("Timestamped OHLCV CSV (cash and futures kept separate)", type="csv", key="prices")
events_file = st.file_uploader("Verified Lahiri / KP event calendar CSV (optional)", type="csv", key="events")

if master_file is None or prices_file is None:
    st.subheader("Scanner coverage")
    st.metric("Supported sector groups", len(SECTORS))
    st.write(", ".join(SECTORS))
    st.warning("Scanner awaits a complete NSE symbol master and real OHLCV data. Live NSE-wide coverage is not active.")
    st.stop()

try:
    master = pd.read_csv(master_file, dtype=str)
    prices = pd.read_csv(prices_file)
    master.columns = master.columns.str.lower().str.strip()
    prices.columns = prices.columns.str.lower().str.strip()
    required_master = {"symbol","sector"}
    required_prices = {"datetime","symbol","open","high","low","close"}
    if not required_master.issubset(master.columns) or not required_prices.issubset(prices.columns):
        raise ValueError("CSV headers missing. Review required formats above.")
    master = master[["symbol","sector"]].dropna().drop_duplicates()
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
st.caption("Research interface only. No live-feed connection, Telegram delivery, automated future forecasts, or out-of-sample reliability is claimed.")
