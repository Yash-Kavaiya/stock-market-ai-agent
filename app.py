from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd
import json
import markdown
import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get_stock_price', methods=['POST'])
def get_stock_price():
    data = request.json
    ticker = data.get('ticker', '')
    
    try:
        # Get stock data using yfinance
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")
        
        # Get current price data
        current_data = stock.info
        current_price = current_data.get('currentPrice', current_data.get('regularMarketPrice', 'N/A'))
        
        # Format the data for display
        price_history = hist[['Open', 'High', 'Low', 'Close', 'Volume']].reset_index()
        price_history['Date'] = price_history['Date'].dt.strftime('%Y-%m-%d')
        
        # Create markdown response
        response_markdown = f"""
# Stock Price Analysis for {ticker.upper()}

## Current Price: ${current_price}

### Price Trend (Last Month)

| Date | Open | High | Low | Close | Volume |
|------|------|------|-----|-------|--------|
"""
        
        # Add last 10 days of data to the table
        for _, row in price_history.tail(10).iterrows():
            response_markdown += f"| {row['Date']} | ${row['Open']:.2f} | ${row['High']:.2f} | ${row['Low']:.2f} | ${row['Close']:.2f} | {row['Volume']:,} |\n"
        
        # Calculate some basic statistics
        avg_price = hist['Close'].mean()
        max_price = hist['High'].max()
        min_price = hist['Low'].min()
        
        response_markdown += f"""
### Summary Statistics
- Average Close Price: ${avg_price:.2f}
- Highest Price: ${max_price:.2f}
- Lowest Price: ${min_price:.2f}
- Price Change: {((current_price - hist['Close'].iloc[0]) / hist['Close'].iloc[0] * 100):.2f}%
"""
        
        return jsonify({
            'content': response_markdown,
            'markdown': response_markdown
        })
    except Exception as e:
        error_message = f"Error retrieving stock data for {ticker}: {str(e)}"
        return jsonify({
            'content': error_message,
            'markdown': f"## Error\n{error_message}"
        })

