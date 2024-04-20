import json
import sys
from argparse import ArgumentParser
import coingecko
from utils import validate_currency_prices, get_currency_symbol, format_currency
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from jsonschema import validate, ValidationError

config_schema = {
    "type": "object",
    "properties": {
        "coins": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "coinId": {
                        "type": "string",
                        "minLength": 1
                    },
                    "currency": {
                        "type": "string",
                        "minLength": 3
                    }
                },
                "required": ["coinId", "currency"]
            }
        },
        "alertPercent": {
            "type": "number",
            "minimum": 1,
        },
        "sendEmail": {
            "type": "boolean"
        },
        "email": {
            "type": "string",
            "format": "email"
        },
        "smtp": {
            "type": "object",
            "properties": {
                "host": {
                    "type": "string",
                    "minLength": 1
                },
                "port": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 65535
                },
                "username": {
                    "type": "string"
                },
                "password": {
                    "type": "string"
                }
            },
            "required": ["host", "port", "username", "password"]
        }
    },
    "required": ["coins", "alertPercent", "sendEmail", "email", "smtp"]
}

def parse_args():
    parser = ArgumentParser(description="Monitor cryptocurrency price changes of a defined percentage and send alerts.")
    parser.add_argument('config_file', type=str, help="Path to the configuration JSON file. See config/pricepercentalert.json.example for an example.")
    return parser.parse_args()

def send_email(config, message):
    msg = MIMEMultipart()
    msg['From'] = config['email']
    msg['To'] = config['email']
    msg['Subject'] = "Coin Percent Change Alert"
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
        sys.exit(f"Error: The file '{args.config_file}' does not exist.")
    
    try:
        with open(args.config_file, 'r') as file:
            config = json.load(file)
    except json.JSONDecodeError:
        sys.exit("Error: Failed to decode JSON from the provided file.")
    
    try:
        validate(instance=config, schema=config_schema)
    except ValidationError as e:
        error_path = " -> ".join(map(str, e.path))
        sys.exit(f"Error: Configuration file validation failed at '{error_path}': {e.message}. Look at the sample configs to see how to structure the configuration.")

    coin_ids = [coin['coinId'] for coin in config['coins']]
    currencies = list(set(coin['currency'] for coin in config['coins']))

    try:
        prices = coingecko.fetch_price_data(coin_ids, currencies)
        validate_currency_prices(prices, currencies)
    except Exception as e:
        sys.exit(str(e))
    
    alert = False
    output = ""

    for coin in config['coins']:
        coin_id = coin['coinId']
        currency = coin['currency'].lower()
        if coin_id in prices and currency + '_24h_change' in prices[coin_id]:
            percent_change = prices[coin_id][currency + '_24h_change']
            if abs(percent_change) >= config['alertPercent']:
                price = prices[coin_id][currency]
                currency_symbol = get_currency_symbol(currency)
                output += f"{coingecko.get_coin_symbol(coin_id)} ({percent_change:.2f}%) is now {currency.upper()} {currency_symbol}{format_currency(price)}\n"
                alert = True
    
    if alert:
        print(output)
        if config['sendEmail']:
            send_email(config, output)

if __name__ == "__main__":
    main()
