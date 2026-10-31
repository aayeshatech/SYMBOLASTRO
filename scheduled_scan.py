"""Scheduled NSE cash scanner. Market-hour guard is authoritative.
Outputs CSV for the scanned partition; never uses futures or synthetic candles.
"""
import argparse
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo
import pandas as pd
from market_feed import nse_equity_master, yahoo_cash_candles

# NSE equity calendar 2026; review annually against official NSE holidays.
HOLIDAYS_2026 = {
"2026-01-15","2026-01-26","2026-03-03","2026-03-26","2026-03-31",
"2026-04-03","2026-04-14","2026-05-01","2026-05-28","2026-06-26",
"2026-09-14","2026-10-02","2026-10-20","2026-11-10",
"2026-11-24","2026-12-25"}
IST = ZoneInfo("Asia/Kolkata")
def allowed(now):
    now=now.astimezone(IST)
    return (now.weekday()<5 and now.date().isoformat() not in HOLIDAYS_2026
            and time(9,15)<=now.time().replace(tzinfo=None)<=time(15,30))
def slot(now):
    t=now.astimezone(IST)
    return ((t.hour*60+t.minute)-(9*60+15))//15
def select_partition(master,now,batch_size):
    # Different subsets over session; no claim of complete all-symbol real-time coverage.
    ordered=master.sort_values("symbol").reset_index(drop=True)
    if ordered.empty: return []
    start=(slot(now)*batch_size)%len(ordered)
    return pd.concat([ordered.iloc[start:],ordered.iloc[:start]]).head(batch_size).symbol.tolist()
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--batch-size",type=int,default=60)
    ap.add_argument("--verify-only",action="store_true")
    args=ap.parse_args()
    now=datetime.now(IST)
    assert not allowed(datetime(2026,11,1,10,0,tzinfo=IST))
    assert not allowed(datetime(2026,11,10,10,0,tzinfo=IST))
    assert allowed(datetime(2026,11,2,9,15,tzinfo=IST))
    assert allowed(datetime(2026,11,2,15,30,tzinfo=IST))
    assert not allowed(datetime(2026,11,2,15,31,tzinfo=IST))
    print("Session gate tests passed")
    if args.verify_only: return
    if not allowed(now):
        print(f"SKIPPED: NSE cash closed at {now.isoformat()}")
        return
    master=nse_equity_master()
    names=select_partition(master,now,args.batch_size)
    if not names: raise RuntimeError("Empty NSE symbol master")
    data=yahoo_cash_candles(names,period="5d",interval="15m")
    if data.empty: raise RuntimeError("Yahoo returned zero usable cash candles")
    data=data[data.instrument.eq("CASH")].copy()
    data["source"]="Yahoo Finance (possibly delayed)"
    data["fetched_at_ist"]=now.isoformat()
    # Only report real observed candles, never treat empty names as flat prices.
    out=Path("output")
    out.mkdir(exist_ok=True)
    stamp=now.strftime("%Y%m%d_%H%M")
    data.to_csv(out/f"nse_cash_{stamp}.csv",index=False)
    coverage=pd.DataFrame({"symbol":names})
    coverage["received"]=coverage.symbol.isin(data.symbol.unique())
    coverage.to_csv(out/f"coverage_{stamp}.csv",index=False)
    print(f"Scheduled subset: {len(names)}, prices returned: {data.symbol.nunique()}; output {stamp}")
if __name__=="__main__": main()
