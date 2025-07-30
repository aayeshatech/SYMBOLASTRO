import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import plotly.graph_objects as go

# Aspect configurations
ASPECT_SIGNALS = {
    'conjunction': ('Neutral', 'gray'),
    'sextile': ('Mild Bullish', 'lightgreen'),
    'square': ('Bearish', 'pink'),
    'trine': ('Bullish', 'green'),
    'opposition': ('Strong Bearish', 'red')
}

PLANET_COLORS = {
    'Sun': 'gold',
    'Moon': 'silver',
    'Mercury': 'brown',
    'Venus': 'orange',
    'Mars': 'red',
    'Jupiter': 'purple',
    'Saturn': 'blue'
}

@st.cache_data
def generate_analysis(symbol, timeframe):
    """Generate analysis with swing points"""
    planets = list(PLANET_COLORS.keys())
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
                'Aspect': aspect,
                'Signal': signal,
                'Color': PLANET_COLORS[planet],
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

def create_swing_chart(analysis):
    """Create interactive swing chart with astro markers"""
    fig = go.Figure()
    
    # Price line
    fig.add_trace(go.Scatter(
        x=analysis['dates'],
        y=analysis['prices'],
        mode='lines',
        name='Price',
        line=dict(color='royalblue', width=2)
    ))
    
    # Swing points
    swing_dates = [analysis['dates'][i] for i in analysis['swings']]
    swing_prices = [analysis['prices'][i] for i in analysis['swings']]
    fig.add_trace(go.Scatter(
        x=swing_dates,
        y=swing_prices,
        mode='markers',
        name='Swing Points',
        marker=dict(color='red', size=10, symbol='diamond')
    ))
    
    # Astro markers
    for transit in analysis['transits']:
        fig.add_annotation(
            x=transit['Date'],
            y=transit['Price'],
            text=f"{transit['Planet']} {transit['Aspect']}",
            showarrow=True,
            arrowhead=1,
            ax=0,
            ay=-40,
            font=dict(color=transit['Color'], size=10),
            bgcolor='rgba(255,255,255,0.8)'
        )
    
    # Chart styling
    fig.update_layout(
        title=f"{analysis['symbol']} {analysis['timeframe'].capitalize()} Price with Astro Aspects",
        xaxis_title='Date/Time',
        yaxis_title='Price',
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig

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
                    fig = create_swing_chart(analysis)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Transits table
                    st.subheader("🪐 Key Planetary Aspects")
                    transits_df = pd.DataFrame(analysis['transits'])[['Date', 'Planet', 'Aspect', 'Signal', 'Swing']]
                    st.dataframe(
                        transits_df.style.apply(
                            lambda x: [f"background-color: {ASPECT_SIGNALS[x['Aspect']][1]}" if x.name == 'Signal' else '' for _, x in transits_df.iterrows()],
                            axis=1
                        ),
                        use_container_width=True
                    )
                    
                    time.sleep(2)  # Simulate live updates
        else:
            analysis = generate_analysis(symbol.upper(), timeframe)
            fig = create_swing_chart(analysis)
            st.plotly_chart(fig, use_container_width=True)
            
            # Transits table
            st.subheader("🪐 Key Planetary Aspects")
            transits_df = pd.DataFrame(analysis['transits'])[['Date', 'Planet', 'Aspect', 'Signal', 'Swing']]
            st.dataframe(
                transits_df.style.apply(
                    lambda x: [f"background-color: {ASPECT_SIGNALS[x['Aspect']][1]}" if x.name == 'Signal' else '' for _, x in transits_df.iterrows()],
                    axis=1
                ),
                use_container_width=True
            )
    else:
        st.info("👈 Enter parameters and click 'Generate Analysis'")
        st.image("https://via.placeholder.com/800x300?text=Astro+Swing+Trader", use_column_width=True)
        st.markdown("""
        ### Features:
        - **Dynamic Swing Charts**: Visualize price swings with astrological markers
        - **Intraday Mode**: Live simulation with 30-minute intervals
        - **Planetary Aspects**: Marked directly on price chart
        - **Swing Signals**: Diamond markers show pivot points
        """)

if __name__ == "__main__":
    main()
