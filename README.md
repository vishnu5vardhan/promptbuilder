# Financial Prompt Engine

A modular Python system that takes a user's financial question, detects the intent, fetches context data, and generates a GPT-ready prompt.

## Overview

This project implements a complete prompt generation pipeline for financial questions:

1. **Intent Classification**: Detects what the user is asking for using keyword matching
2. **Context Fetching**: Retrieves relevant financial data based on the intent
3. **Prompt Generation**: Fills a template with user-specific data to create a GPT-ready prompt

## Project Structure

```
financial-prompt-engine/
├── core/                        # Core logic modules
│   ├── intent_classifier.py     # Classifies user question into intent
│   ├── context_fetcher.py       # Fetches context data for a given intent
│   ├── prompt_builder.py        # Orchestrates the pipeline
│   └── template_engine.py       # Loads and fills templates
│
├── templates/                   # Prompt templates with {placeholders}
│   ├── salary_query.txt
│   ├── merchant_spend_summary.txt
│   └── ... (more templates)
│
├── data/                        # Mock data (for now)
│   ├── sample_transactions.json
│   ├── sample_persona.json
│   └── sample_products.json
│
├── config/                      # Configuration files
│   └── intents.json             # Intent rules with keywords
│
├── test/                        # Test scripts
│   └── test_engine.py           # End-to-end testing
│
├── run_prompt_engine.py         # Main script
└── requirements.txt             # Dependencies
```

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/financial-prompt-engine.git
cd financial-prompt-engine
```

2. Set up a virtual environment (optional but recommended):
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

## Usage

### Command Line

Run the prompt engine with a question:

```
python run_prompt_engine.py "What is my salary?"
```

Options:
- `--user` or `-u`: Specify a user ID (default: user123)
- `--verbose` or `-v`: Show detailed processing information

### As a Module

```python
from core.prompt_builder import build_prompt

question = "What is my debt-to-income ratio?"
result = build_prompt(question, user_id="user123")

print(result["intent"])        # The detected intent
print(result["confidence"])    # Confidence score
print(result["prompt"])        # The generated prompt
```

## Testing

Run the test suite:

```
python test/test_engine.py
```

This will process several test questions and save the generated prompts to `test/outputs/`.

## Supported Question Types

The system currently supports various financial questions including:

- Salary and income queries
- Spending summaries (by merchant, category, etc.)
- Debt and loan analysis
- Savings rate assessment
- Credit card usage
- Subscription tracking
- And many more

## Extending the System

### Adding New Intents

1. Add a new intent entry to `config/intents.json`:
```json
{
  "intent": "new_intent_name",
  "keywords": ["keyword1", "keyword2", "phrase with multiple words"],
  "template": "new_intent_template.txt"
}
```

2. Create a template file in `templates/new_intent_template.txt`

3. Update the context fetcher to handle the new intent

## Future Improvements

- Connect to real data sources instead of mock data
- Implement machine learning for more accurate intent detection
- Add more sophisticated template handling
- Implement real-time data processing

## License

MIT

---

*Note: This project uses mock data for demonstration purposes. In a production environment, it would connect to real financial data sources.*
