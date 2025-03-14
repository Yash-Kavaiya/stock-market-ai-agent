from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.firecrawl import FirecrawlTools

class ShoppingAgent:
    """Shopping agent class that uses the phi library to recommend products."""
    
    def __init__(self, google_api_key, firecrawl_api_key):
        """Initialize the shopping agent with API keys.
        
        Args:
            google_api_key (str): Google API key for Gemini
            firecrawl_api_key (str): Firecrawl API key
        """
        self.google_api_key = google_api_key
        self.firecrawl_api_key = firecrawl_api_key
        self.agent = self._create_agent()
    
    def _create_agent(self):
        """Create and return a phi agent with Gemini model and Firecrawl tools.
        
        Returns:
            Agent: Phi agent configured for product recommendations
        """
        return Agent(
            name="shopping partner",
            model=Gemini(
                id="gemini-2.0-flash-exp",
                api_key=self.google_api_key
            ),
            instructions=[
                "You are a product recommender agent specializing in finding products that match user preferences.",
                "Prioritize finding products that satisfy as many user requirements as possible, but ensure a minimum match of 50%.",
                "Search for products only from authentic and trusted e-commerce websites such as Google Shopping, Amazon, Flipkart, Myntra, Meesho, Nike, and other reputable platforms.",
                "Verify that each product recommendation is in stock and available for purchase.",
                "Avoid suggesting counterfeit or unverified products.",
                "Clearly mention the key attributes of each product (e.g., price, brand, features) in the response.",
                "Format the recommendations neatly and ensure clarity for ease of user understanding.",
            ],
            tools=[FirecrawlTools(api_key=self.firecrawl_api_key)],
        )
    
    def get_recommendations(self, query):
        """Get product recommendations based on the user query.
        
        Args:
            query (str): User query describing product preferences
        
        Returns:
            str: Formatted product recommendations
        """
        try:
            response = self.agent.run(query)
            
            # Check if response is a string
            if isinstance(response, str):
                return response
            
            # If response is an object with content attribute
            if hasattr(response, 'content'):
                return response.content
                
            # If it's a dict or has a different structure
            if isinstance(response, dict) and 'content' in response:
                return response['content']
                
            # Last resort: convert to string and try to extract useful parts
            response_str = str(response)
            if "content='" in response_str:
                # Try to extract content between content=' and the next single quote
                import re
                content_match = re.search(r"content='([^']+)'", response_str)
                if content_match:
                    return content_match.group(1)
            
            # If we can't extract properly, return the original response
            return response
        except Exception as e:
            return f"Error retrieving recommendations: {str(e)}"
    
    def format_query(self, category, specific_item, preferences, budget_range, brand=None, additional_info=None):
        """Format user inputs into a query string for the agent.
        
        Args:
            category (str): Product category
            specific_item (str): Specific item within the category
            preferences (list): List of user preferences
            budget_range (str): Budget range selected
            brand (str, optional): Preferred brand. Defaults to None.
            additional_info (str, optional): Additional information. Defaults to None.
        
        Returns:
            str: Formatted query string
        """
        # Convert budget range to actual amounts
        budget_mapping = {
            '0-1000': 'under Rs. 1,000',
            '1000-5000': 'between Rs. 1,000 and Rs. 5,000',
            '5000-10000': 'between Rs. 5,000 and Rs. 10,000',
            '10000-20000': 'between Rs. 10,000 and Rs. 20,000',
            '20000-50000': 'between Rs. 20,000 and Rs. 50,000',
            '50000+': 'above Rs. 50,000'
        }
        
        budget_text = budget_mapping.get(budget_range, 'flexible budget')
        
        # Build the query
        query = f"I am looking for {specific_item if specific_item else category}"
        
        if brand and brand != '':
            query += f" from {brand}"
            
        query += " with the following preferences: "
        
        if preferences:
            query += ", ".join(preferences)
            
        query += f". Budget: {budget_text}"
        
        if additional_info:
            query += f". Additional requirements: {additional_info}"
            
        return query