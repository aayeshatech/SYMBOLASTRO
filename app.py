import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Market configurations
INDIAN_MARKET = {
    'Stocks': ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'HDFC', 'ICICIBANK', 'KOTAKBANK', 'BHARTIARTL'],
    'Indices': ['NIFTY50', 'BANKNIFTY', 'NIFTYIT', 'SENSEX']
}

GLOBAL_MARKET = {
    'Commodities': ['GOLD', 'SILVER', 'CRUDEOIL', 'NATURALGAS'],
    'Indices': ['DOWJONES', 'SNP500', 'NASDAQ', 'FTSE100'],
    'Crypto': ['BTC', 'ETH', 'XRP', 'SOL']
}

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
def generate_analysis(symbol, timeframe, market_type):
    """Generate analysis with swing points"""
    planets = list(PLANET_SYMBOLS.keys())
    
    # Timeframe setup
    if timeframe == 'intraday':
        if market_type == 'Indian Market':
            # Indian market hours (9:15 AM to 3:30 PM)
            start_time = datetime.now().replace(hour=9, minute=15)
            intervals = [(start_time + timedelta(minutes=15*i)).strftime('%H:%M') 
                         for i in range(25)]  # 6.5 hours in 15-min intervals
        else:
            # Global market hours (5:00 AM to 11:55 PM)
            start_time = datetime.now().replace(hour=5, minute=0)
            intervals = [(start_time + timedelta(minutes=30*i)).strftime('%H:%M') 
                         for i in range(36)]  # 18 hours in 30-min intervals
            
        dates = [f"{datetime.now().strftime('%Y-%m-%d')} {time}" for time in intervals]
    else:
        days = {'daily': 1, 'weekly': 7, 'monthly': 30}.get(timeframe, 7)
        dates = [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
    
    # Generate price data with swing points
    rng = np.random.RandomState(abs(hash(symbol)) % 1000)
    base_price = 100 + rng.uniform(-5, 5)
    prices = []
    swing_points = []
    trend_dir = 1 if rng.random() > 0.5 else -1
    
    for i in range(len(dates)):
        # Simulate price movement with swings
        if i > 0 and i % (2 if timeframe == 'intraday' else 1) == 0:
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
        'market': market_type,
        'dates': dates,
        'prices': prices,
        'transits': transits
    }

def main():
    st.set_page_config(page_title="🌟 Astro Swing Trader Pro", layout="wide")
    
    # Title
    st.title("🌟 Astrological Swing Trading Analysis")
    st.markdown("*Market-specific price swings with planetary aspects*")
    
    # Market selection
    market_type = st.radio(
        "Select Market Type:",
        ["Indian Market", "Global Market"],
        horizontal=True
    )
    
    # Sidebar
    st.sidebar.header("Parameters")
    
    # Dynamic symbol selection based on market type
    if market_type == 'Indian Market':
        category = st.sidebar.selectbox("Category", list(INDIAN_MARKET.keys()))
        symbol = st.sidebar.selectbox("Symbol", INDIAN_MARKET[category])
    else:
        category = st.sidebar.selectbox("Category", list(GLOBAL_MARKET.keys()))
        symbol = st.sidebar.selectbox("Symbol", GLOBAL_MARKET[category])
    
    timeframe = st.sidebar.selectbox("Timeframe", ["intraday", "daily", "weekly", "monthly"])
    
    if st.sidebar.button("Generate Analysis", type="primary"):
        analysis = generate_analysis(symbol, timeframe, market_type)
        
        # Display market info
        st.subheader(f"{market_type} - {symbol} ({timeframe.capitalize()})")
        
        # Single price chart
        st.line_chart(pd.DataFrame({
            'Price': analysis['prices']
        }, index=analysis['dates']))
        
        # Planetary aspects table
        st.subheader("🪐 Key Planetary Aspects")
        transits_df = pd.DataFrame(analysis['transits'])[['Date', 'Planet', 'Symbol', 'Aspect', 'Signal', 'Swing']]
        st.dataframe(transits_df, use_container_width=True)
        
        # Market-specific notes
        if market_type == 'Indian Market':
            st.info("Indian Market Hours: 9:15 AM to 3:30 PM (15-min intervals)")
        else:
            st.info("Global Market Hours: 5:00 AM to 11:55 PM (30-min intervals)")
    else:
        st.info("👈 Select market parameters and click 'Generate Analysis'")
        st.markdown("""
        ### Features:
        - **Indian Market**: Stocks and indices (9:15 AM to 3:30 PM)
        - **Global Market**: Commodities, indices, crypto (5:00 AM to 11:55 PM)
        - Planetary aspects with trading signals
        - Multiple timeframe analysis
        """)

if __name__ == "__main__":
    main()
