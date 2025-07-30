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
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    
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
    last_swing = base_price
    trend_dir = 1 if rng.random() > 0.5 else -1
    
    for i in range(len(dates)):
        # Simulate price movement with swings
        if i > 0 and i % (3 if timeframe == 'intraday' else 2) == 0:
            trend_dir *= -1
            swing_points.append(i)
            last_swing = prices[-1] if prices else base_price
        
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
                'Color': color,
                'Swing': '▲' if prices[i] > (prices[i-1] if i > 0 else base_price) else '▼'
            })
    
    return {
        'symbol': symbol,
        'timeframe': timeframe,
        'dates': dates,
        'prices': prices,
        'swings': swing_points,
        'transits': transits
    }

def display_swing_chart(analysis):
    """Display swing chart using Streamlit's native charts"""
    # Create DataFrame for the chart
    chart_data = pd.DataFrame({
        'Price': analysis['prices'],
        'Swing': [np.nan] * len(analysis['prices'])
    }, index=analysis['dates'])
    
    # Mark swing points
    for i in analysis['swings']:
        chart_data.iloc[i, 1] = chart_data.iloc[i, 0]
    
    # Display the main chart
    st.line_chart(chart_data['Price'])
    
    # Add swing point markers
    swing_df = chart_data.dropna(subset=['Swing'])
    if not swing_df.empty:
        st.scatter_chart(swing_df['Swing'])

def color_row(row):
    return [f'background-color: {row["Color"]}; color: white'] * len(row)

def main():
    st.set_page_config(page_title="🌟 Astro Swing Trader", layout="wide")
    
    # Title
    st.title("🌟 Astrological Swing Trading Analysis")
    st.markdown("*Dynamic price swings with planetary aspect markers*")
    
    # Sidebar
    st.sidebar.header("Parameters")
    symbol = st.sidebar.text_input("Stock Symbol", value="AAPL")
    timeframe = st.sidebar.selectbox("Timeframe", ["intraday", "daily", "weekly", "monthly"])
    live_mode = st.sidebar.checkbox("Live Simulation Mode", True) if timeframe == 'intraday' else False
    
    if st.sidebar.button("Generate Analysis", type="primary"):
        placeholder = st.empty()
        
        if live_mode:
            for _ in range(3):  # Simulate 3 updates for demo
                with placeholder.container():
                    analysis = generate_analysis(symbol.upper(), timeframe)
                    display_swing_chart(analysis)
                    
                    # Transits table
                    st.subheader("🪐 Key Planetary Aspects")
                    transits_df = pd.DataFrame(analysis['transits'])[['Date', 'Planet', 'Symbol', 'Aspect', 'Signal', 'Swing']]
                    st.dataframe(
                        transits_df,
                        use_container_width=True
                    )
                    
                    time.sleep(2)
        else:
            analysis = generate_analysis(symbol.upper(), timeframe)
            display_swing_chart(analysis)
            
            # Transits table
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
        - **Swing Analysis**: Automatic pivot point detection
        - **Planetary Markers**: Astrological symbols and aspects
        - **Timeframe Support**: Intraday to monthly analysis
        """)

if __name__ == "__main__":
    main()
