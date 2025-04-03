#!/usr/bin/env python3
"""
Financial Prompt Engine - Main Script

This script runs the full prompt engine pipeline:
1. Takes a user's financial question
2. Classifies the intent
3. Fetches relevant context data
4. Fills a prompt template
5. Returns the GPT-ready prompt
"""

import sys
import argparse
from core.prompt_builder import build_prompt

def get_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Financial Prompt Engine")
    parser.add_argument(
        "question", 
        nargs="?", 
        help="The financial question to process"
    )
    parser.add_argument(
        "--user", 
        "-u", 
        default="user123", 
        help="User ID (default: user123)"
    )
    parser.add_argument(
        "--verbose", 
        "-v", 
        action="store_true", 
        help="Show detailed information about the process"
    )
    return parser.parse_args()

def get_input_question(args):
    """Get the question from arguments or prompt the user."""
    if args.question:
        return args.question
    
    return input("Enter your financial question: ")

def main():
    args = get_args()
    
    # Get the question
    question = get_input_question(args)
    
    # Build the prompt
    result = build_prompt(question, args.user)
    
    # Print results
    if args.verbose:
        print(f"\nDetected Intent: {result['intent']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print("\n" + "=" * 50)
        print("Generated GPT-Ready Prompt:")
        print("=" * 50)
    
    print(result['prompt'])
    
    # Return success code
    return 0

if __name__ == "__main__":
    sys.exit(main())
