import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Aspect configurations
ASPECT_IMPACT = {
    'conjunction': ('Neutral', 0),
    'sextile': ('Mild Bullish', 1),
    'square': ('Bearish', -1),
    'trine': ('Bullish', 2),
    'opposition': ('Strong Bearish', -2)
}

def generate_swing_chart(timeframe):
    """Generate swing chart data for the specified timeframe"""
    if timeframe == 'intraday':
        times = [(datetime.now().replace(hour=9, minute=30) + timedelta(minutes=30*i)).strftime('%H:%M') 
                for i in range(13)]
        dates = [f"Today {time}" for time in times]
    else:
        days = {'daily': 1, 'weekly': 7, 'monthly': 30}[timeframe]
        dates = [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
    
    # Generate random swing data (0-20 scale)
    rng = np.random.RandomState(42)
    swing_values = np.clip(np.cumsum(rng.normal(0, 3, len(dates)) + 10, 0, 20).astype(int)
    
    # Generate aspects
    aspects = []
    for i in range(len(dates)):
        if i % (2 if timeframe == 'intraday' else 1) == 0:
            aspect = rng.choice(list(ASPECT_IMPACT.keys()))
            aspects.append({
                'Time': dates[i],
                'Aspect': aspect,
                'Impact': ASPECT_IMPACT[aspect][1],
                'Label': ASPECT_IMPACT[aspect][0]
            })
    
    return {
        'dates': dates,
        'swing_values': swing_values,
        'aspects': aspects
    }

def display_swing_chart(data, timeframe):
    """Display the swing chart with aspects"""
    st.subheader(f"General Astro Swing Chart - {datetime.now().strftime('%d %B %Y')}")
    
    # Display aspects summary
    aspect_counts = pd.DataFrame(data['aspects'])['Label'].value_counts()
    for label, count in aspect_counts.items():
        st.markdown(f"- **{label}**")
    
    st.markdown("---")
    
    # Display swing chart
    st.markdown("## Swing Index (0 to 20)")
    chart_data = pd.DataFrame({
        'Swing Index': data['swing_values'],
        'Time': data['dates']
    }).set_index('Time')
    
    st.line_chart(chart_data)
    
    # Display squared times
    squared_times = [asp['Time'] for asp in data['aspects'] if asp['Aspect'] == 'square']
    if squared_times:
        st.markdown("## Squared")
        for time in squared_times:
            st.markdown(f"- {time}")

def main():
    st.set_page_config(page_title="Astro Swing Charts", layout="wide")
    
    st.title("Astrological Swing Charts")
    st.markdown("Track market swings based on planetary aspects")
    
    # Timeframe selection
    timeframe = st.radio(
        "Select Timeframe:",
        ["intraday", "daily", "weekly", "monthly"],
        horizontal=True
    )
    
    if st.button("Generate Swing Chart"):
        data = generate_swing_chart(timeframe)
        display_swing_chart(data, timeframe)
    else:
        st.info("Select a timeframe and click 'Generate Swing Chart'")

if __name__ == "__main__":
    main()
