import json
import sys
import argparse
from prettytable import PrettyTable
import os
import coingecko
from utils import merge_configurations, validate_currency_prices, get_currency_symbol, format_currency
from jsonschema import validate, ValidationError

config_schema = {
    "type": "object",
    "properties": {
        "investmentAmount": {
            "type": "number",
            "minimum": 0
        },
        "defaultCurrency": {
            "type": "string",
            "minLength": 3
        },
        "currencies": {
            "type": "array",
            "items": {
                "type": "string",
                "minLength": 3
            }
        },
        "holdings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "coinId": {
                        "type": "string",
                        "minLength": 1
                    },
                    "units": {
                        "type": "number",
                        "exclusiveMinimum": 0
                    }
                },
                "required": ["coinId", "units"]
            }
        }
    },
    "required": ["investmentAmount", "defaultCurrency", "currencies", "holdings"]
}


def parse_args():
    parser = argparse.ArgumentParser(description="Display cryptocurrency portfolio based on CoinGecko data.")
    parser.add_argument('config_file', type=str, help='The JSON file containing the portfolio data. See config/portfolio.json.example for an example.')
    return parser.parse_args()

def main():
    args = parse_args()
    portfolio_file = args.config_file

    if not os.path.exists(portfolio_file):
        sys.exit(f"Error: The file '{portfolio_file}' does not exist.")

    # Default configuration with zero or default values
    default_config = {
        'investmentAmount': 0,
        'defaultCurrency': 'AUD',
        'currencies': [],
        'holdings': []
    }

    try:
        with open(portfolio_file, 'r') as file:
            portfolio = json.load(file)
            portfolio = merge_configurations(default_config, portfolio)
    except json.JSONDecodeError:
        sys.exit("Error: Failed to decode JSON from the provided file.")

    try:
        validate(instance=portfolio, schema=config_schema)
    except ValidationError as e:
        error_path = " -> ".join(map(str, e.path))
        sys.exit(f"Error: Configuration file validation failed at '{error_path}': {e.message}. Look at the sample configs to see how to structure the configuration.")

    if not portfolio['holdings']:
        sys.exit("Error: The portfolio holdings are empty in the supplied config.")

    default_currency = portfolio.get('defaultCurrency', 'AUD').upper()
    additional_currencies = [currency.upper() for currency in portfolio.get('currencies', []) if currency.upper() != default_currency]
    supported_currencies = [default_currency] + additional_currencies
    
    ids = [coin['coinId'] for coin in portfolio['holdings']]

    try:
        prices = coingecko.fetch_price_data(ids, supported_currencies)
        validate_currency_prices(prices, supported_currencies)
    except Exception as e:
        sys.exit(str(e))

    total_value = {currency: 0 for currency in supported_currencies}
    total_24h_change = 0

    for holding in portfolio['holdings']:
        id = holding['coinId']
        units = holding['units']
        currency_value = prices[id][default_currency.lower()] * units
        total_value[default_currency] += currency_value
        change_24h_currency = prices[id][f"{default_currency.lower()}_24h_change"]
        total_24h_change += currency_value * (change_24h_currency / 100)

    detail_table = PrettyTable()
    detail_table.field_names = ["Name", "Units", "Alloc", f"Total ({default_currency})", f"Price ({default_currency})", f"24H % ({default_currency})"]

    for holding in portfolio['holdings']:
        id = holding['coinId']
        units = holding['units']
        currency_value = prices[id][default_currency.lower()] * units
        price_currency = prices[id][default_currency.lower()]
        change_24h_currency = prices[id][f"{default_currency.lower()}_24h_change"]
        symbol = get_currency_symbol(default_currency)

        detail_table.add_row([
            coingecko.get_coin_symbol(id), units, f"{(currency_value / total_value[default_currency] * 100):.2f}%", f"{symbol}{format_currency(currency_value)}", f"{symbol}{format_currency(price_currency)}", f"{change_24h_currency:.2f}%"
        ])

    summary_table = PrettyTable()
    field_names = [f"Return % ({default_currency})", f"Total ({default_currency})", f"Return ({default_currency})", f"24H Diff ({default_currency})", f"24H % ({default_currency})"]
    for currency in additional_currencies:
        field_names.append(f"Total ({currency})")
    summary_table.field_names = field_names
    
    investment_return = total_value[default_currency] - portfolio.get('investmentAmount', 0)
    return_percent = (investment_return / portfolio.get('investmentAmount', 1)) * 100
    change_24h_percent = (total_24h_change / total_value[default_currency]) * 100 if total_value[default_currency] != 0 else 0
    
    row = [f"{return_percent:.2f}%", f"{symbol}{format_currency(total_value[default_currency])}", f"{symbol}{format_currency(investment_return)}", f"{symbol}{total_24h_change:,.2f}", f"{change_24h_percent:.2f}%"]
    for currency in additional_currencies:
        symbol = get_currency_symbol(currency)
        total_currency_value = sum(prices[coin['coinId']][currency.lower()] * coin['units'] for coin in portfolio['holdings'])
        row.append(f"{symbol}{format_currency(total_currency_value)}")
    
    summary_table.add_row(row)
    
    print(summary_table)
    print(detail_table)

if __name__ == "__main__":
    main()
