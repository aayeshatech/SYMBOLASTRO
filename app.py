import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Pre-calculate data to make the app load faster
@st.cache_data
def generate_analysis(symbol, timeframe):
    """Generate simplified astrological analysis"""
    planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    aspects = ['conjunction', 'sextile', 'square', 'trine', 'opposition']
    
    days = {'daily': 7, 'weekly': 30, 'monthly': 90, 'intraday': 1}.get(timeframe, 7)
    
    # Generate consistent random data based on symbol
    rng = np.random.RandomState(abs(hash(symbol)) % 1000)
    bullish_prob = rng.beta(2, 2)
    bearish_prob = 1 - bullish_prob
    
    # Generate price data
    dates = [datetime.now() + timedelta(days=i) for i in range(days)]
    base_price = 100
    prices = []
    
    for date in dates:
        trend = (bullish_prob - 0.5) * 0.02
        volatility = rng.normal(0, 0.01)
        base_price *= (1 + trend + volatility)
        prices.append(round(base_price, 2))
    
    # Generate recommendation
    if bullish_prob > 0.65:
        recommendation = "Strong Buy"
        confidence = f"{(bullish_prob - 0.5) * 200:.1f}%"
    elif bullish_prob > 0.55:
        recommendation = "Buy"
        confidence = f"{(bullish_prob - 0.5) * 150:.1f}%"
    elif bullish_prob < 0.35:
        recommendation = "Strong Sell"
        confidence = f"{(0.5 - bullish_prob) * 200:.1f}%"
    elif bullish_prob < 0.45:
        recommendation = "Sell"
        confidence = f"{(0.5 - bullish_prob) * 150:.1f}%"
    else:
        recommendation = "Neutral"
        confidence = "Low"
    
    # Generate transit data
    transits = []
    for i in range(min(5, days)):  # Reduced from 10 to 5 for faster load
        transits.append({
            'date': dates[i].strftime('%Y-%m-%d'),
            'planet': rng.choice(planets),
            'sign': rng.choice(signs),
            'aspect': rng.choice(aspects)
        })
    
    return {
        'symbol': symbol,
        'timeframe': timeframe,
        'recommendation': recommendation,
        'confidence': confidence,
        'bullish_prob': f"{bullish_prob*100:.1f}%",
        'bearish_prob': f"{bearish_prob*100:.1f}%",
        'dates': [d.strftime('%Y-%m-%d') for d in dates],
        'prices': prices,
        'transits': transits
    }

def main():
    st.set_page_config(page_title="🌟 Astro Trading", layout="wide")
    
    # Title
    st.title("🌟 Astrological Trading Analysis")
    st.markdown("*Generate trading insights based on planetary alignments*")
    
    # Sidebar
    st.sidebar.header("Parameters")
    symbol = st.sidebar.text_input("Stock Symbol", value="AAPL")
    timeframe = st.sidebar.selectbox("Timeframe", ["daily", "weekly", "monthly", "intraday"])
    
    if st.sidebar.button("Generate Analysis", type="primary"):
        with st.spinner("🔮 Consulting the stars..."):
            analysis = generate_analysis(symbol.upper(), timeframe)
        
        # Display results
        st.success(f"Analysis completed for {analysis['symbol']}")
        
        # Metrics
        cols = st.columns(3)
        cols[0].metric("Recommendation", analysis['recommendation'])
        cols[1].metric("Confidence", analysis['confidence'])
        cols[2].metric("Bullish Probability", analysis['bullish_prob'])
        
        # Price chart
        if len(analysis['prices']) > 1:
            st.line_chart(pd.DataFrame({
                'Price': analysis['prices']
            }, index=analysis['dates']))
        
        # Analysis display
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🪐 Key Transits")
            st.dataframe(pd.DataFrame(analysis['transits']), use_container_width=True)
        
        with col2:
            st.subheader("📊 Analysis Summary")
            st.info(f"""
            **Symbol:** {analysis['symbol']}  
            **Timeframe:** {analysis['timeframe']}  
            **Bullish Probability:** {analysis['bullish_prob']}  
            **Bearish Probability:** {analysis['bearish_prob']}  
            **Recommendation:** {analysis['recommendation']}  
            **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
            """)
    else:
        # Default view
        st.info("👈 Enter a stock symbol and click 'Generate Analysis' to begin")
        st.image("https://via.placeholder.com/800x300?text=Astrological+Trading+Analysis", use_column_width=True)
        
        st.markdown("""
        ### How It Works
        This app analyzes astrological factors to generate trading insights:
        
        1. **Planetary Positions**: Current planetary alignments
        2. **Astrological Aspects**: Conjunctions, trines, squares
        3. **Market Probabilities**: Bullish/bearish probabilities
        4. **Trading Signals**: Buy/sell recommendations
        
        *Note: For educational/entertainment purposes only. Not financial advice.*
        """)

if __name__ == "__main__":
    main()
