/**
 * Shopping Agent - Client-side JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if Bootstrap is loaded
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl)
        });
    }

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
        
        // Apply the formatted HTML
        content.innerHTML = html;
    }
});