"""NSE equity universe and best-effort Yahoo Finance cash candles.
No futures substitution, no synthetic pricing. Not an exchange licensed real-time feed.
"""
from io import StringIO
import pandas as pd
import requests
import yfinance as yf

NSE_MASTER_URL = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"

def nse_equity_master():
    r = requests.get(NSE_MASTER_URL, timeout=18, headers={
        "User-Agent": "Mozilla/5.0 (compatible; NSE-Research-Dashboard/1.0)",
        "Accept": "text/csv,*/*",
        "Referer": "https://www.nseindia.com/"})
    r.raise_for_status()
    raw = pd.read_csv(StringIO(r.content.decode("utf-8-sig")))
    raw.columns = raw.columns.str.strip().str.upper()
    if "SYMBOL" not in raw.columns or "SERIES" not in raw.columns:
        raise ValueError("NSE equity master schema has changed")
    raw = raw[raw["SERIES"].astype(str).str.strip().eq("EQ")].copy()
    out = pd.DataFrame({"symbol": raw["SYMBOL"].astype(str).str.strip().str.upper()})
    out = out[out.symbol.ne("")].drop_duplicates()
    out["sector"] = "Unclassified"
    return out.reset_index(drop=True)

def yahoo_cash_candles(symbols, period="1mo", interval="1d"):
    """Fetch only the selected batch. Failed names remain missing; never fabricate rows."""
    symbols = list(dict.fromkeys(str(s).strip().upper() for s in symbols if str(s).strip()))
    if not symbols:
        return pd.DataFrame(columns=["datetime","symbol","open","high","low","close","volume","instrument","expiry"])
    frames=[]
    # Small batches avoid overwhelming Yahoo or the dashboard.
    for start in range(0,len(symbols),15):
        batch=symbols[start:start+15]
        tickers=[s+".NS" for s in batch]
        try:
            raw=yf.download(tickers=tickers, period=period, interval=interval,
                group_by="ticker", auto_adjust=False, threads=False, progress=False, timeout=15)
        except Exception:
            continue
        if raw is None or raw.empty:
            continue
        for sym,ticker in zip(batch,tickers):
            try:
                df=raw[ticker].copy() if isinstance(raw.columns,pd.MultiIndex) else raw.copy()
                df=df.rename(columns={c:str(c).strip().lower() for c in df.columns})
                required={"open","high","low","close"}
                if not required.issubset(df.columns):
                    continue
                df=df.reset_index()
                datecol="Datetime" if "Datetime" in df.columns else ("Date" if "Date" in df.columns else df.columns[0])
                df=df.rename(columns={datecol:"datetime"})
                ts=pd.to_datetime(df["datetime"],utc=True,errors="coerce").dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
                df["datetime"]=ts
                df["symbol"]=sym
                df["instrument"]="CASH"
                df["expiry"]=""
                if "volume" not in df.columns: df["volume"]=pd.NA
                frames.append(df[["datetime","symbol","open","high","low","close","volume","instrument","expiry"]])
            except Exception:
                continue
    if not frames:
        return pd.DataFrame(columns=["datetime","symbol","open","high","low","close","volume","instrument","expiry"])
    return pd.concat(frames,ignore_index=True).dropna(subset=["datetime","close"])
