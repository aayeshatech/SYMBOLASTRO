import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import plotly.graph_objects as go
from plotly.subplots import make_subplots
app = Flask(__name__)

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
            'transits': transits.to_dict('records'),
            'probabilities': probabilities.to_dict('records'),
            'price_data': price_data.to_dict('records'),
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
                            'price': base_price,
                            'bullish_prob': row['bullish_prob'],
                            'bearish_prob': row['bearish_prob']
                        })
            else:
                # Daily/Weekly/Monthly data
                price_move = direction_strength * volatility
                base_price *= (1 + price_move)
                price_data.append({
                    'timestamp': row['date'],
                    'price': base_price,
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analysis/<symbol>/<timeframe>')
def get_analysis(symbol, timeframe):
    analyzer = AstroTradingAnalyzer()
    analysis = analyzer.generate_analysis(symbol, timeframe)
    return jsonify(analysis)

if __name__ == '__main__':
    app.run(debug=True)