@app.route('/api/get_analyst_recommendations', methods=['POST'])
def get_analyst_recommendations():
    data = request.json
    ticker = data.get('ticker', '')
    
    try:
        # Get stock data using yfinance
        stock = yf.Ticker(ticker)
        
        # Create a robust response that doesn't depend on recommendations data
        response_markdown = f"""
# Analyst Recommendations for {ticker.upper()}

## Summary Rating
"""
        
        # Try to get the company name
        try:
            company_name = stock.info.get('shortName', ticker.upper())
        except:
            company_name = ticker.upper()
            
        # Try to get analyst data - if this fails, use placeholder data
        try:
            # Try to get recommendations
            recommendations = stock.recommendations
            
            if recommendations is not None and not recommendations.empty:
                # Handle the case where recommendations exist and have data
                
                # Check if 'Date' column exists in index
                if hasattr(recommendations.index, 'name') and recommendations.index.name == 'Date':
                    recommendations = recommendations.reset_index()
                    if 'Date' in recommendations.columns and hasattr(recommendations['Date'], 'dt'):
                        recommendations['Date'] = recommendations['Date'].dt.strftime('%Y-%m-%d')
                
                # Check column existence before accessing
                has_to_grade = 'toGrade' in recommendations.columns or 'To Grade' in recommendations.columns
                has_from_grade = 'fromGrade' in recommendations.columns or 'From Grade' in recommendations.columns
                has_action = 'Action' in recommendations.columns
                has_firm = 'Firm' in recommendations.columns
                
                # Determine which column names to use
                to_grade_col = 'toGrade' if 'toGrade' in recommendations.columns else 'To Grade'
                from_grade_col = 'fromGrade' if 'fromGrade' in recommendations.columns else 'From Grade'
                
                if has_to_grade and has_firm:  # If we have the key columns
                    response_markdown += f"""
## Recent Recommendations

| Date | Firm | To Grade | From Grade | Action |
|------|------|----------|------------|--------|
"""
                    
                    # Add recommendations to the table (last 10)
                    for _, row in recommendations.tail(10).iterrows():
                        date_val = row.get('Date', 'N/A') if 'Date' in row else 'N/A'
                        firm_val = row.get('Firm', 'N/A') if 'Firm' in row else 'N/A'
                        to_grade_val = row.get(to_grade_col, 'N/A') if to_grade_col in row else 'N/A'
                        from_grade_val = row.get(from_grade_col, 'N/A') if from_grade_col in row else 'N/A'
                        action_val = row.get('Action', 'N/A') if 'Action' in row else 'N/A'
                        
                        response_markdown += f"| {date_val} | {firm_val} | {to_grade_val} | {from_grade_val} | {action_val} |\n"
                    
                    # Calculate recommendation distribution if possible
                    if has_to_grade:
                        grades = recommendations[to_grade_col].value_counts()
                        
                        response_markdown += f"""
## Recommendation Distribution

| Grade | Count | Percentage |
|-------|-------|------------|
"""
                        
                        for grade, count in grades.items():
                            percentage = (count / len(recommendations)) * 100
                            response_markdown += f"| {grade} | {count} | {percentage:.1f}% |\n"
                
                else:
                    # If we don't have the right columns, show what we do have
                    response_markdown += f"""
The recommendations data structure doesn't contain the expected columns.
Available columns: {', '.join(recommendations.columns)}
                    """
            else:
                # If no recommendations data, use a placeholder
                response_markdown += f"""
No specific analyst recommendations are available for {company_name} through our data provider.

### General Market Sentiment
Based on general market indicators, {company_name} would typically be evaluated on:

- **Financial Performance**: Recent earnings and revenue growth
- **Market Position**: Competitive advantages in their industry
- **Future Outlook**: Growth projections and upcoming product/service initiatives
- **Valuation Metrics**: Price-to-earnings ratio, price-to-sales, etc.

For detailed analyst recommendations, consider checking financial news websites or specialized investment platforms.
"""
        except Exception as e:
            # Use placeholder data if we couldn't get recommendations
            response_markdown += f"""
## Analyst Overview for {company_name}

*Note: Specific analyst data couldn't be retrieved. Below is general information about how analysts typically rate stocks.*

### Common Analyst Ratings
1. **Strong Buy**: Significant outperformance expected
2. **Buy**: Moderate outperformance expected
3. **Hold**: Performance in line with the market
4. **Underperform**: Expected to perform worse than the market
5. **Sell**: Significant underperformance expected

For actual analyst ratings for {ticker}, please check financial news websites or investment platforms.

*Technical note: {str(e)}*
"""
        
        return jsonify({
            'content': response_markdown,
            'markdown': response_markdown
        })
    except Exception as e:
        error_message = f"Error retrieving analyst recommendations for {ticker}: {str(e)}"
        return jsonify({
            'content': error_message,
            'markdown': f"## Error\n{error_message}"
        })

@app.route('/api/get_company_info', methods=['POST'])
def get_company_info():
    data = request.json
    ticker = data.get('ticker', '')
    
    try:
        # Get stock data using yfinance
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Create markdown response
        response_markdown = f"""
# Company Information: {info.get('shortName', ticker.upper())}

## Business Overview
{info.get('longBusinessSummary', 'No business summary available.')}

## Key Information

| Metric | Value |
|--------|-------|
| Sector | {info.get('sector', 'N/A')} |
| Industry | {info.get('industry', 'N/A')} |
| Full Time Employees | {info.get('fullTimeEmployees', 'N/A'):,} |
| Country | {info.get('country', 'N/A')} |
| Website | {info.get('website', 'N/A')} |
| Market Cap | ${info.get('marketCap', 0)/1000000000:.2f} billion |
"""
        
        # Add financial metrics if available
        response_markdown += f"""
## Financial Metrics

| Metric | Value |
|--------|-------|
| P/E Ratio | {info.get('trailingPE', 'N/A')} |
| Forward P/E | {info.get('forwardPE', 'N/A')} |
| Price-to-Sales | {info.get('priceToSalesTrailing12Months', 'N/A')} |
| Price-to-Book | {info.get('priceToBook', 'N/A')} |
| Profit Margins | {info.get('profitMargins', 0) * 100:.2f}% |
| Dividend Yield | {info.get('dividendYield', 0) * 100:.2f}% |
| 52-Week Change | {info.get('52WeekChange', 0) * 100:.2f}% |
| Beta | {info.get('beta', 'N/A')} |
"""
        
        return jsonify({
            'content': response_markdown,
            'markdown': response_markdown
        })
    except Exception as e:
        error_message = f"Error retrieving company information for {ticker}: {str(e)}"
        return jsonify({
            'content': error_message,
            'markdown': f"## Error\n{error_message}"
        })

