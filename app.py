import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time  # For intraday simulation

# Aspect to trading signal mapping
ASPECT_SIGNALS = {
    'conjunction': 'Neutral',
    'sextile': 'Mild Bullish',
    'square': 'Bearish',
    'trine': 'Bullish',
    'opposition': 'Strong Bearish'
}

# Pre-calculate data to make the app load faster
@st.cache_data
def generate_analysis(symbol, timeframe):
    """Generate simplified astrological analysis"""
    planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    
    if timeframe == 'intraday':
        days = 1
        intervals = ['09:30', '10:00', '10:30', '11:00', '11:30', 
                    '12:00', '12:30', '13:00', '13:30', '14:00',
                    '14:30', '15:00', '15:30', '16:00']
    else:
        days = {'daily': 7, 'weekly': 30, 'monthly': 90}.get(timeframe, 7)
        intervals = None
    
    # Generate consistent random data based on symbol
    rng = np.random.RandomState(abs(hash(symbol)) % 1000)
    bullish_prob = rng.beta(2, 2)
    bearish_prob = 1 - bullish_prob
    
    # Generate price data
    if timeframe == 'intraday':
        dates = [f"{datetime.now().strftime('%Y-%m-%d')} {time}" for time in intervals]
        base_price = 100
        prices = []
        for i in range(len(intervals)):
            trend = (bullish_prob - 0.5) * 0.005  # Smaller moves for intraday
            volatility = rng.normal(0, 0.003)
            base_price *= (1 + trend + volatility)
            prices.append(round(base_price, 2))
    else:
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
        rec_color = "green"
    elif bullish_prob > 0.55:
        recommendation = "Buy"
        confidence = f"{(bullish_prob - 0.5) * 150:.1f}%"
        rec_color = "lightgreen"
    elif bullish_prob < 0.35:
        recommendation = "Strong Sell"
        confidence = f"{(0.5 - bullish_prob) * 200:.1f}%"
        rec_color = "red"
    elif bullish_prob < 0.45:
        recommendation = "Sell"
        confidence = f"{(0.5 - bullish_prob) * 150:.1f}%"
        rec_color = "pink"
    else:
        recommendation = "Neutral"
        confidence = "Low"
        rec_color = "gray"
    
    # Generate transit data with trading signals
    transits = []
    num_transits = len(intervals) if timeframe == 'intraday' else min(10, days)
    
    for i in range(num_transits):
        aspect = rng.choice(list(ASPECT_SIGNALS.keys()))
        signal = ASPECT_SIGNALS[aspect]
        
        # Determine signal strength color
        if "Strong" in signal:
            signal_color = "darkred" if "Bearish" in signal else "darkgreen"
        elif "Bullish" in signal:
            signal_color = "green"
        elif "Bearish" in signal:
            signal_color = "red"
        else:
            signal_color = "gray"
        
        transits.append({
            'date': dates[i].strftime('%Y-%m-%d') if timeframe != 'intraday' else dates[i],
            'planet': rng.choice(planets),
            'sign': rng.choice(signs),
            'aspect': aspect,
            'signal': signal,
            'color': signal_color
        })
    
    return {
        'symbol': symbol,
        'timeframe': timeframe,
        'recommendation': recommendation,
        'confidence': confidence,
        'rec_color': rec_color,
        'bullish_prob': f"{bullish_prob*100:.1f}%",
        'bearish_prob': f"{bearish_prob*100:.1f}%",
        'dates': dates,
        'prices': prices,
        'transits': transits
    }

def color_cell(val, color):
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
        
        # Display results
        st.success(f"Analysis completed for {analysis['symbol']} ({analysis['timeframe']})")
        
        # Metrics with colored backgrounds
        cols = st.columns(3)
        with cols[0]:
            st.markdown(f"""
            <div style='background-color:{analysis['rec_color']}; padding:10px; border-radius:5px; color:white'>
                <h3 style='color:white'>Recommendation</h3>
                <h2>{analysis['recommendation']}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with cols[1]:
            st.metric("Confidence Level", analysis['confidence'])
        
        with cols[2]:
            st.metric("Bullish Probability", analysis['bullish_prob'])
        
        # Price chart
        st.subheader(f"📈 {'Intraday' if timeframe == 'intraday' else 'Historical'} Price Movement")
        if len(analysis['prices']) > 1:
            chart_data = pd.DataFrame({
                'Price': analysis['prices']
            }, index=analysis['dates'])
            st.line_chart(chart_data)
        
        # Enhanced transits table with colors
        st.subheader("🪐 Planetary Aspects & Trading Signals")
        transits_df = pd.DataFrame(analysis['transits'])
        
        # Apply color coding
        styled_df = transits_df.style.apply(lambda x: [
            color_cell(x['signal'], x['color']) if x.name == 'signal' else '' 
            for _, x in transits_df.iterrows()
        ], axis=1)
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # Analysis summary
        st.subheader("📊 Analysis Summary")
        st.info(f"""
        **Symbol:** {analysis['symbol']}  
        **Timeframe:** {analysis['timeframe']}  
        **Bullish Probability:** {analysis['bullish_prob']}  
        **Bearish Probability:** {analysis['bearish_prob']}  
        **Recommendation:** <span style='color:{analysis['rec_color']}; font-weight:bold'>{analysis['recommendation']}</span>  
        **Confidence:** {analysis['confidence']}  
        **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """, unsafe_allow_html=True)
    
    else:
        # Default view
        st.info("👈 Enter a stock symbol and click 'Generate Analysis' to begin")
        st.image("https://via.placeholder.com/800x300?text=Advanced+Astro+Trading", use_column_width=True)
        
        st.markdown("""
        ### Enhanced Features:
        - **Intraday Analysis**: 30-minute interval planetary aspects
        - **Signal Strength**: Color-coded trading signals
        - **Aspect Interpretation**:
          - Trine → Bullish
          - Sextile → Mild Bullish  
          - Square → Bearish
          - Opposition → Strong Bearish
          - Conjunction → Neutral
        
        *Note: For educational purposes only. Always conduct your own analysis.*
        """)

if __name__ == "__main__":
    main()
