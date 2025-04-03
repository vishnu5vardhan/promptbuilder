import json
import os
from datetime import datetime

# Load mock data
DATA_PATH = os.path.join(os.path.dirname(__file__), '../data')

def load_mock_data():
    """Load all mock data files."""
    with open(os.path.join(DATA_PATH, 'sample_transactions.json'), 'r') as f:
        transactions = json.load(f)
    
    with open(os.path.join(DATA_PATH, 'sample_persona.json'), 'r') as f:
        persona = json.load(f)
    
    with open(os.path.join(DATA_PATH, 'sample_products.json'), 'r') as f:
        products = json.load(f)
    
    return {
        'transactions': transactions,
        'persona': persona,
        'products': products
    }

def fetch_context(user_id, intent, user_question=""):
    """
    Fetches context data for generating prompts based on the detected intent.
    This function pulls user-specific data, analyzes it, and formats it
    so it can be used in the prompt templates.
    
    Args:
        user_id (str): The ID of the user
        intent (str): The detected intent
        user_question (str, optional): The original user question for entity extraction
        
    Returns:
        dict: A dictionary containing context data for the prompt
    """
    # Load mock data
    mock_data = load_mock_data()
    transactions = mock_data['transactions']
    persona = mock_data['persona']
    products = mock_data['products']
    
    # Base context with user info
    context = {
        'user_id': user_id,
        'user_name': persona['name'],
        'query_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Handle conversational intents
    if intent in ['greeting', 'bot_identity', 'bot_capabilities', 'thank_you', 'goodbye']:
        # These intents don't need additional context data beyond user info
        return context
    
    # Add intent-specific context
    if intent == 'salary_query':
        salary_transactions = [tx for tx in transactions if tx['category'] == 'salary']
        context.update({
            'salary_transactions': format_transactions(salary_transactions),
            'monthly_income': persona['financial_profile']['monthly_income'],
            'annual_income': persona['financial_profile']['annual_income']
        })
    
    elif intent == 'merchant_spend_summary':
        # Try to extract merchant name from the query if provided
        merchant_name = "AMAZON"  # Default merchant
        
        # Common merchants in our dataset
        known_merchants = ["AMAZON", "SWIGGY", "ZOMATO", "NETFLIX", "SPOTIFY", "OLA", "UBER", "MAKEMYTRIP", "AGODA"]
        
        # Check if any known merchant is mentioned in the query
        if user_question:
            user_question_lower = user_question.lower()
            for merchant in known_merchants:
                if merchant.lower() in user_question_lower:
                    merchant_name = merchant
                    break
        
        merchant_transactions = [tx for tx in transactions if tx['merchant'] == merchant_name]
        
        total_spend = sum(tx['amount'] for tx in merchant_transactions if tx['amount'] < 0)
        start_date = min(tx['date'] for tx in merchant_transactions) if merchant_transactions else "N/A"
        end_date = max(tx['date'] for tx in merchant_transactions) if merchant_transactions else "N/A"
        
        payment_methods = {}
        for tx in merchant_transactions:
            payment_methods[tx['account']] = payment_methods.get(tx['account'], 0) + 1
        
        most_used_payment = max(payment_methods.items(), key=lambda x: x[1])[0] if payment_methods else "N/A"
        
        context.update({
            'merchant_name': merchant_name,
            'merchant_transactions': format_transactions(merchant_transactions),
            'total_spend': abs(total_spend),
            'transaction_count': len(merchant_transactions),
            'average_transaction': abs(total_spend) / len(merchant_transactions) if merchant_transactions else 0,
            'start_date': start_date,
            'end_date': end_date,
            'most_used_payment_method': most_used_payment
        })
    
    elif intent == 'monthly_spend_summary':
        # Get current month transactions (using March 2023 for demo)
        month = "March"
        year = "2023"
        monthly_transactions = [tx for tx in transactions if tx['date'].startswith(f"2023-03")]
        
        # Calculate category breakdown
        categories = {}
        for tx in monthly_transactions:
            if tx['amount'] < 0:  # Only consider expenses
                category = tx['category']
                categories[category] = categories.get(category, 0) + abs(tx['amount'])
        
        category_breakdown = "\n".join([f"- {cat}: ₹{amount:.2f}" for cat, amount in categories.items()])
        
        # Calculate top merchants
        merchants = {}
        for tx in monthly_transactions:
            if tx['amount'] < 0:
                merchant = tx['merchant']
                merchants[merchant] = merchants.get(merchant, 0) + abs(tx['amount'])
        
        top_merchants = "\n".join([f"- {merchant}: ₹{amount:.2f}" for merchant, amount in 
                                  sorted(merchants.items(), key=lambda x: x[1], reverse=True)[:5]])
        
        # Find previous month data (February for demo)
        prev_month_transactions = [tx for tx in transactions if tx['date'].startswith(f"2023-02")]
        prev_month_total = sum(abs(tx['amount']) for tx in prev_month_transactions if tx['amount'] < 0)
        
        # Current month total
        current_month_total = sum(abs(tx['amount']) for tx in monthly_transactions if tx['amount'] < 0)
        
        # Month over month change
        if prev_month_total > 0:
            mom_change = ((current_month_total - prev_month_total) / prev_month_total) * 100
            increase_decrease = "increase" if mom_change > 0 else "decrease"
        else:
            mom_change = 0
            increase_decrease = "no change"
        
        # Get highest and lowest categories
        if categories:
            highest_category = max(categories.items(), key=lambda x: x[1])
            lowest_category = min(categories.items(), key=lambda x: x[1])
        else:
            highest_category = ("None", 0)
            lowest_category = ("None", 0)
        
        # Get largest transaction
        largest_tx = min(monthly_transactions, key=lambda x: x['amount']) if monthly_transactions else None
        
        context.update({
            'month_name': f"{month} {year}",
            'transaction_count': len(monthly_transactions),
            'total_spend': current_month_total,
            'category_breakdown': category_breakdown,
            'top_merchants': top_merchants,
            'highest_category': highest_category[0],
            'highest_category_amount': highest_category[1],
            'lowest_category': lowest_category[0],
            'lowest_category_amount': lowest_category[1],
            'largest_transaction_amount': abs(largest_tx['amount']) if largest_tx else 0,
            'largest_transaction_merchant': largest_tx['merchant'] if largest_tx else "None",
            'average_transaction': current_month_total / len([tx for tx in monthly_transactions if tx['amount'] < 0]) if monthly_transactions else 0,
            'previous_month_total': prev_month_total,
            'month_over_month_change': abs(mom_change),
            'increase_decrease': increase_decrease
        })
    
    elif intent == 'spending_by_category':
        # Try to extract category name from the query if provided
        requested_category = "food"  # Default category
        
        # Common spending categories in our dataset
        known_categories = ["food", "travel", "shopping", "utilities", "transportation", "subscription", "emi"]
        
        # Check if any known category is mentioned in the query
        if user_question:
            user_question_lower = user_question.lower()
            for category in known_categories:
                if category in user_question_lower:
                    requested_category = category
                    break
        
        # Get transactions for the requested category
        category_transactions = [tx for tx in transactions if tx['category'] == requested_category]
        
        # Calculate total spending in this category
        category_total = sum(abs(tx['amount']) for tx in category_transactions if tx['amount'] < 0)
        
        # Calculate time period
        start_date = min(tx['date'] for tx in category_transactions) if category_transactions else "N/A"
        end_date = max(tx['date'] for tx in category_transactions) if category_transactions else "N/A"
        
        # Get top merchants in this category
        category_merchants = {}
        for tx in category_transactions:
            if tx['amount'] < 0:  # Only consider expenses
                merchant = tx['merchant']
                category_merchants[merchant] = category_merchants.get(merchant, 0) + abs(tx['amount'])
        
        top_category_merchants = "\n".join([f"- {merchant}: ₹{amount:.2f}" for merchant, amount in 
                                sorted(category_merchants.items(), key=lambda x: x[1], reverse=True)[:3]])
        
        # Calculate percentage of total monthly spending
        monthly_total = sum(abs(tx['amount']) for tx in transactions if tx['amount'] < 0 and tx['date'].startswith('2023-03'))
        percentage_of_total = (category_total / monthly_total * 100) if monthly_total > 0 else 0
        
        # Format transactions
        formatted_transactions = format_transactions(category_transactions)
        
        context.update({
            'requested_category': requested_category,
            'category_transactions': formatted_transactions,
            'category_total': category_total,
            'transaction_count': len(category_transactions),
            'average_transaction': category_total / len([tx for tx in category_transactions if tx['amount'] < 0]) if category_transactions else 0,
            'start_date': start_date,
            'end_date': end_date,
            'percentage_of_total': round(percentage_of_total, 2),
            'monthly_trend': "Data not available for monthly trend", # Placeholder for now
            'top_merchants': top_category_merchants
        })
    
    elif intent == 'category_overuse_warning':
        # Try to extract category name from the query if provided
        category = "food"  # Default category
        
        # Common spending categories in our dataset
        known_categories = ["food", "travel", "shopping", "utilities", "transportation", "subscription", "emi"]
        
        # Check if any known category is mentioned in the query
        if user_question:
            user_question_lower = user_question.lower()
            for cat in known_categories:
                if cat in user_question_lower:
                    category = cat
                    break
                    
        # Special handling for "food delivery" phrase
        if "food delivery" in user_question.lower() or "delivery" in user_question.lower():
            category = "food"
        
        # Get transactions for the requested category
        category_transactions = [tx for tx in transactions if tx['category'] == category]
        
        # Calculate total spending in this category
        category_total = sum(abs(tx['amount']) for tx in category_transactions if tx['amount'] < 0)
        
        # Calculate time period
        start_date = min(tx['date'] for tx in category_transactions) if category_transactions else "N/A"
        end_date = max(tx['date'] for tx in category_transactions) if category_transactions else "N/A"
        
        # Calculate percentage of total monthly spending
        monthly_total = sum(abs(tx['amount']) for tx in transactions if tx['amount'] < 0 and tx['date'].startswith('2023-03'))
        percentage_of_total = (category_total / monthly_total * 100) if monthly_total > 0 else 0
        
        # Mock data for benchmarks and budget analysis
        average_monthly = category_total * 0.8  # Mock data: assume average is 80% of current
        difference_percentage = 25  # Mock data: assume 25% above average
        
        # Budget recommendations based on category
        budget_recommendations = {
            "food": 15,  # 15% of income
            "travel": 10,
            "shopping": 10,
            "utilities": 20,
            "transportation": 15,
            "subscription": 5,
            "emi": 20
        }
        
        monthly_income = persona['financial_profile']['monthly_income']
        recommended_budget = monthly_income * budget_recommendations.get(category, 10) / 100
        
        # Determine budget status
        if category_total > recommended_budget * 1.2:
            budget_status = "Significantly over budget"
        elif category_total > recommended_budget:
            budget_status = "Slightly over budget"
        else:
            budget_status = "Within budget"
        
        # Format transactions
        formatted_transactions = format_transactions(category_transactions)
        
        context.update({
            'category': category,
            'category_transactions': formatted_transactions,
            'category_total': category_total,
            'transaction_count': len(category_transactions),
            'average_transaction': category_total / len([tx for tx in category_transactions if tx['amount'] < 0]) if category_transactions else 0,
            'start_date': start_date,
            'end_date': end_date,
            'percentage_of_total': round(percentage_of_total, 2),
            'average_monthly': average_monthly,
            'current_month_total': category_total,
            'difference_percentage': difference_percentage,
            'recommended_budget': recommended_budget,
            'budget_status': budget_status
        })
    
    elif intent == 'subscription_summary':
        # Get transactions for the subscription category
        subscription_transactions = [tx for tx in transactions if tx['category'] == 'subscription']
        
        # Group transactions by merchant (assuming each merchant is a distinct subscription)
        subscriptions = {}
        for tx in subscription_transactions:
            if tx['amount'] < 0:  # Only consider expenses
                merchant = tx['merchant']
                amount = abs(tx['amount'])
                date = tx['date']
                
                if merchant not in subscriptions:
                    subscriptions[merchant] = {
                        'amount': amount,
                        'date': date,
                        'payment_method': tx['account'],
                        'description': tx['description']
                    }
        
        # Format active subscriptions
        active_subscription_items = []
        for merchant, details in subscriptions.items():
            active_subscription_items.append(f"- {merchant}: ₹{details['amount']:.2f}/month (paid via {details['payment_method']})")
        
        active_subscriptions = "\n".join(active_subscription_items)
        
        # Calculate most expensive and newest subscriptions
        if subscriptions:
            most_expensive = max(subscriptions.items(), key=lambda x: x[1]['amount'])
            newest = max(subscriptions.items(), key=lambda x: x[1]['date'])
            
            most_expensive_str = f"{most_expensive[0]}: ₹{most_expensive[1]['amount']:.2f}/month"
            newest_subscription = f"{newest[0]} (added on {newest[1]['date']})"
        else:
            most_expensive_str = "None"
            newest_subscription = "None"
        
        # Group by payment method
        payment_methods = {}
        for merchant, details in subscriptions.items():
            method = details['payment_method']
            payment_methods[method] = payment_methods.get(method, 0) + 1
        
        payment_methods_str = "\n".join([f"- {method}: {count} subscription(s)" for method, count in payment_methods.items()])
        
        # Group by type (using basic categorization based on merchant name)
        subscription_types = {
            "Entertainment": ["NETFLIX", "PRIME", "SPOTIFY", "DISNEY"],
            "Productivity": ["MICROSOFT", "GOOGLE", "DROPBOX"],
            "Fitness": ["GYM", "FITNESS"],
            "News": ["TIMES", "ECONOMIST", "NEWS"]
        }
        
        type_counts = {category: 0 for category in subscription_types}
        type_counts["Other"] = 0
        
        for merchant in subscriptions:
            categorized = False
            for category, keywords in subscription_types.items():
                if any(keyword in merchant.upper() for keyword in keywords):
                    type_counts[category] += 1
                    categorized = True
                    break
                    
            if not categorized:
                type_counts["Other"] += 1
        
        subscription_types_str = "\n".join([f"- {category}: {count}" for category, count in type_counts.items() if count > 0])
        
        # Mock renewal schedule
        renewal_days = [5, 10, 15, 20, 25]
        renewal_items = []
        
        import random
        for i, (merchant, details) in enumerate(subscriptions.items()):
            day = renewal_days[i % len(renewal_days)]
            renewal_items.append(f"- {merchant}: Renews on the {day}th of each month")
        
        renewal_schedule = "\n".join(renewal_items)
        
        # Calculate total and percentage of income
        total_monthly_cost = sum(details['amount'] for details in subscriptions.values())
        monthly_income = persona['financial_profile']['monthly_income']
        percentage_of_income = (total_monthly_cost / monthly_income * 100) if monthly_income > 0 else 0
        
        context.update({
            'active_subscriptions': active_subscriptions,
            'subscription_count': len(subscriptions),
            'total_monthly_cost': total_monthly_cost,
            'percentage_of_income': round(percentage_of_income, 2),
            'most_expensive': most_expensive_str,
            'newest_subscription': newest_subscription,
            'subscription_types': subscription_types_str,
            'payment_methods': payment_methods_str,
            'renewal_schedule': renewal_schedule
        })
    
    elif intent == 'debt_to_income_ratio':
        # Calculate monthly debt payments
        loan_payments = sum(loan['monthly_payment'] for loan in persona['financial_profile']['loans'])
        
        # Calculate credit card minimum payments (assume 5% of balance)
        cc_min_payments = sum(max(abs(account['balance']) * 0.05, 1000) 
                             for account in persona['financial_profile']['accounts'] 
                             if account['type'] == 'credit' and account['balance'] < 0)
        
        total_monthly_debt = loan_payments + cc_min_payments
        monthly_income = persona['financial_profile']['monthly_income']
        
        dti_ratio = (total_monthly_debt / monthly_income) * 100
        
        # Classify DTI ratio
        if dti_ratio < 28:
            dti_classification = "Excellent"
            credit_impact = "Positive"
            loan_eligibility = "High likelihood of approval for most loans"
        elif dti_ratio < 36:
            dti_classification = "Good"
            credit_impact = "Mostly positive"
            loan_eligibility = "Good chances for loan approval with favorable rates"
        elif dti_ratio < 43:
            dti_classification = "Moderate"
            credit_impact = "Neutral to slightly negative"
            loan_eligibility = "May qualify for most loans but with higher interest rates"
        else:
            dti_classification = "High"
            credit_impact = "Negative"
            loan_eligibility = "Difficult to qualify for new loans"
        
        # Format debt obligations
        debt_obligations = []
        for loan in persona['financial_profile']['loans']:
            debt_obligations.append(f"- {loan['name']}: ₹{loan['monthly_payment']}")
        
        for account in persona['financial_profile']['accounts']:
            if account['type'] == 'credit' and account['balance'] < 0:
                min_payment = max(abs(account['balance']) * 0.05, 1000)
                debt_obligations.append(f"- {account['name']} (min payment): ₹{min_payment:.2f}")
        
        context.update({
            'monthly_income': monthly_income,
            'debt_obligations': "\n".join(debt_obligations),
            'total_monthly_debt': total_monthly_debt,
            'dti_ratio': round(dti_ratio, 2),
            'dti_classification': dti_classification,
            'credit_impact': credit_impact,
            'loan_eligibility_impact': loan_eligibility
        })
    
    elif intent == 'savings_rate_query':
        monthly_income = persona['financial_profile']['monthly_income']
        total_expenses = persona['financial_profile']['total_expenses']
        monthly_savings = monthly_income - total_expenses
        savings_rate = (monthly_savings / monthly_income) * 100
        
        # Evaluate savings rate
        if savings_rate >= 30:
            savings_assessment = "Excellent - Well above recommended levels"
        elif savings_rate >= 20:
            savings_assessment = "Very Good - Above recommended levels"
        elif savings_rate >= 15:
            savings_assessment = "Good - Meeting recommended levels"
        elif savings_rate >= 10:
            savings_assessment = "Fair - Below ideal but on the right track"
        else:
            savings_assessment = "Needs improvement - Below recommended levels"
        
        # Mock savings breakdown
        savings_breakdown = [
            f"- Regular savings: ₹{monthly_savings * 0.3:.2f}",
            f"- Retirement contributions: ₹{monthly_savings * 0.4:.2f}",
            f"- Emergency fund: ₹{monthly_savings * 0.2:.2f}",
            f"- Other investments: ₹{monthly_savings * 0.1:.2f}"
        ]
        
        # Mock historical trend (3 months)
        savings_trend = [
            "- January 2023: 22%",
            "- February 2023: 24%",
            "- March 2023: 25%",
            f"- Current: {savings_rate:.1f}%"
        ]
        
        context.update({
            'monthly_income': monthly_income,
            'total_monthly_expenses': total_expenses,
            'monthly_savings': monthly_savings,
            'savings_rate': round(savings_rate, 1),
            'savings_breakdown': "\n".join(savings_breakdown),
            'savings_assessment': savings_assessment,
            'savings_trend': "\n".join(savings_trend)
        })
    
    elif intent == 'credit_card_usage':
        # Get credit card accounts
        cc_accounts = [account for account in persona['financial_profile']['accounts'] if account['type'] == 'credit']
        
        formatted_accounts = []
        for acc in cc_accounts:
            formatted_accounts.append(
                f"- {acc['name']}:\n"
                f"  Balance: ₹{abs(acc['balance'])}\n"
                f"  Credit limit: ₹{acc['credit_limit']}\n"
                f"  Utilization: {abs(acc['balance'])/acc['credit_limit']*100:.1f}%\n"
                f"  Due date: {acc['due_date']}"
            )
        
        # Get credit card transactions
        cc_transactions = [tx for tx in transactions if tx['account'] in ['hdfc_credit', 'icici_credit']]
        
        # Calculate spending by category
        categories = {}
        for tx in cc_transactions:
            if tx['amount'] < 0:  # Only consider expenses
                category = tx['category']
                categories[category] = categories.get(category, 0) + abs(tx['amount'])
        
        category_breakdown = "\n".join([f"- {cat}: ₹{amount:.2f}" for cat, amount in categories.items()])
        
        # Calculate totals
        total_limit = sum(acc['credit_limit'] for acc in cc_accounts)
        total_balance = sum(abs(acc['balance']) for acc in cc_accounts)
        utilization = (total_balance / total_limit) * 100 if total_limit > 0 else 0
        
        # Format due dates and payments
        due_dates = "\n".join([f"- {acc['name']}: {acc['due_date']}" for acc in cc_accounts])
        minimum_payments = "\n".join([f"- {acc['name']}: ₹{max(abs(acc['balance']) * 0.05, 1000):.2f}" for acc in cc_accounts])
        interest_rates = "\n".join([f"- {acc['name']}: {acc['interest_rate'] * 100:.2f}%" for acc in cc_accounts])
        
        context.update({
            'credit_card_accounts': "\n".join(formatted_accounts),
            'total_spend': sum(abs(tx['amount']) for tx in cc_transactions if tx['amount'] < 0),
            'transaction_count': len([tx for tx in cc_transactions if tx['amount'] < 0]),
            'average_transaction': sum(abs(tx['amount']) for tx in cc_transactions if tx['amount'] < 0) / 
                                  len([tx for tx in cc_transactions if tx['amount'] < 0]) if cc_transactions else 0,
            'category_breakdown': category_breakdown,
            'total_credit_limit': total_limit,
            'current_balance': total_balance,
            'utilization_ratio': round(utilization, 1),
            'due_dates': due_dates,
            'minimum_payments': minimum_payments,
            'interest_rates': interest_rates
        })
    
    else:
        # For unknown intents, return basic user data
        context.update({
            'message': f"No specific context data available for intent: {intent}"
        })
    
    return context

def format_transactions(transactions):
    """Format transaction data for display in prompts."""
    if not transactions:
        return "No transactions found."
    
    formatted = []
    for tx in transactions:
        amount_str = f"₹{abs(tx['amount'])}" + (" (credit)" if tx['amount'] > 0 else " (debit)")
        formatted.append(f"- Date: {tx['date']}, Amount: {amount_str}, Description: {tx['description']}")
    
    return "\n".join(formatted)


# For testing
if __name__ == "__main__":
    # Test different intents
    intents_to_test = [
        'salary_query',
        'merchant_spend_summary',
        'monthly_spend_summary',
        'debt_to_income_ratio',
        'savings_rate_query',
        'credit_card_usage',
        'spending_by_category',
        'category_overuse_warning',
        'subscription_summary'
    ]
    
    for intent in intents_to_test:
        print(f"\nTesting intent: {intent}")
        context = fetch_context("user123", intent)
        print(f"Keys in context: {list(context.keys())}")
        print(f"Sample data: {list(context.items())[:3]}")
