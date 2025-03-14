import os
import datetime
from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired
from config import get_config
from agent import ShoppingAgent


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(get_config())
    
    # Initialize the shopping agent
    if app.config['GOOGLE_API_KEY'] and app.config['FIRECRAWL_API_KEY']:
        agent = ShoppingAgent(app.config['GOOGLE_API_KEY'], app.config['FIRECRAWL_API_KEY'])
    else:
        agent = None
        app.logger.warning('API keys not found. Shopping agent functionality will be limited.')
    
    # Create form class for search
    class SearchForm(FlaskForm):
        category = SelectField('Product Category', validators=[DataRequired()], 
                               choices=app.config['PRODUCT_CATEGORIES'])
        specific_item = StringField('Specific Item (Optional)')
        preferences = SelectMultipleField('Preferences (Select multiple)', 
                                         choices=[
                                             ('high_quality', 'High Quality'),
                                             ('eco_friendly', 'Eco-Friendly'),
                                             ('popular', 'Popular/Highly Rated'),
                                             ('fast_delivery', 'Fast Delivery'),
                                             ('discounted', 'On Discount/Sale'),
                                             ('new_arrival', 'New Arrivals')
                                         ])
        budget = SelectField('Budget Range', validators=[DataRequired()], 
                            choices=app.config['BUDGET_RANGES'])
        brand = SelectField('Preferred Brand (Optional)', choices=app.config['BRANDS'])
        additional_info = TextAreaField('Additional Requirements (Optional)')
        submit = SubmitField('Find Products')
    
    @app.route('/', methods=['GET', 'POST'])
    def index():
        """Home page with search form."""
        form = SearchForm()
        
        if form.validate_on_submit():
            if not agent:
                flash('Shopping agent is not properly configured. Please check API keys.', 'error')
                return render_template('index.html', form=form)
            
            # Store form data in session for use in results page
            session['search_data'] = {
                'category': form.category.data,
                'specific_item': form.specific_item.data,
                'preferences': form.preferences.data,
                'budget': form.budget.data,
                'brand': form.brand.data,
                'additional_info': form.additional_info.data
            }
            
            return redirect(url_for('results'))
        
        return render_template('index.html', form=form)
    
    @app.route('/results')
    def results():
        """Results page showing product recommendations."""
        if 'search_data' not in session:
            flash('Please complete the search form first.', 'error')
            return redirect(url_for('index'))
        
        if not agent:
            flash('Shopping agent is not properly configured. Please check API keys.', 'error')
            return redirect(url_for('index'))
        
        search_data = session['search_data']
        
        # Format query for the agent
        query = agent.format_query(
            category=search_data['category'],
            specific_item=search_data['specific_item'],
            preferences=search_data['preferences'],
            budget_range=search_data['budget'],
            brand=search_data['brand'],
            additional_info=search_data['additional_info']
        )
        
        # Get recommendations from the agent
        recommendations = agent.get_recommendations(query)
        
        return render_template('results.html', 
                               recommendations=recommendations,
                               search_data=search_data,
                               query=query)
    
    return app


# Create the application
app = create_app()

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_ENV') == 'development')