import json
import os
import sys
import argparse
from prettytable import PrettyTable
import coingecko
from utils import merge_configurations, get_currency_symbol, format_currency

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Shows how much crypto can be purchased for an equivalent fiat amount.")
    parser.add_argument("config_file", help="Path to the configuration JSON file. fiatpurchase.json is an example.")
    return parser.parse_args()

def main():
    args = parse_arguments()
    config_path = args.config_file

    if not os.path.exists(config_path):
        sys.exit(f"Error: The file '{config_path}' does not exist.")

    default_config = {
        'purchases': []
    }

    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
            config = merge_configurations(default_config, config)
    except Exception as e:
        print(f"Config file error: {str(e)}")
        sys.exit(1)

    if not config['purchases']:
        sys.exit("Error: No purchases found in the configuration.")

    # Gather all exchange coin IDs and ensure they are unique
    coin_ids = list(set(p['coinId'] for p in config['purchases']))

    # Extract unique currencies from the configuration
    currencies = list(set(p['currency'] for p in config['purchases']))

    try:
        prices = coingecko.fetch_price_data(coin_ids, currencies)
    except Exception as e:
        print(str(e))
        sys.exit(1)

    table = PrettyTable()
    table.field_names = ["Currency", "Currency Amount", "Symbol", "Units", "Unit Price"]

    for purchase in config['purchases']:
        currency = purchase['currency'].lower()
        coin_data = prices.get(purchase['coinId'], {})
        coin_price = coin_data.get(currency, 0)

        if coin_price == 0:
            continue

        currency_symbol = get_currency_symbol(currency)

        units = int(purchase.get('unitAmount', 0))
        currency_amount = int(purchase.get('currencyAmount', 0))

        if units > 0:
            currency_amount = units * coin_price
        else:
            units = currency_amount / coin_price

        table.add_row([
            currency.upper(),
            f"{currency_symbol}{format_currency(currency_amount)}",
            coingecko.get_coin_symbol(purchase['coinId']),
            f"{units:.4f}",
            f"{currency_symbol}{format_currency(coin_price)}"
        ])

    print(table)

if __name__ == "__main__":
    main()