@app.route('/api/get_company_news', methods=['POST'])
def get_company_news():
    data = request.json
    ticker = data.get('ticker', '')
    
    try:
        # Since YFinance doesn't have a direct news API, we'll create a placeholder
        # In a real app, you would integrate with a news API or use web scraping
        
        # Create markdown response with sample news
        company_name = yf.Ticker(ticker).info.get('shortName', ticker.upper())
        
        response_markdown = f"""
# Latest News for {company_name}

*Note: This is sample news data. In a production environment, you would integrate with a financial news API.*

## Recent News Articles

1. **{company_name} Reports Quarterly Earnings**  
   *Source: Financial Times - {(datetime.datetime.now() - datetime.timedelta(days=2)).strftime('%Y-%m-%d')}*  
   {company_name} reported quarterly earnings that exceeded analyst expectations, with revenue growing by 15% year-over-year.

2. **Industry Analysis: Impact of Market Trends on {company_name}**  
   *Source: Bloomberg - {(datetime.datetime.now() - datetime.timedelta(days=5)).strftime('%Y-%m-%d')}*  
   Analysts discuss how current market trends are affecting {company_name}'s growth strategy and competitive position.

3. **{company_name} Announces New Product Line**  
   *Source: Reuters - {(datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')}*  
   {company_name} has unveiled its latest product line, aimed at expanding its market share in key demographics.

4. **Regulatory Changes and Their Impact on {company_name}**  
   *Source: Wall Street Journal - {(datetime.datetime.now() - datetime.timedelta(days=10)).strftime('%Y-%m-%d')}*  
   Recent regulatory changes could significantly impact {company_name}'s operations in several key markets.

5. **{company_name} Executive Interview: Future Outlook**  
   *Source: CNBC - {(datetime.datetime.now() - datetime.timedelta(days=12)).strftime('%Y-%m-%d')}*  
   In an exclusive interview, executives from {company_name} discuss their vision for the company's future and upcoming initiatives.
"""
        
        return jsonify({
            'content': response_markdown,
            'markdown': response_markdown
        })
    except Exception as e:
        error_message = f"Error retrieving company news for {ticker}: {str(e)}"
        return jsonify({
            'content': error_message,
            'markdown': f"## Error\n{error_message}"
        })

