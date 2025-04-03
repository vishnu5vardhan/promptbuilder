#!/usr/bin/env python3
"""
Test script for the financial prompt engine.
Runs a series of test questions through the full pipeline.
"""

import sys
import os
import json

# Add the parent directory to the path to import the core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.prompt_builder import build_prompt

# Test questions covering different intents
TEST_QUESTIONS = [
    {
        "question": "What is my salary?",
        "expected_intent": "salary_query"
    },
    {
        "question": "How much did I spend on Amazon?",
        "expected_intent": "merchant_spend_summary"
    },
    {
        "question": "What's my debt-to-income ratio?",
        "expected_intent": "debt_to_income_ratio"
    },
    {
        "question": "What are my subscriptions?",
        "expected_intent": "subscription_summary"
    },
    {
        "question": "Tell me my savings rate",
        "expected_intent": "savings_rate_query"
    },
    {
        "question": "How's my credit card usage?",
        "expected_intent": "credit_card_usage"
    },
    {
        "question": "Where did most of my money go last month?",
        "expected_intent": "top_spend_category"
    },
    {
        "question": "Am I overspending on food delivery?",
        "expected_intent": "category_overuse_warning"
    },
    # New conversational intent tests
    {
        "question": "Hi",
        "expected_intent": "greeting"
    },
    {
        "question": "Who are you?",
        "expected_intent": "bot_identity"
    },
    {
        "question": "What can you do?",
        "expected_intent": "bot_capabilities"
    },
    {
        "question": "Thanks for your help",
        "expected_intent": "thank_you"
    },
    {
        "question": "Bye",
        "expected_intent": "goodbye"
    }
]

def run_tests():
    """Run all test questions through the prompt engine."""
    print("Starting Financial Prompt Engine Tests\n")
    
    passed = 0
    failed = 0
    
    for test_case in TEST_QUESTIONS:
        question = test_case["question"]
        expected_intent = test_case["expected_intent"]
        
        print(f"Test: \"{question}\"")
        print(f"Expected intent: {expected_intent}")
        
        # Run through the prompt builder
        result = build_prompt(question)
        
        # Check if the intent matches the expected intent
        detected_intent = result["intent"]
        confidence = result["confidence"]
        
        if detected_intent == expected_intent:
            status = "PASS"
            passed += 1
        else:
            status = "FAIL"
            failed += 1
            
        print(f"Detected intent: {detected_intent} (Confidence: {confidence:.2f})")
        print(f"Status: {status}\n")
        
        # Save prompt to a file for review
        save_test_output(question, result)
        
    print(f"Test Summary: {passed} passed, {failed} failed")
    print(f"Success rate: {passed/(passed+failed)*100:.1f}%")
    
    return failed

def save_test_output(question, result):
    """Save the test output to a file for review."""
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
    
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create a filename based on the question
    filename = question.lower().replace(' ', '_').replace('?', '').replace("'", "")[:30]
    filepath = os.path.join(output_dir, f"{filename}.txt")
    
    # Write the output to the file
    with open(filepath, 'w') as f:
        f.write(f"Question: {question}\n")
        f.write(f"Intent: {result['intent']} (Confidence: {result['confidence']:.2f})\n")
        f.write("\nGenerated Prompt:\n")
        f.write("-" * 50 + "\n")
        f.write(result["prompt"])
        f.write("\n" + "-" * 50)

if __name__ == "__main__":
    sys.exit(run_tests())
