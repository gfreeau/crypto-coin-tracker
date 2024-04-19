import json
import os
import sys
from argparse import ArgumentParser
import coingecko
from utils import validate_currency_prices, get_currency_symbol, format_currency
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
            },
        },
        "increasePercent": {
            "type": "number",
            "minimum": 1 # A percentage increase of at least 1% is represented by the whole number 1 and not 0.01
        },
        "sendEmail": {
            "type": "boolean"
        },
        "email": {
            "type": "string",
            "format": "email",
            "minLength": 1
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
    "required": ["coins", "sendEmail", "email", "smtp", "increasePercent"]
}

def parse_args():
    parser = ArgumentParser(description="Track if cryptocurrency prices increase by a defined percentage and send alerts.")
    parser.add_argument('config_file', type=str, help="Path to the configuration JSON file. pricealert.json is an example.")
    return parser.parse_args()

def send_email(config, message):
    msg = MIMEMultipart()
    msg['From'] = config['email']
    msg['To'] = config['email']
    msg['Subject'] = "Coin Price Increase Alert"
    msg.attach(MIMEText(message, 'plain'))
    try:
        with smtplib.SMTP(config['smtp']['host'], config['smtp']['port']) as server:
            server.starttls()
            server.login(config['smtp']['username'], config['smtp']['password'])
            server.send_message(msg)
            print("Email sent successfully.")
    except Exception as e:
        sys.exit(f"Failed to send email: {e}")

def main(cache_directory=None):
    if cache_directory is None:
        cache_directory = os.path.join(os.path.dirname(__file__), 'cache')

    cache_filename = os.path.join(cache_directory, 'coin_prices_cache.json')

    args = parse_args()
    config_path = args.config_file

    if not os.path.exists(config_path):
        sys.exit("Error: Config file does not exist.")

    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
    except json.JSONDecodeError:
        sys.exit("Error: Failed to decode JSON from the provided file.")

    try:
        validate(instance=config, schema=config_schema)
    except ValidationError as e:
        error_path = " -> ".join(map(str, e.path))
        sys.exit(f"Error: Configuration file validation failed at '{error_path}': {e.message}. Look at the sample configs to see how to structure the configuration.")

    if not config['coins']:
        sys.exit("Error: No coins specified in the configuration.")

    if not os.path.exists(os.path.dirname(cache_filename)):
        os.makedirs(os.path.dirname(cache_filename))

    if os.path.exists(cache_filename):
        try:
            with open(cache_filename, 'r') as file:
                price_history = json.load(file)
        except json.JSONDecodeError:
            sys.exit("Error: Failed to decode JSON from the price history file.")
    else:
        price_history = {}

    active_keys = {f"{coin['coinId']}-{coin['currency'].lower()}" for coin in config['coins'] if 'coinId' in coin and 'currency' in coin}
    # Remove any keys that are not in the active set
    price_history = {key: value for key, value in price_history.items() if key in active_keys}

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
        price_key = f"{coin_id}-{currency}"
        current_price = prices.get(coin_id, {}).get(currency, 0)
        if current_price == 0:
            sys.exit(f"Error: No price data for {coin_id} in {currency.upper()}.")
        alert_price = price_history.get(price_key, 0)

        if current_price > alert_price:
            currency_symbol = get_currency_symbol(currency)
            output += f"{coingecko.get_coin_symbol(coin_id)} is now {currency.upper()} {currency_symbol}{format_currency(current_price)}\n"
            price_history[price_key] = current_price + (current_price * (config['increasePercent'] / 100))
            alert = True

    if alert:
        print(output)
        try:
            with open(cache_filename, 'w') as file:
                json.dump(price_history, file, indent=4)
        except Exception as e:
            sys.exit(f"Failed to write price history: {e}")

        if config['sendEmail']:
            send_email(config, output)

if __name__ == "__main__":
    main()
