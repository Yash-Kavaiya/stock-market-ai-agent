import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-for-development-only')
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    FIRECRAWL_API_KEY = os.environ.get('FIRECRAWL_API_KEY')
    
    # Product categories for dropdown
    PRODUCT_CATEGORIES = [
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('footwear', 'Footwear'),
        ('home_appliances', 'Home Appliances'),
        ('beauty', 'Beauty & Personal Care'),
        ('sports', 'Sports & Fitness'),
        ('books', 'Books'),
        ('toys', 'Toys & Games')
    ]
    
    # Budget ranges for dropdown
    BUDGET_RANGES = [
        ('0-1000', 'Under ₹1,000'),
        ('1000-5000', '₹1,000 - ₹5,000'),
        ('5000-10000', '₹5,000 - ₹10,000'),
        ('10000-20000', '₹10,000 - ₹20,000'),
        ('20000-50000', '₹20,000 - ₹50,000'),
        ('50000+', 'Above ₹50,000')
    ]
    
    # Brands for dropdown (sample list, can be expanded)
    BRANDS = [
        ('', 'Any Brand'),
        ('samsung', 'Samsung'),
        ('apple', 'Apple'),
        ('nike', 'Nike'),
        ('adidas', 'Adidas'),
        ('sony', 'Sony'),
        ('lg', 'LG'),
        ('hp', 'HP'),
        ('dell', 'Dell'),
        ('lenovo', 'Lenovo')
    ]


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = False
    TESTING = True


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# Get configuration based on environment
def get_config():
    env = os.environ.get('FLASK_ENV', 'default')
    return config.get(env)