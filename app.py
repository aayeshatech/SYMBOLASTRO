import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

# Aspect configurations
ASPECT_SIGNALS = {
    'conjunction': ('Neutral', 'gray'),
    'sextile': ('Mild Bullish', 'lightgreen'),
    'square': ('Bearish', 'pink'),
    'trine': ('Bullish', 'green'),
    'opposition': ('Strong Bearish', 'red')
}

PLANET_SYMBOLS = {
    'Sun': '☉',
    'Moon': '☽',
    'Mercury': '☿',
    'Venus': '♀',
    'Mars': '♂',
    'Jupiter': '♃',
    'Saturn': '♄'
}

@st.cache_data
def generate_analysis(symbol, timeframe):
    """Generate analysis with swing points"""
    planets = list(PLANET_SYMBOLS.keys())
    
    # Timeframe setup
    if timeframe == 'intraday':
        intervals = [(datetime.now().replace(hour=9, minute=30) + timedelta(minutes=30*i)).strftime('%H:%M') 
                    for i in range(13)]
        dates = [f"{datetime.now().strftime('%Y-%m-%d')} {time}" for time in intervals]
    else:
        days = {'daily': 7, 'weekly': 30, 'monthly': 90}.get(timeframe, 7)
        dates = [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
    
    # Generate price data with swing points
    rng = np.random.RandomState(abs(hash(symbol)) % 1000)
    base_price = 100 + rng.uniform(-5, 5)
    prices = []
    swing_points = []
    trend_dir = 1 if rng.random() > 0.5 else -1
    
    for i in range(len(dates)):
        # Simulate price movement with swings
        if i > 0 and i % (3 if timeframe == 'intraday' else 2) == 0:
            trend_dir *= -1
            swing_points.append(i)
        
        volatility = rng.normal(0, 0.003 if timeframe == 'intraday' else 0.01)
        price_move = trend_dir * abs(rng.normal(0.005, 0.002)) + volatility
        base_price *= (1 + price_move)
        prices.append(round(base_price, 2))
    
    # Generate transits with swing markers
    transits = []
    for i in range(len(dates)):
        if i in swing_points or rng.random() > 0.7:
            aspect = rng.choice(list(ASPECT_SIGNALS.keys()))
            signal, color = ASPECT_SIGNALS[aspect]
            planet = rng.choice(planets)
            
            transits.append({
                'Date': dates[i],
                'Price': prices[i],
                'Planet': planet,
                'Symbol': PLANET_SYMBOLS[planet],
                'Aspect': aspect,
                'Signal': signal,
                'Swing': '▲' if prices[i] > (prices[i-1] if i > 0 else base_price) else '▼'
            })
    
    return {
        'symbol': symbol,
        'timeframe': timeframe,
        'dates': dates,
        'prices': prices,
        'transits': transits
    }

def main():
    st.set_page_config(page_title="🌟 Astro Swing Trader", layout="wide")
    
    # Title
    st.title("🌟 Astrological Swing Trading Analysis")
    st.markdown("*Price swings with planetary aspect markers*")
    
    # Sidebar
    st.sidebar.header("Parameters")
    symbol = st.sidebar.text_input("Stock Symbol", value="AAPL")
    timeframe = st.sidebar.selectbox("Timeframe", ["intraday", "daily", "weekly", "monthly"])
    
    if st.sidebar.button("Generate Analysis", type="primary"):
        analysis = generate_analysis(symbol.upper(), timeframe)
        
        # Single price chart
        st.subheader(f"{analysis['symbol']} {analysis['timeframe'].capitalize()} Price")
        chart_data = pd.DataFrame({
            'Price': analysis['prices']
        }, index=analysis['dates'])
        st.line_chart(chart_data)
        
        # Single planetary aspects table
        st.subheader("🪐 Key Planetary Aspects")
        transits_df = pd.DataFrame(analysis['transits'])[['Date', 'Planet', 'Symbol', 'Aspect', 'Signal', 'Swing']]
        st.dataframe(
            transits_df,
            use_container_width=True
        )
    else:
        st.info("👈 Enter parameters and click 'Generate Analysis'")
        st.markdown("""
        ### Features:
        - Clean single price chart
        - Planetary aspects table with trading signals
        - Supports intraday to monthly timeframes
        """)

if __name__ == "__main__":
    main()
