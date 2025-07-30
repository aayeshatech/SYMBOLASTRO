import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Aspect to trading signal mapping
ASPECT_SIGNALS = {
    'conjunction': 'Neutral',
    'sextile': 'Mild Bullish',
    'square': 'Bearish',
    'trine': 'Bullish',
    'opposition': 'Strong Bearish'
}

# Color mapping for signals
SIGNAL_COLORS = {
    'Neutral': 'gray',
    'Mild Bullish': 'lightgreen',
    'Bullish': 'green',
    'Bearish': 'pink',
    'Strong Bearish': 'red',
    'Strong Buy': 'darkgreen',
    'Buy': 'green',
    'Sell': 'red',
    'Strong Sell': 'darkred'
}

@st.cache_data
def generate_analysis(symbol, timeframe):
    """Generate simplified astrological analysis"""
    planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    
    if timeframe == 'intraday':
        intervals = ['09:30', '10:00', '10:30', '11:00', '11:30', 
                    '12:00', '12:30', '13:00', '13:30', '14:00',
                    '14:30', '15:00', '15:30', '16:00']
        dates = [f"{datetime.now().strftime('%Y-%m-%d')} {time}" for time in intervals]
        days = 1
    else:
        days = {'daily': 7, 'weekly': 30, 'monthly': 90}.get(timeframe, 7)
        dates = [datetime.now() + timedelta(days=i) for i in range(days)]
        intervals = None
    
    rng = np.random.RandomState(abs(hash(symbol)) % 1000)
    bullish_prob = rng.beta(2, 2)
    bearish_prob = 1 - bullish_prob
    
    # Generate price data
    base_price = 100
    prices = []
    for i in range(len(dates)):
        trend = (bullish_prob - 0.5) * (0.005 if timeframe == 'intraday' else 0.02)
        volatility = rng.normal(0, 0.003 if timeframe == 'intraday' else 0.01)
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
    num_transits = len(intervals) if timeframe == 'intraday' else min(10, days)
    
    for i in range(num_transits):
        aspect = rng.choice(list(ASPECT_SIGNALS.keys()))
        signal = ASPECT_SIGNALS[aspect]
        
        transits.append({
            'Date': dates[i] if timeframe == 'intraday' else dates[i].strftime('%Y-%m-%d'),
            'Planet': rng.choice(planets),
            'Sign': rng.choice(signs),
            'Aspect': aspect,
            'Signal': signal
        })
    
    return {
        'symbol': symbol,
        'timeframe': timeframe,
        'recommendation': recommendation,
        'confidence': confidence,
        'bullish_prob': f"{bullish_prob*100:.1f}%",
        'bearish_prob': f"{bearish_prob*100:.1f}%",
        'dates': dates,
        'prices': prices,
        'transits': transits
    }

def color_signal(val):
    color = SIGNAL_COLORS.get(val, 'white')
    return f'background-color: {color}; color: white; font-weight: bold;'

def main():
    st.set_page_config(page_title="🌟 Astro Trading Pro", layout="wide")
    
    # Title
    st.title("🌟 Advanced Astrological Trading Analysis")
    st.markdown("*Intraday and positional trading signals based on planetary aspects*")
    
    # Sidebar
    st.sidebar.header("Parameters")
    symbol = st.sidebar.text_input("Stock Symbol", value="AAPL")
    timeframe = st.sidebar.selectbox("Timeframe", ["intraday", "daily", "weekly", "monthly"])
    
    if st.sidebar.button("Generate Analysis", type="primary"):
        with st.spinner("🔮 Analyzing planetary alignments..."):
            analysis = generate_analysis(symbol.upper(), timeframe)
        
        st.success(f"Analysis completed for {analysis['symbol']} ({analysis['timeframe']})")
        
        # Metrics
        cols = st.columns(3)
        cols[0].metric("Recommendation", analysis['recommendation'])
        cols[1].metric("Confidence Level", analysis['confidence'])
        cols[2].metric("Bullish Probability", analysis['bullish_prob'])
        
        # Price chart
        st.subheader(f"📈 {'Intraday' if timeframe == 'intraday' else 'Historical'} Price Movement")
        chart_data = pd.DataFrame({'Price': analysis['prices']}, index=analysis['dates'])
        st.line_chart(chart_data)
        
        # Transits table
        st.subheader("🪐 Planetary Aspects & Trading Signals")
        transits_df = pd.DataFrame(analysis['transits'])
        
        # Apply styling only to Signal column
        styled_df = transits_df.style.applymap(color_signal, subset=['Signal'])
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            column_order=['Date', 'Planet', 'Sign', 'Aspect', 'Signal']
        )
        
        # Analysis summary
        st.subheader("📊 Analysis Summary")
        st.info(f"""
        **Symbol:** {analysis['symbol']}  
        **Timeframe:** {analysis['timeframe']}  
        **Bullish Probability:** {analysis['bullish_prob']}  
        **Bearish Probability:** {analysis['bearish_prob']}  
        **Recommendation:** {analysis['recommendation']}  
        **Confidence:** {analysis['confidence']}  
        **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """)

if __name__ == "__main__":
    main()