@app.route('/api/run_custom_analysis', methods=['POST'])
def run_custom_analysis():
    data = request.json
    prompt = data.get('prompt', '')
    
    # Extract any ticker symbols from the prompt (simple regex approach)
    import re
    tickers = re.findall(r'\b[A-Z]{1,5}\b', prompt)
    
    try:
        response_markdown = f"""
# Custom Financial Analysis

## Query
*{prompt}*

"""
        
        # If we found ticker symbols, provide basic analysis
        if tickers:
            response_markdown += f"## Analysis for {', '.join(tickers)}\n\n"
            
            valid_tickers = []
            ticker_data = {}
            
            # First, validate all tickers and collect data safely
            for ticker in tickers[:3]:  # Limit to first 3 tickers
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    
                    # Skip tickers with no data
                    if not info or len(info) == 0:
                        response_markdown += f"### {ticker}: No data available\n\n"
                        continue
                        
                    hist = stock.history(period="6mo")
                    
                    # Skip tickers with no history
                    if hist.empty:
                        response_markdown += f"### {ticker}: No historical data available\n\n"
                        continue
                    
                    # Store the data for this ticker
                    ticker_data[ticker] = {
                        'info': info,
                        'hist': hist
                    }
                    valid_tickers.append(ticker)
                    
                except Exception as e:
                    response_markdown += f"### {ticker}: Error retrieving data - {str(e)}\n\n"
            
            # Now process the valid tickers
            for ticker in valid_tickers:
                info = ticker_data[ticker]['info']
                hist = ticker_data[ticker]['hist']
                
                # Safely get values with fallbacks
                try:
                    current_price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
                except:
                    current_price = 'N/A'
                    
                try:
                    company_name = info.get('shortName', ticker)
                except:
                    company_name = ticker
                
                try:
                    if not hist.empty and 'Close' in hist.columns and len(hist['Close']) > 0:
                        first_close = hist['Close'].iloc[0]
                        last_close = hist['Close'].iloc[-1]
                        if first_close > 0:  # Avoid division by zero
                            price_change = ((last_close - first_close) / first_close) * 100
                        else:
                            price_change = 0
                    else:
                        price_change = 'N/A'
                except:
                    price_change = 'N/A'
                
                try:
                    market_cap = info.get('marketCap', 0)/1000000000
                    market_cap_str = f"${market_cap:.2f} billion"
                except:
                    market_cap_str = 'N/A'
                
                try:
                    pe_ratio = info.get('trailingPE', 'N/A')
                except:
                    pe_ratio = 'N/A'
                
                try:
                    industry = info.get('industry', 'N/A')
                except:
                    industry = 'N/A'
                
                # Build response with safe values
                response_markdown += f"""
### {company_name} ({ticker})
- Current Price: {current_price if current_price == 'N/A' else f'${current_price}'}
- 6-Month Price Change: {price_change if price_change == 'N/A' else f'{price_change:.2f}%'}
- Market Cap: {market_cap_str}
- P/E Ratio: {pe_ratio}
- Industry: {industry}

"""
            
            # Only do comparative analysis if we have multiple valid tickers
            if len(valid_tickers) > 1:
                response_markdown += "## Comparative Analysis\n\n"
                response_markdown += "| Metric | " + " | ".join(valid_tickers) + " |\n"
                response_markdown += "|--------|" + "-|".join(["-" * len(ticker) for ticker in valid_tickers]) + "-|\n"
                
                # Compare current price safely
                response_markdown += "| Current Price | "
                for ticker in valid_tickers:
                    info = ticker_data[ticker]['info']
                    try:
                        current_price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
                        response_markdown += f"${current_price} | "
                    except:
                        response_markdown += "N/A | "
                response_markdown += "\n"
                
                # Compare market cap safely
                response_markdown += "| Market Cap | "
                for ticker in valid_tickers:
                    info = ticker_data[ticker]['info']
                    try:
                        market_cap = info.get('marketCap', 0)/1000000000
                        response_markdown += f"${market_cap:.2f}B | "
                    except:
                        response_markdown += "N/A | "
                response_markdown += "\n"
                
                # Compare P/E ratio safely
                response_markdown += "| P/E Ratio | "
                for ticker in valid_tickers:
                    info = ticker_data[ticker]['info']
                    try:
                        pe_ratio = info.get('trailingPE', 'N/A')
                        response_markdown += f"{pe_ratio} | "
                    except:
                        response_markdown += "N/A | "
                response_markdown += "\n"
        else:
            response_markdown += """
## General Market Analysis

Without specific ticker symbols, here's a general market overview:

### S&P 500 Performance
"""
            try:
                # Get S&P 500 data safely
                spy = yf.Ticker("SPY")
                spy_hist = spy.history(period="1mo")
                
                if not spy_hist.empty and 'Close' in spy_hist.columns and len(spy_hist['Close']) > 0:
                    current_level = spy_hist['Close'].iloc[-1]
                    first_close = spy_hist['Close'].iloc[0]
                    if first_close > 0:  # Avoid division by zero
                        spy_change = ((current_level - first_close) / first_close) * 100
                    else:
                        spy_change = 0
                        
                    response_markdown += f"""
- Current Level: ${current_level:.2f}
- 1-Month Change: {spy_change:.2f}%
"""
                else:
                    response_markdown += "Unable to retrieve current S&P 500 data.\n"
            except Exception as e:
                response_markdown += f"Error retrieving S&P 500 data: {str(e)}\n"
            
            response_markdown += """
### Popular Stock Tickers to Try
Here are some popular stock tickers you can analyze:

- Technology: AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA
- Financial: JPM, BAC, GS, V, MA, AXP
- Healthcare: JNJ, PFE, MRK, UNH, ABBV
- Consumer: KO, PEP, MCD, SBUX, NKE, WMT, TGT
- Industrial: GE, CAT, BA, HON, MMM

### Recommendation
For detailed analysis, try specifying ticker symbols in your query (e.g., "Compare AAPL and MSFT").
"""
        
        return jsonify({
            'content': response_markdown,
            'markdown': response_markdown
        })
    except Exception as e:
        error_message = f"Error performing custom analysis: {str(e)}"
        return jsonify({
            'content': error_message,
            'markdown': f"## Error\n{error_message}"
        })

