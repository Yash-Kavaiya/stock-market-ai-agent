/**
 * Shopping Agent - Client-side JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Product search form validation and handling
    const searchForm = document.querySelector('form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            // Show loading spinner when form is submitted
            const loadingSpinner = document.querySelector('.loading-spinner');
            if (loadingSpinner) {
                loadingSpinner.classList.remove('d-none');
            }
            
            // Custom validation can be added here if needed
            const categorySelect = document.getElementById('category');
            const budgetSelect = document.getElementById('budget');
            
            if (categorySelect && categorySelect.value === '') {
                e.preventDefault();
                alert('Please select a product category');
                if (loadingSpinner) {
                    loadingSpinner.classList.add('d-none');
                }
                return false;
            }
            
            if (budgetSelect && budgetSelect.value === '') {
                e.preventDefault();
                alert('Please select a budget range');
                if (loadingSpinner) {
                    loadingSpinner.classList.add('d-none');
                }
                return false;
            }
            
            // Disable form submission button to prevent multiple submissions
            const submitButton = searchForm.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Searching...';
            }
            
            return true;
        });
    }
    
    // Handle dynamic content in the results page
    if (window.location.pathname.includes('/results')) {
        // Parse and format links in recommendations
        const recommendationsContent = document.querySelector('.markdown-content');
        if (recommendationsContent) {
            // Create clickable links from URLs in text
            const urlRegex = /(https?:\/\/[^\s]+)/g;
            recommendationsContent.innerHTML = recommendationsContent.innerHTML.replace(
                urlRegex, 
                function(url) {
                    return `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`;
                }
            );
            
            // Format product items with better styling
            formatProductItems();
            
            // Add event listener for new search button
            const newSearchBtn = document.querySelector('a[href="/"]');
            if (newSearchBtn) {
                newSearchBtn.addEventListener('click', function() {
                    // Clear any stored form data from session if needed
                    // This would require an AJAX call to a backend endpoint
                });
            }
        }
    }
    
    // Function to format product items in the recommendation output
    function formatProductItems() {
        const content = document.querySelector('.markdown-content');
        if (!content) return;
        
        let html = content.innerHTML;
        
        // Look for product patterns
        // Pattern 1: Product name followed by price
        const pricePattern = /([^\n<>]+)((?:\s*-\s*|\s*:\s*|\s+))(₹|Rs\.?|INR|\$)(\s*)([0-9,]+(\.[0-9]{2})?)/g;
        html = html.replace(pricePattern, function(match, name, separator, currency, space, price) {
            return `<div class="product-item">
                      <div class="product-title">${name.trim()}</div>
                      <div class="product-price">${currency}${price}</div>
                    </div>`;
        });
        
        // Pattern 2: Look for bullet points that might indicate features
        const bulletPattern = /<br>\s*[-•*]\s*([^<>]+)(?:<br>|$)/g;
        html = html.replace(bulletPattern, function(match, feature) {
            return `<div class="product-feature">${feature.trim()}</div>`;
        });
        
        // Apply the formatted HTML
        content.innerHTML = html;
        
        // Clean up duplicate <br> tags
        content.innerHTML = content.innerHTML.replace(/<br>\s*<br>\s*<br>/g, '<br><br>');
        
        // Convert any remaining feature-like text into feature pills
        const productItems = content.querySelectorAll('.product-item');
        productItems.forEach(item => {
            const text = item.innerHTML;
            
            // Look for feature-like patterns (lowercase words like "camera", "battery", etc.)
            const featureWords = [
                'camera', 'battery', 'display', 'screen', 'storage', 'memory', 'ram', 
                'processor', 'cpu', 'gpu', 'resolution', 'wireless', 'bluetooth', 
                'warranty', 'weight', 'lightweight', 'portable', 'fast', 'charging',
                'eco-friendly', 'popular', 'high-quality', 'discounted'
            ];
            
            let enhancedText = text;
            featureWords.forEach(word => {
                const regex = new RegExp(`(\\b${word}\\b[^.<>]*?)(?:<br>|<div|$)`, 'gi');
                enhancedText = enhancedText.replace(regex, function(match, feature) {
                    if (!feature.includes('product-feature')) {
                        return `<div class="product-feature">${feature.trim()}</div>`;
                    }
                    return match;
                });
            });
            
            item.innerHTML = enhancedText;
        });
    }
    
    // Dynamic behavior for preferences dropdown
    const categorySelect = document.getElementById('category');
    const preferencesSelect = document.getElementById('preferences');
    
    if (categorySelect && preferencesSelect) {
        categorySelect.addEventListener('change', function() {
            updatePreferencesOptions(this.value);
        });
        
        // Initialize preferences on page load
        if (categorySelect.value) {
            updatePreferencesOptions(categorySelect.value);
        }
    }
    
    // Function to update preferences options based on category
    function updatePreferencesOptions(category) {
        if (!preferencesSelect) return;
        
        // Store currently selected preferences
        const selectedPreferences = Array.from(preferencesSelect.selectedOptions).map(option => option.value);
        
        // Common preferences for all categories
        const commonPreferences = [
            {value: 'high_quality', text: 'High Quality'},
            {value: 'popular', text: 'Popular/Highly Rated'},
            {value: 'fast_delivery', text: 'Fast Delivery'},
            {value: 'discounted', text: 'On Discount/Sale'}
        ];
        
        // Category-specific preferences
        const categoryPreferences = {
            'electronics': [
                {value: 'energy_efficient', text: 'Energy Efficient'},
                {value: 'warranty', text: 'Extended Warranty'},
                {value: 'latest_model', text: 'Latest Model'},
                {value: 'good_battery', text: 'Good Battery Life'}
            ],
            'clothing': [
                {value: 'comfortable', text: 'Comfortable'},
                {value: 'trendy', text: 'Trendy/Fashionable'},
                {value: 'durable', text: 'Durable/Long-lasting'},
                {value: 'easy_care', text: 'Easy Care/Wash'}
            ],
            'footwear': [
                {value: 'comfortable', text: 'Comfortable'},
                {value: 'durable', text: 'Durable/Long-lasting'},
                {value: 'waterproof', text: 'Waterproof'},
                {value: 'lightweight', text: 'Lightweight'}
            ],
            'home_appliances': [
                {value: 'energy_efficient', text: 'Energy Efficient'},
                {value: 'warranty', text: 'Extended Warranty'},
                {value: 'quiet_operation', text: 'Quiet Operation'},
                {value: 'space_saving', text: 'Space-saving'}
            ],
            'beauty': [
                {value: 'natural', text: 'Natural/Organic'},
                {value: 'cruelty_free', text: 'Cruelty-free'},
                {value: 'fragrance_free', text: 'Fragrance-free'},
                {value: 'long_lasting', text: 'Long-lasting'}
            ],
            'sports': [
                {value: 'durable', text: 'Durable/Long-lasting'},
                {value: 'lightweight', text: 'Lightweight'},
                {value: 'high_performance', text: 'High Performance'},
                {value: 'waterproof', text: 'Waterproof/Weather-resistant'}
            ]
        };
        
        // Clear existing options
        preferencesSelect.innerHTML = '';
        
        // Add common preferences
        commonPreferences.forEach(pref => {
            const option = document.createElement('option');
            option.value = pref.value;
            option.textContent = pref.text;
            option.selected = selectedPreferences.includes(pref.value);
            preferencesSelect.appendChild(option);
        });
        
        // Add category-specific preferences if available
        if (categoryPreferences[category]) {
            categoryPreferences[category].forEach(pref => {
                const option = document.createElement('option');
                option.value = pref.value;
                option.textContent = pref.text;
                option.selected = selectedPreferences.includes(pref.value);
                preferencesSelect.appendChild(option);
            });
        }
        
        // Refresh Select2 if it's being used
        if (window.jQuery && window.jQuery.fn.select2) {
            jQuery(preferencesSelect).trigger('change');
        }
    }
});