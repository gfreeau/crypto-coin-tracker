import json
import sys
import os
from argparse import ArgumentParser
from prettytable import PrettyTable
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import coingecko
from jsonschema import validate, ValidationError
from utils import validate_currency_prices, format_currency, get_currency_symbol

config_schema = {
    "type": "object",
    "properties": {
        "showOptimalOnly": {
            "type": "boolean",
            "description": "If this is true only coins that are below the target price will be shown in the table otherwise all of them will show."
        },
        "purchases": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "coinId": {"type": "string", "minLength": 1},
                    "buyUnits": {"type": "number", "exclusiveMinimum": 0},
                    "price": {"type": "number", "exclusiveMinimum": 0},
                    "currency": {"type": "string", "minLength": 3}
                },
                "required": ["coinId", "buyUnits", "price", "currency"]
            }
        },
        "sendEmail": {"type": "boolean"},
        "email": {"type": "string", "format": "email"},
        "smtp": {
            "type": "object",
            "properties": {
                "host": {"type": "string", "minLength": 1},
                "port": {"type": "integer", "minimum": 1, "exclusiveMaximum": 65536},
                "username": {"type": "string"},
                "password": {"type": "string"}
            },
            "required": ["host", "port", "username", "password"]
        }
    },
    "required": ["showOptimalOnly", "purchases", "sendEmail", "email", "smtp"]
}

def parse_args():
    parser = ArgumentParser(description="Optimal purchase calculator and alert system.")
    parser.add_argument('config_file', type=str, help="Path to the configuration JSON file. See config/optimalpurchase.json.example for an example.")
    return parser.parse_args()

def send_email(config, message):
    msg = MIMEMultipart()
    msg['From'] = config['email']
    msg['To'] = config['email']
    msg['Subject'] = "Optimal Purchase Alert"
    msg.attach(MIMEText(message, 'plain'))
    try:
        with smtplib.SMTP(config['smtp']['host'], config['smtp']['port']) as server:
            server.starttls()
            server.login(config['smtp']['username'], config['smtp']['password'])
            server.send_message(msg)
            print("Email sent successfully.")
    except Exception as e:
        sys.exit(f"Failed to send email: {e}")

def main():
    args = parse_args()
    if not os.path.exists(args.config_file):
        sys.exit(f"Error: Config file does not exist. Usage: {os.path.basename(__file__)} configfilepath")

    with open(args.config_file, 'r') as file:
        try:
            config = json.load(file)
        except json.JSONDecodeError:
            sys.exit("Error: Failed to decode JSON from the provided file.")

    try:
        validate(instance=config, schema=config_schema)
    except ValidationError as e:
        error_path = " -> ".join(map(str, e.path))
        sys.exit(f"Error: Configuration file validation failed at '{error_path}': {e.message}. Look at the sample configs to see how to structure the configuration.")

    coin_ids = [coin['coinId'] for coin in config['purchases']]
    currencies = list(set(coin['currency'] for coin in config['purchases']))

    try:
        prices = coingecko.fetch_price_data(coin_ids, currencies)
        validate_currency_prices(prices, currencies)
    except Exception as e:
        sys.exit(str(e))

    table = PrettyTable()
    table.field_names = ["Buy", "Current Price", "Target Price", "Unit Price", "Target Unit Price", "Price Diff"]

    alert = False

    for purchase in config['purchases']:
        currency = purchase['currency']
        coin_id = purchase['coinId']
        current_price = prices[coin_id][currency.lower()]
        units = purchase['buyUnits']
        current_total_purchase_price = current_price * units
        target_price = purchase['price']

        if target_price > current_total_purchase_price:
            alert = True
        elif config['showOptimalOnly']:
            continue

        unit_price = current_price
        target_unit_price = target_price / units
        price_diff = (unit_price - target_unit_price) / target_unit_price * 100
        currency_symbol = get_currency_symbol(currency)

        table.add_row([
            f"{units} {coingecko.get_coin_symbol(coin_id)}",
            f"{currency_symbol}{format_currency(current_total_purchase_price)} {purchase['currency']}",
            f"{currency_symbol}{format_currency(target_price)} {purchase['currency']}",
            f"{currency_symbol}{format_currency(unit_price)} {purchase['currency']}",
            f"{currency_symbol}{format_currency(target_unit_price)} {purchase['currency']}",
            f"{price_diff:.2f}%"
        ])

    if table.rows:
        print(table)
        if alert and config['sendEmail']:
            send_email(config, table.get_string())

if __name__ == "__main__":
    main()