@app.route('/api/get_stock_list', methods=['GET'])
def get_stock_list():
    """Provide a list of popular stocks categorized by sector"""
    
    stock_list = {
        "Technology": [
            {"ticker": "AAPL", "name": "Apple Inc."},
            {"ticker": "MSFT", "name": "Microsoft Corporation"},
            {"ticker": "GOOGL", "name": "Alphabet Inc. (Google)"},
            {"ticker": "AMZN", "name": "Amazon.com Inc."},
            {"ticker": "META", "name": "Meta Platforms Inc. (Facebook)"},
            {"ticker": "NVDA", "name": "NVIDIA Corporation"},
            {"ticker": "TSLA", "name": "Tesla, Inc."},
            {"ticker": "INTC", "name": "Intel Corporation"},
            {"ticker": "CRM", "name": "Salesforce, Inc."},
            {"ticker": "ADBE", "name": "Adobe Inc."},
            {"ticker": "ORCL", "name": "Oracle Corporation"},
            {"ticker": "CSCO", "name": "Cisco Systems, Inc."}
        ],
        "Financial": [
            {"ticker": "JPM", "name": "JPMorgan Chase & Co."},
            {"ticker": "BAC", "name": "Bank of America Corporation"},
            {"ticker": "WFC", "name": "Wells Fargo & Company"},
            {"ticker": "C", "name": "Citigroup Inc."},
            {"ticker": "GS", "name": "The Goldman Sachs Group, Inc."},
            {"ticker": "V", "name": "Visa Inc."},
            {"ticker": "MA", "name": "Mastercard Incorporated"},
            {"ticker": "AXP", "name": "American Express Company"},
            {"ticker": "BLK", "name": "BlackRock, Inc."},
            {"ticker": "MS", "name": "Morgan Stanley"}
        ],
        "Healthcare": [
            {"ticker": "JNJ", "name": "Johnson & Johnson"},
            {"ticker": "PFE", "name": "Pfizer Inc."},
            {"ticker": "MRK", "name": "Merck & Co., Inc."},
            {"ticker": "UNH", "name": "UnitedHealth Group Incorporated"},
            {"ticker": "ABBV", "name": "AbbVie Inc."},
            {"ticker": "LLY", "name": "Eli Lilly and Company"},
            {"ticker": "TMO", "name": "Thermo Fisher Scientific Inc."},
            {"ticker": "DHR", "name": "Danaher Corporation"},
            {"ticker": "ABT", "name": "Abbott Laboratories"},
            {"ticker": "BMY", "name": "Bristol-Myers Squibb Company"}
        ],
        "Consumer": [
            {"ticker": "KO", "name": "The Coca-Cola Company"},
            {"ticker": "PEP", "name": "PepsiCo, Inc."},
            {"ticker": "WMT", "name": "Walmart Inc."},
            {"ticker": "TGT", "name": "Target Corporation"},
            {"ticker": "MCD", "name": "McDonald's Corporation"},
            {"ticker": "SBUX", "name": "Starbucks Corporation"},
            {"ticker": "HD", "name": "The Home Depot, Inc."},
            {"ticker": "NKE", "name": "NIKE, Inc."},
            {"ticker": "PG", "name": "The Procter & Gamble Company"},
            {"ticker": "COST", "name": "Costco Wholesale Corporation"}
        ],
        "Industrial": [
            {"ticker": "GE", "name": "General Electric Company"},
            {"ticker": "CAT", "name": "Caterpillar Inc."},
            {"ticker": "BA", "name": "The Boeing Company"},
            {"ticker": "MMM", "name": "3M Company"},
            {"ticker": "HON", "name": "Honeywell International Inc."},
            {"ticker": "UPS", "name": "United Parcel Service, Inc."},
            {"ticker": "LMT", "name": "Lockheed Martin Corporation"},
            {"ticker": "RTX", "name": "Raytheon Technologies Corporation"},
            {"ticker": "DE", "name": "Deere & Company"},
            {"ticker": "FDX", "name": "FedEx Corporation"}
        ],
        "Energy": [
            {"ticker": "XOM", "name": "Exxon Mobil Corporation"},
            {"ticker": "CVX", "name": "Chevron Corporation"},
            {"ticker": "COP", "name": "ConocoPhillips"},
            {"ticker": "SLB", "name": "Schlumberger Limited"},
            {"ticker": "EOG", "name": "EOG Resources, Inc."},
            {"ticker": "OXY", "name": "Occidental Petroleum Corporation"},
            {"ticker": "BP", "name": "BP p.l.c."},
            {"ticker": "TTE", "name": "TotalEnergies SE"},
            {"ticker": "VLO", "name": "Valero Energy Corporation"},
            {"ticker": "PSX", "name": "Phillips 66"}
        ],
        "Utilities & Telecom": [
            {"ticker": "NEE", "name": "NextEra Energy, Inc."},
            {"ticker": "DUK", "name": "Duke Energy Corporation"},
            {"ticker": "SO", "name": "The Southern Company"},
            {"ticker": "T", "name": "AT&T Inc."},
            {"ticker": "VZ", "name": "Verizon Communications Inc."},
            {"ticker": "TMUS", "name": "T-Mobile US, Inc."},
            {"ticker": "D", "name": "Dominion Energy, Inc."},
            {"ticker": "EXC", "name": "Exelon Corporation"},
            {"ticker": "PCG", "name": "PG&E Corporation"},
            {"ticker": "SRE", "name": "Sempra"}
        ],
        "ETFs": [
            {"ticker": "SPY", "name": "SPDR S&P 500 ETF Trust"},
            {"ticker": "QQQ", "name": "Invesco QQQ Trust (NASDAQ-100 Index)"},
            {"ticker": "DIA", "name": "SPDR Dow Jones Industrial Average ETF"},
            {"ticker": "IWM", "name": "iShares Russell 2000 ETF"},
            {"ticker": "VTI", "name": "Vanguard Total Stock Market ETF"},
            {"ticker": "XLF", "name": "Financial Select Sector SPDR Fund"},
            {"ticker": "XLK", "name": "Technology Select Sector SPDR Fund"},
            {"ticker": "XLV", "name": "Health Care Select Sector SPDR Fund"},
            {"ticker": "XLE", "name": "Energy Select Sector SPDR Fund"},
            {"ticker": "XLY", "name": "Consumer Discretionary Select Sector SPDR Fund"}
        ]
    }
    
    return jsonify(stock_list)

