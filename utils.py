import sys
from typing import List

def merge_configurations(default_config: dict, user_config: dict) -> dict:
    merged_config = default_config.copy()
    merged_config.update(user_config)
    return merged_config

def validate_currency_prices(prices: List, supported_currencies: List):
    if not prices:
        sys.exit("Error: No prices found for the specified coins.")

    first_price = list(prices.values())[0]
    for currency in supported_currencies:
        if currency.lower() not in first_price:
            sys.exit(f"Error: No price found for currency '{currency}'.")

def get_currency_symbol(currency: str) -> str:
    symbols = {
        'AUD': '$', 'USD': '$', 'CAD': '$',
        'EUR': '€', 'GBP': '£', 'JPY': '¥'
    }
    return symbols.get(currency.upper(), '')  # Default to empty string if not found

def format_currency(value: float) -> str:
    """
    Formats currency values based on their magnitude:
    - If the value is less than $0.01, it will have 8 decimal places.
    - If the value is less than $1, it will have 4 decimal places.
    - If the value is less than $10,000, it will have 2 decimal places.
    - If the value is $10,000 or more, it will have no decimal places.

    Args:
    value (float): The currency value to format.

    Returns:
    str: Formatted currency string.
    """
    if abs(value) < 0.01:
        return f"{value:.8f}"
    elif abs(value) < 1:
        return f"{value:.4f}"
    else:
        return f"{value:,.2f}"  # Includes comma for thousands separator
