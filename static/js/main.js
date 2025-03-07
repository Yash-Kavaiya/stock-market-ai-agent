// Main JavaScript for Finance Agent Dashboard

document.addEventListener('DOMContentLoaded', function() {
    // First load the stock list for dropdown menus
    loadStockDropdowns().then(() => {
        // After dropdowns are populated, set up the rest of the functionality
        
        // Form submission handlers
        setupFormHandler('stock-price-form', 'stock-price-ticker', 'stock-price-loader', 'stock-price-result', '/api/get_stock_price');
        setupFormHandler('analyst-recommendations-form', 'analyst-recommendations-ticker', 'analyst-recommendations-loader', 'analyst-recommendations-result', '/api/get_analyst_recommendations');
        setupFormHandler('company-info-form', 'company-info-ticker', 'company-info-loader', 'company-info-result', '/api/get_company_info');
        setupFormHandler('company-news-form', 'company-news-ticker', 'company-news-loader', 'company-news-result', '/api/get_company_news');
        setupCustomAnalysisHandler();
        setupQuickAnalysis();
        setupPopularTickers();
        
        // Setup chart handlers
        setupChartHandlers();
        
        // Setup dropdown synchronization
        setupDropdownSync();
        
        // Setup navigation highlight
        setupNavHighlight();
        
        // Check URL parameters for ticker
        checkUrlParameters();
    });
});

// Sets up the form handler for each analysis type
function setupFormHandler(formId, tickerId, loaderId, resultId, endpoint) {
    const form = document.getElementById(formId);
    const dropdown = document.getElementById(tickerId);
    const loader = document.getElementById(loaderId);
    const resultContainer = document.getElementById(resultId);
    
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const ticker = dropdown.value;
        if (!ticker) {
            alert('Please select a stock from the dropdown');
            return;
        }
        
        // Show loader and clear previous results
        loader.style.display = 'block';
        resultContainer.innerHTML = '';
        
        // Get the stock name for display purposes
        let stockName = ticker;
        if (window.allStocksList) {
            const stockInfo = window.allStocksList.find(stock => stock.ticker === ticker);
            if (stockInfo) {
                stockName = `${ticker} - ${stockInfo.name}`;
            }
        }
        
        // Show loading message with stock name
        resultContainer.innerHTML = `<div class="alert alert-info">Loading data for ${stockName}...</div>`;
        
        // Send API request
        fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ ticker: ticker })
        })
        .then(response => response.json())
        .then(data => {
            // Hide loader
            loader.style.display = 'none';
            
            // Display the result using markdown renderer
            resultContainer.innerHTML = marked.parse(data.markdown);
            
            // Apply Bootstrap styling to tables
            const tables = resultContainer.querySelectorAll('table');
            tables.forEach(table => {
                table.classList.add('table', 'table-striped', 'table-bordered');
            });
        })
        .catch(error => {
            loader.style.display = 'none';
            resultContainer.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
        });
    });
}

// Sets up the custom analysis form handler
function setupCustomAnalysisHandler() {
    const form = document.getElementById('custom-analysis-form');
    const promptInput = document.getElementById('custom-prompt');
    const loader = document.getElementById('custom-analysis-loader');
    const resultContainer = document.getElementById('custom-analysis-result');
    
    // Add example query handlers
    const exampleQueries = document.querySelectorAll('.example-query');
    exampleQueries.forEach(button => {
        button.addEventListener('click', function() {
            promptInput.value = this.textContent.trim();
            promptInput.focus();
        });
    });
    
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const prompt = promptInput.value.trim();
        if (!prompt) {
            alert('Please enter a custom analysis request');
            return;
        }
        
        // Show loader and clear previous results
        loader.style.display = 'block';
        resultContainer.innerHTML = '';
        
        // Send API request
        fetch('/api/run_custom_analysis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt: prompt })
        })
        .then(response => response.json())
        .then(data => {
            // Hide loader
            loader.style.display = 'none';
            
            // Display the result using markdown renderer
            resultContainer.innerHTML = marked.parse(data.markdown);
            
            // Apply Bootstrap styling to tables
            const tables = resultContainer.querySelectorAll('table');
            tables.forEach(table => {
                table.classList.add('table', 'table-striped', 'table-bordered');
            });
        })
        .catch(error => {
            loader.style.display = 'none';
            resultContainer.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
        });
    });
}

