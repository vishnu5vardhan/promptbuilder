from core.intent_classifier import classify_intent
from core.context_fetcher import fetch_context
from core.template_engine import render_template

def build_prompt(user_question, user_id="user123"):
    """
    Orchestrates the prompt building pipeline.
    
    Args:
        user_question (str): The user's question
        user_id (str): The user's ID
        
    Returns:
        dict: The result containing:
            - intent: The detected intent
            - confidence: The confidence score
            - prompt: The filled prompt template
    """
    # Step 1: Classify the intent
    intent_result = classify_intent(user_question)
    intent = intent_result["intent"]
    template_name = intent_result["template"]
    confidence = intent_result["confidence"]
    
    # Step 2: Fetch context data
    if confidence > 0.05:  # Lower threshold to allow more intents to match
        context_data = fetch_context(user_id, intent, user_question)
        
        # Step 3: Fill template if available
        if template_name:
            filled_prompt = render_template(template_name, context_data)
        else:
            filled_prompt = f"No template available for intent: {intent}.\n\nUser question: {user_question}"
    else:
        # Use fallback template for low confidence
        context_data = {'user_question': user_question, 'user_name': 'User'}
        filled_prompt = render_template('fallback.txt', context_data)
    
    return {
        "intent": intent,
        "confidence": confidence,
        "prompt": filled_prompt
    }


# For testing
if __name__ == "__main__":
    # Test with a sample question
    test_questions = [
        "What is my salary?",
        "How much did I spend on Amazon?",
        "What's my debt-to-income ratio?",
        "What are my subscriptions?",
        "Tell me my savings rate",
        "How's my credit card usage?"
    ]
    
    for question in test_questions:
        print(f"\n\n===== Testing: {question} =====")
        result = build_prompt(question)
        print(f"Detected Intent: {result['intent']} (Confidence: {result['confidence']:.2f})")
        print("\nGenerated Prompt:")
        print("-" * 50)
        print(result["prompt"])
        print("-" * 50)
