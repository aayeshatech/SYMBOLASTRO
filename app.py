<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Astro Trading Analysis</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/luxon@2.0.2"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-luxon@1.0.0"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .symbol-selector, .timeframe-selector {
            padding: 8px;
            border-radius: 4px;
            border: 1px solid #ddd;
        }
        .chart-container {
            position: relative;
            height: 400px;
            margin-bottom: 20px;
        }
        .recommendation {
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
            text-align: center;
            font-weight: bold;
            font-size: 18px;
        }
        .bullish {
            background-color: rgba(0, 255, 0, 0.1);
            border: 1px solid green;
            color: darkgreen;
        }
        .bearish {
            background-color: rgba(255, 0, 0, 0.1);
            border: 1px solid red;
            color: darkred;
        }
        .neutral {
            background-color: rgba(200, 200, 200, 0.1);
            border: 1px solid gray;
            color: #333;
        }
        .transits-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        .transits-table th, .transits-table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        .transits-table th {
            background-color: #f2f2f2;
        }
        .transits-table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .bullish-cell {
            background-color: rgba(0, 255, 0, 0.1);
        }
        .bearish-cell {
            background-color: rgba(255, 0, 0, 0.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Astro Trading Analysis</h1>
            <div>
                <select id="symbol" class="symbol-selector">
                    <option value="AAPL">AAPL</option>
                    <option value="MSFT">MSFT</option>
                    <option value="GOOGL">GOOGL</option>
                    <option value="AMZN">AMZN</option>
                    <option value="TSLA">TSLA</option>
                </select>
                <select id="timeframe" class="timeframe-selector">
                    <option value="intraday">Intraday</option>
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                </select>
                <button id="update-btn">Update Analysis</button>
            </div>
        </div>
        
        <div id="recommendation" class="recommendation neutral">
            Select symbol and timeframe to generate analysis
        </div>
        
        <div class="chart-container">
            <canvas id="priceChart"></canvas>
        </div>
        
        <div class="chart-container">
            <canvas id="probabilityChart"></canvas>
        </div>
        
        <h2>Planetary Transits</h2>
        <table class="transits-table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Planet</th>
                    <th>Zodiac Sign</th>
                    <th>Aspect</th>
                    <th>Orb</th>
                    <th>Retrograde</th>
                    <th>Influence</th>
                </tr>
            </thead>
            <tbody id="transits-body">
                <tr>
                    <td colspan="7">No data available</td>
                </tr>
            </tbody>
        </table>
    </div>

    <script>
        // Global chart references
        let priceChart, probabilityChart;
        
        // DOM elements
        const updateBtn = document.getElementById('update-btn');
        const symbolSelect = document.getElementById('symbol');
        const timeframeSelect = document.getElementById('timeframe');
        const recommendationDiv = document.getElementById('recommendation');
        const transitsBody = document.getElementById('transits-body');
        
        // Event listeners
        updateBtn.addEventListener('click', updateAnalysis);
        
        // Initialize with default data
        updateAnalysis();
        
        async function updateAnalysis() {
            const symbol = symbolSelect.value;
            const timeframe = timeframeSelect.value;
            
            try {
                const response = await fetch(`/api/analysis/${symbol}/${timeframe}`);
                const analysis = await response.json();
                updateCharts(analysis);
                updateRecommendation(analysis.current_recommendation);
                updateTransitsTable(analysis.probabilities);
            } catch (error) {
                console.error('Error updating analysis:', error);
                alert('Failed to update analysis. See console for details.');
            }
        }
        
        function updateCharts(analysis) {
            // Process price data
            const priceData = analysis.price_data.map(item => ({
                x: new Date(item.timestamp),
                y: item.price
            }));
            
            // Process probability data
            const probData = analysis.probabilities.map(item => ({
                x: new Date(item.date),
                bullish: item.bullish_prob * 100,
                bearish: item.bearish_prob * 100
            }));
            
            // Update or create price chart
            const priceCtx = document.getElementById('priceChart').getContext('2d');
            if (priceChart) {
                priceChart.data.datasets[0].data = priceData;
                priceChart.options.title.text = `${analysis.symbol} Price - ${analysis.timeframe}`;
                priceChart.update();
            } else {
                priceChart = new Chart(priceCtx, {
                    type: 'line',
                    data: {
                        datasets: [{
                            label: 'Price',
                            data: priceData,
                            borderColor: 'rgb(54, 162, 235)',
                            backgroundColor: 'rgba(54, 162, 235, 0.1)',
                            borderWidth: 2,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        title: {
                            display: true,
                            text: `${analysis.symbol} Price - ${analysis.timeframe}`
                        },
                        scales: {
                            xAxes: [{
                                type: 'time',
                                time: {
                                    unit: analysis.timeframe === 'intraday' ? 'hour' : 
                                          analysis.timeframe === 'daily' ? 'day' :
                                          analysis.timeframe === 'weekly' ? 'week' : 'month',
                                    displayFormats: {
                                        hour: 'HH:mm',
                                        day: 'MMM D',
                                        week: 'MMM D',
                                        month: 'MMM YYYY'
                                    }
                                }
                            }],
                            yAxes: [{
                                ticks: {
                                    beginAtZero: false
                                }
                            }]
                        }
                    }
                });
            }
            
            // Update or create probability chart
            const probCtx = document.getElementById('probabilityChart').getContext('2d');
            if (probabilityChart) {
                probabilityChart.data.datasets[0].data = probData.map(item => ({
                    x: item.x,
                    y: item.bullish
                }));
                probabilityChart.data.datasets[1].data = probData.map(item => ({
                    x: item.x,
                    y: item.bearish
                }));
                probabilityChart.options.title.text = `${analysis.symbol} Bullish/Bearish Probability - ${analysis.timeframe}`;
                probabilityChart.update();
            } else {
                probabilityChart = new Chart(probCtx, {
                    type: 'line',
                    data: {
                        datasets: [
                            {
                                label: 'Bullish %',
                                data: probData.map(item => ({
                                    x: item.x,
                                    y: item.bullish
                                })),
                                borderColor: 'rgb(75, 192, 192)',
                                backgroundColor: 'rgba(75, 192, 192, 0.1)',
                                borderWidth: 2,
                                fill: true
                            },
                            {
                                label: 'Bearish %',
                                data: probData.map(item => ({
                                    x: item.x,
                                    y: item.bearish
                                })),
                                borderColor: 'rgb(255, 99, 132)',
                                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                                borderWidth: 2,
                                fill: true
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        title: {
                            display: true,
                            text: `${analysis.symbol} Bullish/Bearish Probability - ${analysis.timeframe}`
                        },
                        scales: {
                            xAxes: [{
                                type: 'time',
                                time: {
                                    unit: analysis.timeframe === 'intraday' ? 'hour' : 
                                          analysis.timeframe === 'daily' ? 'day' :
                                          analysis.timeframe === 'weekly' ? 'week' : 'month',
                                    displayFormats: {
                                        hour: 'HH:mm',
                                        day: 'MMM D',
                                        week: 'MMM D',
                                        month: 'MMM YYYY'
                                    }
                                }
                            }],
                            yAxes: [{
                                ticks: {
                                    beginAtZero: false,
                                    max: 100,
                                    min: 0
                                }
                            }]
                        }
                    }
                });
            }
        }
        
        function updateRecommendation(recommendation) {
            recommendationDiv.innerHTML = `
                <div>Recommendation: <strong>${recommendation.recommendation}</strong></div>
                <div>Confidence: ${recommendation.confidence}</div>
                <div>Bullish Probability: ${recommendation.bullish_prob}</div>
                <div>Bearish Probability: ${recommendation.bearish_prob}</div>
            `;
            
            // Update styling based on recommendation
            recommendationDiv.className = 'recommendation';
            if (recommendation.recommendation.includes('Buy')) {
                recommendationDiv.classList.add('bullish');
            } else if (recommendation.recommendation.includes('Sell')) {
                recommendationDiv.classList.add('bearish');
            } else {
                recommendationDiv.classList.add('neutral');
            }
        }
        
        function updateTransitsTable(probabilities) {
            // Get all transits from all probability entries
            const allTransits = [];
            probabilities.forEach(day => {
                day.transits.forEach(transit => {
                    allTransits.push({
                        date: day.date,
                        ...transit
                    });
                });
            });
            
            // Sort by date (newest first)
            allTransits.sort((a, b) => new Date(b.date) - new Date(a.date));
            
            // Update table
            transitsBody.innerHTML = '';
            
            allTransits.forEach(transit => {
                const row = document.createElement('tr');
                
                // Determine influence
                let influence = 'Neutral';
                let influenceClass = '';
                
                if (['Jupiter', 'Venus', 'Sun'].includes(transit.planet)) {
                    influence = transit.aspect === 'square' || transit.aspect === 'opposition' ? 
                               'Mildly Bearish' : 'Bullish';
                    influenceClass = influence.includes('Bullish') ? 'bullish-cell' : '';
                } else if (['Saturn', 'Mars', 'Pluto'].includes(transit.planet)) {
                    influence = transit.aspect === 'square' || transit.aspect === 'opposition' ? 
                               'Bearish' : 'Mildly Bullish';
                    influenceClass = influence.includes('Bearish') ? 'bearish-cell' : '';
                }
                
                row.innerHTML = `
                    <td>${new Date(transit.date).toLocaleDateString()}</td>
                    <td>${transit.planet}</td>
                    <td>${transit.zodiac_sign}</td>
                    <td>${transit.aspect}</td>
                    <td>${transit.orb}°</td>
                    <td>${transit.retrograde ? 'Yes' : 'No'}</td>
                    <td class="${influenceClass}">${influence}</td>
                `;
                
                transitsBody.appendChild(row);
            });
        }
    </script>
</body>
</html>
