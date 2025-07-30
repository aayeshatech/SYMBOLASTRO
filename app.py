import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import Dict
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class AstroDataGenerator:
    """Generates simulated astronomical data for trading analysis"""
    
    PLANETS = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 
               'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']
    
    ZODIAC_SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 
                    'Leo', 'Virgo', 'Libra', 'Scorpio', 
                    'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    
    ASPECTS = ['conjunction', 'sextile', 'square', 'trine', 'opposition']
    
    def __init__(self):
        self.planet_weights = {
            'Sun': 0.9, 'Moon': 0.8, 'Mercury': 0.7, 'Venus': 0.85,
            'Mars': 0.75, 'Jupiter': 0.95, 'Saturn': 0.8, 
            'Uranus': 0.7, 'Neptune': 0.65, 'Pluto': 0.6
        }
        
        self.aspect_strengths = {
            'conjunction': 1.0, 'opposition': 0.9, 
            'trine': 0.8, 'square': 0.7, 'sextile': 0.6
        }
        
        self.bullish_planets = ['Jupiter', 'Venus', 'Sun']
        self.bearish_planets = ['Saturn', 'Mars', 'Pluto']
    
    def generate_transits(self, days: int = 30) -> pd.DataFrame:
        """Generate simulated planetary transit data"""
        start_date = datetime.now()
        dates = [start_date + timedelta(days=i) for i in range(days)]
        
        data = []
        for date in dates:
            for planet in self.PLANETS:
                entry = {
                    'date': date,
                    'planet': planet,
                    'zodiac_sign': random.choice(self.ZODIAC_SIGNS),
                    'longitude': random.uniform(0, 360),
                    'aspect': random.choice(self.ASPECTS),
                    'orb': random.uniform(0, 5),
                    'retrograde': random.random() > 0.85
                }
                data.append(entry)
        
        return pd.DataFrame(data)
    
    def calculate_aspect_strength(self, row: pd.Series) -> float:
        """Calculate strength of astrological aspect"""
        base_strength = self.aspect_strengths[row['aspect']]
        orb_penalty = 1 - (row['orb'] / 10)  # Smaller orbs are stronger
        retro_factor = 0.9 if row['retrograde'] else 1.0
        return base_strength * orb_penalty * retro_factor * self.planet_weights[row['planet']]
    
    def calculate_market_probabilities(self, transits: pd.DataFrame) -> pd.DataFrame:
        """Calculate bullish/bearish probabilities based on transits"""
        transits['aspect_strength'] = transits.apply(self.calculate_aspect_strength, axis=1)
        
        # Group by date to get daily probabilities
        daily_data = []
        for date, group in transits.groupby('date'):
            bullish_score = 0
            bearish_score = 0
            
            for _, row in group.iterrows():
                if row['planet'] in self.bullish_planets:
                    bullish_score += row['aspect_strength']
                elif row['planet'] in self.bearish_planets:
                    bearish_score += row['aspect_strength']
            
            total_score = bullish_score + bearish_score
            if total_score > 0:
                bullish_prob = bullish_score / total_score
                bearish_prob = bearish_score / total_score
            else:
                bullish_prob = 0.5
                bearish_prob = 0.5
            
            daily_data.append({
                'date': date,
                'bullish_prob': bullish_prob,
                'bearish_prob': bearish_prob,
                'transits': group.to_dict('records')
            })
        
        return pd.DataFrame(daily_data)

