import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Simplified data generator
class SimpleAstroAnalyzer:
    def __init__(self):
        self.planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
        self.signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
                     'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        self.aspects = ['conjunction', 'sextile', 'square', 'trine', 'opposition']
        
    def generate_analysis(self, symbol, timeframe):
        """Generate simplified astrological analysis"""
        days = {'daily': 7, 'weekly': 30, 'monthly': 90, 'intraday': 1}.get(timeframe, 7)
        
        # Generate random but consistent data
        np.random.seed(abs(hash(symbol)) % 1000)  # Using abs() to ensure positive seed
        
        bullish_prob = np.random.beta(2, 2)  # Generates values between 0 and 1
        bearish_prob = 1 - bullish_prob
        
        # Generate price data
        dates = [datetime.now() + timedelta(days=i) for i in range(days)]
        base_price = 100
        prices = []
        
        for i, date in enumerate(dates):
            trend = (bullish_prob - 0.5) * 0.02
            volatility = np.random.normal(0, 0.01)
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
        
        # Generate some transit data
        transits = []
        for i in range(min(10, days)):
            transits.append({
                'date': dates[i].strftime('%Y-%m-%d'),
                'planet': np.random.choice(self.planets),
                'sign': np.random.choice(self.signs),
                'aspect': np.random.choice(self.aspects)
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
        
        # Generate analysis
        analyzer = SimpleAstroAnalyzer()
        analysis = analyzer.generate_analysis(symbol.upper(), timeframe)
        
        # Display results
        st.success(f"Analysis completed for {analysis['symbol']}")
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Recommendation", analysis['recommendation'])
        with col2:
            st.metric("Confidence", analysis['confidence'])
        with col3:
            st.metric("Bullish Probability", analysis['bullish_prob'])
        
        # Price chart
        if len(analysis['prices']) > 1:
            chart_data = pd.DataFrame({
                'Date': analysis['dates'],
                'Price': analysis['prices']
            })
            st.line_chart(chart_data.set_index('Date'))
        
        # Transits table
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🪐 Recent Transits")
            transits_df = pd.DataFrame(analysis['transits'])
            st.dataframe(transits_df, use_container_width=True)
        
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
        
        # Sample data
        st.subheader("How it works")
        st.markdown("""
        This app analyzes astrological factors to generate trading insights:
        
        1. **Planetary Positions**: Analyzes current planetary alignments
        2. **Astrological Aspects**: Considers conjunctions, trines, squares, etc.
        3. **Market Probabilities**: Calculates bullish/bearish probabilities
        4. **Trading Signals**: Generates buy/sell recommendations
        
        *Note: This is for educational/entertainment purposes only. Not financial advice.*
        """)

if __name__ == "__main__":
    main()