// Sets up the quick analysis button
function setupQuickAnalysis() {
    const quickAnalysisBtn = document.getElementById('analyze-all-btn');
    const quickTickerInput = document.getElementById('quick-ticker');
    
    quickAnalysisBtn.addEventListener('click', function() {
        const ticker = quickTickerInput.value.trim();
        if (!ticker) {
            alert('Please enter a valid stock ticker');
            return;
        }
        
        // Set the ticker value for all forms and submit them one by one
        setAndSubmitForm('stock-price-ticker', 'stock-price-form', ticker);
        setAndSubmitForm('analyst-recommendations-ticker', 'analyst-recommendations-form', ticker);
        setAndSubmitForm('company-info-ticker', 'company-info-form', ticker);
        setAndSubmitForm('company-news-ticker', 'company-news-form', ticker);
        
        // Scroll to the first section
        document.getElementById('stock-price-section').scrollIntoView({ behavior: 'smooth' });
    });
}

// Sets the ticker value and submits the form
function setAndSubmitForm(tickerId, formId, ticker) {
    const tickerInput = document.getElementById(tickerId);
    const form = document.getElementById(formId);
    
    tickerInput.value = ticker;
    form.dispatchEvent(new Event('submit'));
}

// Sets up the popular ticker buttons
function setupPopularTickers() {
    const popularTickerBtns = document.querySelectorAll('.popular-ticker-btn');
    
    popularTickerBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const ticker = this.getAttribute('data-ticker');
            
            // Update all dropdown values
            const dropdowns = [
                document.getElementById('stock-price-ticker'),
                document.getElementById('analyst-recommendations-ticker'),
                document.getElementById('company-info-ticker'),
                document.getElementById('company-news-ticker'),
                document.getElementById('quick-ticker')
            ];
            
            dropdowns.forEach(dropdown => {
                if (dropdown) {
                    dropdown.value = ticker;
                }
            });
            
            // Trigger the analyze all button
            document.getElementById('analyze-all-btn').click();
        });
    });
}

// Sets up the navigation highlight based on scroll position
function setupNavHighlight() {
    const sections = document.querySelectorAll('section');
    const navLinks = document.querySelectorAll('.nav-link');
    
    window.addEventListener('scroll', function() {
        let current = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 100;
            const sectionHeight = section.clientHeight;
            
            if (window.pageYOffset >= sectionTop && window.pageYOffset < sectionTop + sectionHeight) {
                current = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    });
}

// Function to render markdown content
function renderMarkdown(markdown, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = marked.parse(markdown);
    
    // Apply Bootstrap styling to tables
    const tables = container.querySelectorAll('table');
    tables.forEach(table => {
        table.classList.add('table', 'table-striped', 'table-bordered');
    });
}

// Function to create and append a chart to a container
function createChart(container, type, data, options) {
    const canvas = document.createElement('canvas');
    container.appendChild(canvas);
    
    return new Chart(canvas, {
        type: type,
        data: data,
        options: options
    });
}

// Function to load all stock options into dropdown menus
async function loadStockDropdowns() {
    try {
        const response = await fetch('/api/get_stock_list');
        const stockList = await response.json();
        
        // Get all dropdown elements
        const dropdowns = [
            document.getElementById('stock-price-ticker'),
            document.getElementById('analyst-recommendations-ticker'),
            document.getElementById('company-info-ticker'),
            document.getElementById('company-news-ticker'),
            document.getElementById('quick-ticker'),
            document.getElementById('chart-ticker')
        ];
        
        // Process the stock list
        let allStocks = [];
        for (const sector in stockList) {
            // Create an optgroup for each sector
            const optgroup = document.createElement('optgroup');
            optgroup.label = sector;
            
            // Add stocks from this sector
            stockList[sector].forEach(stock => {
                const option = document.createElement('option');
                option.value = stock.ticker;
                option.textContent = `${stock.ticker} - ${stock.name}`;
                optgroup.appendChild(option);
                
                // Also add to flat list
                allStocks.push({
                    ticker: stock.ticker,
                    name: stock.name,
                    sector: sector
                });
            });
            
            // Add the optgroup to each dropdown
            dropdowns.forEach(dropdown => {
                if (dropdown) {
                    dropdown.appendChild(optgroup.cloneNode(true));
                }
            });
        }
        
        console.log(`Loaded ${allStocks.length} stocks into dropdown menus`);
        
        // Store the list for later use
        window.allStocksList = allStocks;
        
    } catch (error) {
        console.error('Error loading stock list:', error);
        alert('Failed to load stock list. Please refresh the page.');
    }
}

// Function to sync dropdown selections
function setupDropdownSync() {
    const dropdowns = [
        document.getElementById('stock-price-ticker'),
        document.getElementById('analyst-recommendations-ticker'),
        document.getElementById('company-info-ticker'),
        document.getElementById('company-news-ticker'),
        document.getElementById('quick-ticker'),
        document.getElementById('chart-ticker')
    ];
    
    // Add change event listener to each dropdown
    dropdowns.forEach(dropdown => {
        if (dropdown) {
            dropdown.addEventListener('change', function() {
                const selectedValue = this.value;
                if (selectedValue) {
                    // Update all other dropdowns
                    dropdowns.forEach(otherDropdown => {
                        if (otherDropdown && otherDropdown !== this) {
                            otherDropdown.value = selectedValue;
                        }
                    });
                }
            });
        }
    });
}

// Function to check URL parameters for ticker symbol
function checkUrlParameters() {
    const urlParams = new URLSearchParams(window.location.search);
    const ticker = urlParams.get('ticker');
    
    if (ticker) {
        console.log('Found ticker in URL:', ticker);
        
        // Set the ticker value in all forms
        document.getElementById('stock-price-ticker').value = ticker;
        document.getElementById('analyst-recommendations-ticker').value = ticker;
        document.getElementById('company-info-ticker').value = ticker;
        document.getElementById('company-news-ticker').value = ticker;
        document.getElementById('quick-ticker').value = ticker;
        document.getElementById('chart-ticker').value = ticker;
        
        // Trigger the analyze all button
        document.getElementById('analyze-all-btn').click();
    }
}

// Add new chart handling function
function setupChartHandlers() {
    const form = document.getElementById('chart-form');
    const ticker = document.getElementById('chart-ticker');
    
    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        if (!ticker.value) {
            alert('Please select a stock');
            return;
        }
        
        try {
            // Fetch and render all charts
            await Promise.all([
                renderPriceChart(ticker.value),
                renderVolumeChart(ticker.value),
                renderIndicatorsChart(ticker.value)
            ]);
        } catch (error) {
            console.error('Error generating charts:', error);
            alert('Failed to generate charts. Please try again.');
        }
    });
}