class AstroTradingAnalyzer:
    """Analyzes astro data for trading signals"""
    
    def __init__(self):
        self.data_generator = AstroDataGenerator()
    
    def generate_analysis(self, symbol: str, timeframe: str) -> Dict:
        """Generate complete analysis for a symbol and timeframe"""
        # Determine days to generate based on timeframe
        if timeframe == 'intraday':
            days = 1
        elif timeframe == 'daily':
            days = 7
        elif timeframe == 'weekly':
            days = 30
        elif timeframe == 'monthly':
            days = 90
        else:
            days = 7
        
        # Generate transits and calculate probabilities
        transits = self.data_generator.generate_transits(days)
        probabilities = self.data_generator.calculate_market_probabilities(transits)
        
        # Generate simulated price data
        price_data = self._generate_price_data(probabilities, timeframe)
        
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'transits': transits,
            'probabilities': probabilities,
            'price_data': price_data,
            'current_recommendation': self._generate_recommendation(probabilities.iloc[-1])
        }
    
    def _generate_price_data(self, probabilities: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """Generate simulated price data based on astro probabilities"""
        price_data = []
        base_price = 100  # Starting price
        
        for _, row in probabilities.iterrows():
            # Determine price movement based on probabilities
            direction_strength = row['bullish_prob'] - 0.5
            volatility = 0.02 * (1 + abs(direction_strength))
            
            if timeframe == 'intraday':
                # Generate data points throughout the day
                for hour in range(9, 16):  # Market hours
                    for minute in [0, 15, 30, 45]:
                        timestamp = row['date'].replace(hour=hour, minute=minute)
                        price_move = direction_strength * volatility * random.uniform(0.8, 1.2)
                        base_price *= (1 + price_move)
                        price_data.append({
                            'timestamp': timestamp,
                            'price': round(base_price, 2),
                            'bullish_prob': row['bullish_prob'],
                            'bearish_prob': row['bearish_prob']
                        })
            else:
                # Daily/Weekly/Monthly data
                price_move = direction_strength * volatility
                base_price *= (1 + price_move)
                price_data.append({
                    'timestamp': row['date'],
                    'price': round(base_price, 2),
                    'bullish_prob': row['bullish_prob'],
                    'bearish_prob': row['bearish_prob']
                })
        
        return pd.DataFrame(price_data)
    
    def _generate_recommendation(self, latest_prob: pd.Series) -> Dict:
        """Generate trading recommendation based on probabilities"""
        strength = abs(latest_prob['bullish_prob'] - 0.5)
        
        if latest_prob['bullish_prob'] > 0.6:
            recommendation = 'Strong Buy'
            confidence = strength * 100
        elif latest_prob['bullish_prob'] > 0.55:
            recommendation = 'Buy'
            confidence = strength * 80
        elif latest_prob['bearish_prob'] > 0.6:
            recommendation = 'Strong Sell'
            confidence = strength * 100
        elif latest_prob['bearish_prob'] > 0.55:
            recommendation = 'Sell'
            confidence = strength * 80
        else:
            recommendation = 'Neutral'
            confidence = 0
        
        return {
            'recommendation': recommendation,
            'confidence': f"{confidence:.1f}%",
            'bullish_prob': f"{latest_prob['bullish_prob']*100:.1f}%",
            'bearish_prob': f"{latest_prob['bearish_prob']*100:.1f}%"
        }

def create_price_chart(price_data, symbol):
    """Create a price chart with bullish/bearish probabilities"""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=[f'{symbol} Price Chart', 'Bullish/Bearish Probabilities'],
        row_heights=[0.7, 0.3],
        vertical_spacing=0.1
    )
    
    # Price chart
    fig.add_trace(
        go.Scatter(
            x=price_data['timestamp'],
            y=price_data['price'],
            mode='lines',
            name='Price',
            line=dict(color='blue', width=2)
        ),
        row=1, col=1
    )
    
    # Probability charts
    fig.add_trace(
        go.Scatter(
            x=price_data['timestamp'],
            y=price_data['bullish_prob'],
            mode='lines',
            name='Bullish Probability',
            line=dict(color='green', width=2)
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=price_data['timestamp'],
            y=price_data['bearish_prob'],
            mode='lines',
            name='Bearish Probability',
            line=dict(color='red', width=2)
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        title=f"Astrological Trading Analysis - {symbol}",
        xaxis_title="Time",
        height=600,
        showlegend=True
    )
    
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="Probability", row=2, col=1)
    
    return fig

def main():
    st.set_page_config(page_title="🌟 Astrological Trading Analysis", layout="wide")
    
    st.title("🌟 Astrological Trading Analysis")
    st.markdown("*Generate trading insights based on planetary alignments and astrological aspects*")
    
    # Sidebar inputs
    st.sidebar.header("Analysis Parameters")
    symbol = st.sidebar.text_input("Stock Symbol", value="AAPL", help="Enter stock ticker (e.g., AAPL, GOOGL)")
    timeframe = st.sidebar.selectbox(
        "Timeframe",
        ["daily", "weekly", "monthly", "intraday"],
        help="Select analysis timeframe"
    )
    
    if st.sidebar.button("Generate Analysis", type="primary"):
        with st.spinner("Analyzing planetary positions..."):
            analyzer = AstroTradingAnalyzer()
            analysis = analyzer.generate_analysis(symbol.upper(), timeframe)
            
            # Display recommendation
            rec = analysis['current_recommendation']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if 'Buy' in rec['recommendation']:
                    st.success(f"**{rec['recommendation']}**")
                elif 'Sell' in rec['recommendation']:
                    st.error(f"**{rec['recommendation']}**")
                else:
                    st.warning(f"**{rec['recommendation']}**")
            
            with col2:
                st.metric("Confidence", rec['confidence'])
            
            with col3:
                st.metric("Bullish Probability", rec['bullish_prob'])
            
            # Display chart
            chart = create_price_chart(analysis['price_data'], symbol.upper())
            st.plotly_chart(chart, use_container_width=True)
            
            # Display detailed analysis
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Market Probabilities")
                prob_df = analysis['probabilities'][['date', 'bullish_prob', 'bearish_prob']].copy()
                prob_df['bullish_prob'] = (prob_df['bullish_prob'] * 100).round(1)
                prob_df['bearish_prob'] = (prob_df['bearish_prob'] * 100).round(1)
                prob_df['date'] = pd.to_datetime(prob_df['date']).dt.strftime('%Y-%m-%d')
                st.dataframe(prob_df, use_container_width=True)
            
            with col2:
                st.subheader("🪐 Recent Transits")
                transit_df = analysis['transits'].head(20)[['date', 'planet', 'zodiac_sign', 'aspect']].copy()
                transit_df['date'] = pd.to_datetime(transit_df['date']).dt.strftime('%Y-%m-%d')
                st.dataframe(transit_df, use_container_width=True)
            
            # Analysis summary
            st.subheader("📈 Analysis Summary")
            st.info(f"""
            **Symbol:** {analysis['symbol']}  
            **Timeframe:** {analysis['timeframe']}  
            **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
            **Total Transits Analyzed:** {len(analysis['transits'])}  
            **Current Recommendation:** {rec['recommendation']} ({rec['confidence']} confidence)
            """)

if __name__ == "__main__":
    main()
