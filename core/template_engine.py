import os

# Templates directory path
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '../templates')

def load_template(template_name):
    """
    Load a template file from the templates directory.
    
    Args:
        template_name (str): The name of the template file
        
    Returns:
        str: The contents of the template file
    
    Raises:
        FileNotFoundError: If the template file does not exist
    """
    template_path = os.path.join(TEMPLATES_DIR, template_name)
    
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file not found: {template_path}")
    
    with open(template_path, 'r') as f:
        return f.read()

def fill_template(template_content, context_data):
    """
    Fill a template with context data using Python's str.format().
    
    Args:
        template_content (str): The template content with {placeholders}
        context_data (dict): Dictionary of values to fill the placeholders
        
    Returns:
        str: The filled template
    """
    try:
        # Use format_map to handle missing keys gracefully
        filled_template = template_content.format_map(SafeDict(context_data))
        return filled_template
    except Exception as e:
        # If there are formatting errors, return a friendly message
        missing_keys = []
        for line in template_content.split('\n'):
            for placeholder in extract_placeholders(line):
                if placeholder not in context_data:
                    missing_keys.append(placeholder)
        
        if missing_keys:
            error_msg = f"Template formatting error: Missing keys: {', '.join(missing_keys)}"
        else:
            error_msg = f"Template formatting error: {str(e)}"
        
        return f"{error_msg}\n\nOriginal template:\n{template_content}"

def render_template(template_name, context_data):
    """
    Load a template and fill it with context data.
    
    Args:
        template_name (str): The name of the template file
        context_data (dict): Dictionary of values to fill the placeholders
        
    Returns:
        str: The filled template
    """
    try:
        template_content = load_template(template_name)
        return fill_template(template_content, context_data)
    except FileNotFoundError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error rendering template: {str(e)}"

def extract_placeholders(text):
    """Extract placeholder names from a template string."""
    placeholders = []
    in_placeholder = False
    current_placeholder = ""
    
    for char in text:
        if char == '{' and not in_placeholder:
            in_placeholder = True
            current_placeholder = ""
        elif char == '}' and in_placeholder:
            in_placeholder = False
            placeholders.append(current_placeholder)
        elif in_placeholder:
            current_placeholder += char
    
    return placeholders

class SafeDict(dict):
    """A dictionary that returns a friendly message for missing keys in format_map()."""
    def __missing__(self, key):
        return f"[MISSING: {key}]"


# For testing
if __name__ == "__main__":
    # Test with a simple template and context
    test_template = "salary_query.txt"
    test_context = {
        "user_name": "John Doe",
        "monthly_income": 75000,
        "annual_income": 900000,
        "salary_transactions": "- Date: 2023-03-01, Amount: ₹75000 (credit), Description: SALARY CREDIT\n- Date: 2023-02-01, Amount: ₹75000 (credit), Description: SALARY CREDIT"
    }
    
    filled_template = render_template(test_template, test_context)
    print("Filled template:")
    print(filled_template)
    
    # Test with missing keys
    test_context_missing = {
        "user_name": "John Doe",
        # Missing other keys
    }
    
    filled_template_missing = render_template(test_template, test_context_missing)
    print("\nFilled template with missing keys:")
    print(filled_template_missing)
