from flask import Flask, jsonify, render_template_string
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import Dict
import json

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
            'transits': self._serialize_dataframe(transits),
            'probabilities': self._serialize_dataframe(probabilities),
            'price_data': self._serialize_dataframe(price_data),
            'current_recommendation': self._generate_recommendation(probabilities.iloc[-1])
        }
    
    def _serialize_dataframe(self, df: pd.DataFrame) -> list:
        """Convert DataFrame to JSON-serializable format"""
        # Convert datetime objects to strings
        df_copy = df.copy()
        for col in df_copy.columns:
            if df_copy[col].dtype == 'datetime64[ns]' or isinstance(df_copy[col].iloc[0] if len(df_copy) > 0 else None, datetime):
                df_copy[col] = df_copy[col].astype(str)
        return df_copy.to_dict('records')
    
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

# HTML template for the main page
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Astrological Trading Analysis</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #555; }
        select, input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
        button { background-color: #4CAF50; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; width: 100%; }
        button:hover { background-color: #45a049; }
        .result { margin-top: 30px; padding: 20px; background-color: #f9f9f9; border-radius: 5px; display: none; }
        .recommendation { font-size: 18px; font-weight: bold; margin-bottom: 10px; }
        .buy { color: #4CAF50; }
        .sell { color: #f44336; }
        .neutral { color: #ff9800; }
        .loading { text-align: center; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌟 Astrological Trading Analysis</h1>
        <form id="analysisForm">
            <div class="form-group">
                <label for="symbol">Stock Symbol:</label>
                <input type="text" id="symbol" name="symbol" placeholder="e.g., AAPL, GOOGL, TSLA" required>
            </div>
            <div class="form-group">
                <label for="timeframe">Timeframe:</label>
                <select id="timeframe" name="timeframe" required>
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                    <option value="intraday">Intraday</option>
                </select>
            </div>
            <button type="submit">Generate Analysis</button>
        </form>
        
        <div id="result" class="result">
            <div id="loading" class="loading">Analyzing planetary positions...</div>
            <div id="analysis" style="display: none;"></div>
        </div>
    </div>

    <script>
        document.getElementById('analysisForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const symbol = document.getElementById('symbol').value.toUpperCase();
            const timeframe = document.getElementById('timeframe').value;
            
            document.getElementById('result').style.display = 'block';
            document.getElementById('loading').style.display = 'block';
            document.getElementById('analysis').style.display = 'none';
            
            fetch(`/api/analysis/${symbol}/${timeframe}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('analysis').style.display = 'block';
                    
                    const rec = data.current_recommendation;
                    let recClass = 'neutral';
                    if (rec.recommendation.includes('Buy')) recClass = 'buy';
                    else if (rec.recommendation.includes('Sell')) recClass = 'sell';
                    
                    document.getElementById('analysis').innerHTML = `
                        <h3>Analysis for ${data.symbol} (${data.timeframe})</h3>
                        <div class="recommendation ${recClass}">
                            ${rec.recommendation} - ${rec.confidence} confidence
                        </div>
                        <p><strong>Bullish Probability:</strong> ${rec.bullish_prob}</p>
                        <p><strong>Bearish Probability:</strong> ${rec.bearish_prob}</p>
                        <p><strong>Analysis Date:</strong> ${new Date().toLocaleDateString()}</p>
                        <p><em>Generated based on ${data.transits.length} planetary transit calculations</em></p>
                    `;
                })
                .catch(error => {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('analysis').innerHTML = '<p style="color: red;">Error generating analysis. Please try again.</p>';
                    console.error('Error:', error);
                });
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_TEMPLATE)

@app.route('/api/analysis/<symbol>/<timeframe>')
def get_analysis(symbol, timeframe):
    try:
        analyzer = AstroTradingAnalyzer()
        analysis = analyzer.generate_analysis(symbol.upper(), timeframe)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print("Starting Astrological Trading Analysis Server...")
    print("Access the application at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