async function renderPriceChart(ticker) {
    try {
        const response = await fetch('/api/get_price_trends', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticker })
        });
        
        if (!response.ok) throw new Error('Network response was not ok');
        
        const data = await response.json();
        if (data.error) throw new Error(data.error);
        
        const canvas = document.getElementById('priceChart');
        const ctx = canvas.getContext('2d');
        
        // Clear existing chart
        if (window.priceChart instanceof Chart) {
            window.priceChart.destroy();
        }
        
        // Create new chart with data
        window.priceChart = new Chart(ctx, data.config);
        
    } catch (error) {
        console.error('Error rendering price chart:', error);
        alert('Failed to generate price chart: ' + error.message);
    }
}

async function renderVolumeChart(ticker) {
    try {
        const response = await fetch('/api/get_volume_analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticker })
        });
        
        if (!response.ok) throw new Error('Network response was not ok');
        
        const data = await response.json();
        if (data.error) throw new Error(data.error);
        
        const canvas = document.getElementById('volumeChart');
        const ctx = canvas.getContext('2d');
        
        // Clear existing chart
        if (window.volumeChart instanceof Chart) {
            window.volumeChart.destroy();
        }
        
        // Create new chart with data
        window.volumeChart = new Chart(ctx, data.config);
        
    } catch (error) {
        console.error('Error rendering volume chart:', error);
        alert('Failed to generate volume chart: ' + error.message);
    }
}

async function renderIndicatorsChart(ticker) {
    try {
        const response = await fetch('/api/get_technical_indicators', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticker })
        });
        
        if (!response.ok) throw new Error('Network response was not ok');
        
        const data = await response.json();
        if (data.error) throw new Error(data.error);
        
        const canvas = document.getElementById('indicatorsChart');
        const ctx = canvas.getContext('2d');
        
        // Clear existing chart
        if (window.indicatorsChart instanceof Chart) {
            window.indicatorsChart.destroy();
            delete window.indicatorsChart;
        }
        
        // Create new chart with data
        window.indicatorsChart = new Chart(ctx, data.config);
        
    } catch (error) {
        console.error('Error rendering indicators chart:', error);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger';
        errorDiv.textContent = 'Failed to generate technical indicators chart: ' + error.message;
        document.getElementById('indicatorsChart').parentNode.appendChild(errorDiv);
    }
}