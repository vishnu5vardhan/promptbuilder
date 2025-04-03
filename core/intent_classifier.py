import json
import os

# Load intent rules from config
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config/intents.json')

def load_intent_rules():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)


def classify_intent(user_question: str):
    """
    Classifies a user's question into a predefined intent using keyword rules.

    Returns:
        {
            "intent": "matched_intent_name",
            "template": "corresponding_template.txt",
            "confidence": score (1.0 if matched, 0.0 if not)
        }
        or None if no match
    """
    user_question_lower = user_question.lower()
    intent_rules = load_intent_rules()

    best_match = None
    highest_score = 0

    # Special handling for very short queries
    is_short_query = len(user_question_lower.split()) <= 3
    
    # Conversational intents that should get boosted for short queries
    conversational_intents = ['greeting', 'thank_you', 'goodbye', 'bot_identity', 'bot_capabilities']
    
    # Special handling for merchant-specific queries
    merchants = ["amazon", "swiggy", "zomato", "netflix", "spotify", "ola", "uber", "makemytrip", "agoda"]
    merchant_phrases = ["spending in", "spend in", "spent on", "spending on", "spend on"]
    
    # Special handling for category-specific queries
    categories = ["food", "travel", "shopping", "utilities", "transportation", "emi"]
    category_phrases = ["spending on", "spend on", "spent on", "how much on", "money on", "budget for"]
    
    # Check for subscription intent specifically (should take precedence over category handling)
    if "subscriptions" in user_question_lower or "subscription" in user_question_lower:
        for rule in intent_rules:
            if rule.get("intent") == "subscription_summary":
                return {
                    "intent": "subscription_summary",
                    "template": rule.get("template"),
                    "confidence": 0.9
                }
    
    # Check for overspending warnings
    if "overspending" in user_question_lower or "too much" in user_question_lower or "spending too much" in user_question_lower:
        for rule in intent_rules:
            if rule.get("intent") == "category_overuse_warning":
                return {
                    "intent": "category_overuse_warning",
                    "template": rule.get("template"),
                    "confidence": 0.9
                }
    
    # Check for merchant-specific queries
    for merchant in merchants:
        if merchant in user_question_lower:
            for phrase in merchant_phrases:
                if phrase in user_question_lower:
                    # This is almost certainly a merchant spend query
                    for rule in intent_rules:
                        if rule.get("intent") == "merchant_spend_summary":
                            return {
                                "intent": "merchant_spend_summary",
                                "template": rule.get("template"),
                                "confidence": 0.9
                            }
    
    # Check for category-specific queries
    for category in categories:
        if category in user_question_lower:
            for phrase in category_phrases:
                if phrase in user_question_lower or f"my {category}" in user_question_lower:
                    # This is likely a category spending query
                    for rule in intent_rules:
                        if rule.get("intent") == "spending_by_category":
                            return {
                                "intent": "spending_by_category",
                                "template": rule.get("template"),
                                "confidence": 0.8
                            }
                            
    # Check for simple category mentions (like "WHAT ABOUT MY FOOD SPENDING?")
    for category in categories:
        if category in user_question_lower and any(word in user_question_lower for word in ["spending", "spend", "spent", "expenses", "costs"]):
            for rule in intent_rules:
                if rule.get("intent") == "spending_by_category":
                    return {
                        "intent": "spending_by_category",
                        "template": rule.get("template"),
                        "confidence": 0.7
                    }

    for rule in intent_rules:
        score = 0
        total_matches = 0
        keywords = rule.get("keywords", [])
        intent_name = rule.get("intent", "")
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # Exact matches get higher weight
            if keyword_lower in user_question_lower:
                if len(keyword_lower.split()) > 1:  # Multi-word keyword gets higher score
                    score += 2
                else:
                    score += 1
                total_matches += 1
        
        # If there are any matches, calculate the score
        if total_matches > 0:
            # Normalize by the total number of keywords
            # But give more weight to the number of matched keywords
            weighted_score = score / len(keywords) * (0.5 + 0.5 * (total_matches / len(keywords)))
            
            # Boost score for conversational intents if it's a short query
            if is_short_query and intent_name in conversational_intents:
                weighted_score *= 2.0
            
            # Exact match for short queries
            if is_short_query and user_question_lower in keywords:
                weighted_score = 1.0
            
            # Cap the score at 1.0
            weighted_score = min(weighted_score, 1.0)
            
            if weighted_score > highest_score:
                best_match = rule
                highest_score = weighted_score

    if best_match:
        return {
            "intent": best_match["intent"],
            "template": best_match["template"],
            "confidence": highest_score
        }

    return {
        "intent": "unknown",
        "template": None,
        "confidence": 0.0
    }


# Optional test block
if __name__ == "__main__":
    sample_questions = [
        "What is my salary?",
        "How much did I spend on Amazon?",
        "What's my debt-to-income ratio?",
        "What are my subscriptions?",
        "Tell me my savings rate",
        "Where did most of my money go last month?",
        "Am I overspending on food delivery?",
        "What's my average daily spend?",
        "How many transactions did I make this month?",
        "What's the largest transaction I made this month?",
        "Which bank account do I use the most?",
        "Show me my credit card due dates.",
        "When is my Netflix bill due?",
        "Any unusual spending this week?",
        "How's my spending compared to last month?"
    ]

    for q in sample_questions:
        result = classify_intent(q)
        print(f"\n[Question]: {q}")
        print(f"[Intent]: {result['intent']}")
        print(f"[Template]: {result['template']}")
        print(f"[Confidence]: {result['confidence']}")