# Let's also update the main HTML template to include a dropdown with all these stocks
@app.route('/stocks')
def stock_list_page():
    return render_template('stock_list.html')

@app.route('/api/get_price_trends', methods=['POST'])
def get_price_trends():
    data = request.json
    ticker = data.get('ticker', '')
    
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="6mo")
        
        # Prepare data for chart
        dates = hist.index.strftime('%Y-%m-%d').tolist()
        prices = hist['Close'].tolist()
        
        config = {
            'type': 'line',
            'data': {
                'labels': dates,
                'datasets': [{
                    'label': f'{ticker} Price',
                    'data': prices,
                    'borderColor': '#0066B3',
                    'backgroundColor': 'rgba(0, 102, 179, 0.1)',
                    'fill': True,
                    'tension': 0.4
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'interaction': {
                    'intersect': False,
                    'mode': 'index'
                },
                'plugins': {
                    'title': {
                        'display': True,
                        'text': f'Price Trend - {ticker}'
                    },
                    'legend': {
                        'position': 'top'
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': False,
                        'grid': {
                            'drawBorder': False
                        }
                    },
                    'x': {
                        'grid': {
                            'display': False
                        }
                    }
                }
            }
        }
        
        return jsonify({'config': config})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_volume_analysis', methods=['POST'])
def get_volume_analysis():
    data = request.json
    ticker = data.get('ticker', '')
    
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="6mo")
        
        # Prepare data for chart
        dates = hist.index.strftime('%Y-%m-%d').tolist()
        volumes = hist['Volume'].tolist()
        
        config = {
            'type': 'bar',
            'data': {
                'labels': dates,
                'datasets': [{
                    'label': f'{ticker} Volume',
                    'data': volumes,
                    'backgroundColor': 'rgba(90, 45, 129, 0.5)',
                    'borderColor': '#5A2D81',
                    'borderWidth': 1,
                    'borderRadius': 4
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'interaction': {
                    'intersect': False,
                    'mode': 'index'
                },
                'plugins': {
                    'title': {
                        'display': True,
                        'text': f'Trading Volume - {ticker}'
                    },
                    'legend': {
                        'position': 'top'
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'grid': {
                            'drawBorder': False
                        }
                    },
                    'x': {
                        'grid': {
                            'display': False
                        }
                    }
                }
            }
        }
        
        return jsonify({'config': config})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_technical_indicators', methods=['POST'])
def get_technical_indicators():
    data = request.json
    ticker = data.get('ticker', '')
    
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="6mo")
        
        # Calculate simple moving averages
        hist['SMA20'] = hist['Close'].rolling(window=20).mean()
        hist['SMA50'] = hist['Close'].rolling(window=50).mean()
        
        # Prepare data for chart - replace NaN with None for JSON serialization
        dates = hist.index.strftime('%Y-%m-%d').tolist()
        prices = [float(x) if pd.notnull(x) else None for x in hist['Close']]
        sma20 = [float(x) if pd.notnull(x) else None for x in hist['SMA20']]
        sma50 = [float(x) if pd.notnull(x) else None for x in hist['SMA50']]
        
        config = {
            'type': 'line',
            'data': {
                'labels': dates,
                'datasets': [
                    {
                        'label': f'{ticker} Price',
                        'data': prices,
                        'borderColor': '#0D1F52',
                        'backgroundColor': 'rgba(13, 31, 82, 0.1)',
                        'fill': False,
                        'tension': 0.4,
                        'borderWidth': 2,
                        'pointRadius': 0,
                        'spanGaps': True
                    },
                    {
                        'label': '20-day SMA',
                        'data': sma20,
                        'borderColor': '#E31B72',
                        'backgroundColor': 'transparent',
                        'borderDash': [5, 5],
                        'borderWidth': 2,
                        'pointRadius': 0,
                        'fill': False,
                        'spanGaps': True
                    },
                    {
                        'label': '50-day SMA',
                        'data': sma50,
                        'borderColor': '#5A2D81',
                        'backgroundColor': 'transparent',
                        'borderDash': [10, 5],
                        'borderWidth': 2,
                        'pointRadius': 0,
                        'fill': False,
                        'spanGaps': True
                    }
                ]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'interaction': {
                    'intersect': False,
                    'mode': 'index'
                },
                'plugins': {
                    'title': {
                        'display': True,
                        'text': f'Technical Analysis - {ticker}'
                    },
                    'legend': {
                        'position': 'top',
                        'labels': {
                            'usePointStyle': True,
                            'padding': 15
                        }
                    },
                    'tooltip': {
                        'mode': 'index',
                        'intersect': False
                    }
                },
                'scales': {
                    'y': {
                        'beginAtZero': False,
                        'grid': {
                            'drawBorder': False,
                            'color': 'rgba(0, 0, 0, 0.05)'
                        },
                        'ticks': {
                            'padding': 10
                        }
                    },
                    'x': {
                        'grid': {
                            'display': False
                        },
                        'ticks': {
                            'maxTicksLimit': 10,
                            'maxRotation': 0
                        }
                    }
                }
            }
        }
        
        return jsonify({'config': config})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)