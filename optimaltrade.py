import json
import sys
import os
from argparse import ArgumentParser
from prettytable import PrettyTable
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import coingecko
from utils import validate_currency_prices, format_currency
from jsonschema import validate, ValidationError

config_schema = {
    "type": "object",
    "properties": {
        "showOptimalOnly": {
            "type": "boolean",
            "description": "If this is true only coins that are below the target price will be shown in the table otherwise all of them will show."
        },
        "currency": {
            "type": "string",
            "minLength": 3
        },
        "trades": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "sellCoinId": {
                        "type": "string",
                        "minLength": 1
                    },
                    "sellUnits": {
                        "type": "number",
                        "exclusiveMinimum": 0
                    },
                    "buyCoinId": {
                        "type": "string",
                        "minLength": 1 
                    },
                    "buyUnits": {
                        "type": "number",
                        "exclusiveMinimum": 0
                    }
                },
                "required": ["sellCoinId", "sellUnits", "buyCoinId", "buyUnits"]
            }
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
                    "exclusiveMaximum": 65536
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
    "required": ["showOptimalOnly", "currency", "trades", "sendEmail", "email", "smtp"]
}

def parse_args():
    parser = ArgumentParser(description="Optimal trade calculator and alert system.")
    parser.add_argument('config_file', type=str, help="Path to the configuration JSON file. See config/optimaltrade.json.example for an example.")
    return parser.parse_args()

def send_email(config, message):
    msg = MIMEMultipart()
    msg['From'] = config['email']
    msg['To'] = config['email']
    msg['Subject'] = "Optimal Trade Alert"
    msg.attach(MIMEText(message, 'plain'))
    try:
        with smtplib.SMTP(config['smtp']['host'], config['smtp']['port']) as server:
            server.starttls()
            server.login(config['smtp']['username'], config['smtp']['password'])
            server.send_message(msg)
            sys.exit("Email sent successfully.")
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

    currency = config.get('currency', 'aud').lower()

    coin_ids = {trade['sellCoinId'] for trade in config['trades']} | {trade['buyCoinId'] for trade in config['trades']}
    
    try:
        prices = coingecko.fetch_price_data(list(coin_ids), [currency, 'btc'])
        validate_currency_prices(prices, [currency, 'btc'])
    except Exception as e:
        print(str(e))
        sys.exit(1)

    alert = False
    table = PrettyTable()
    table.field_names = ["Sell", "Target Buy", "Current Buy", "Diff", "Current Sell Price", "Target Sell Price", "Current Buy Price", "Target Buy Price"]
    
    for trade in config['trades']:
        sell_symbol = coingecko.get_coin_symbol(trade['sellCoinId'])
        buy_symbol = coingecko.get_coin_symbol(trade['buyCoinId'])
        sell_coin = prices.get(trade['sellCoinId'])
        buy_coin = prices.get(trade['buyCoinId'])

        if not sell_coin or not buy_coin or trade['sellUnits'] <= 0:
            continue

        price_ratio = sell_coin['btc'] / buy_coin['btc']
        current_buy = trade['sellUnits'] * price_ratio

        if current_buy > trade['buyUnits']:
            alert = True
        elif config['showOptimalOnly']:
            continue

        target_sell_price = trade['buyUnits'] / trade['sellUnits']
        target_buy_price = 1 / target_sell_price

        target_sell_price_currency = buy_coin[currency] * target_sell_price
        target_buy_price_currency = sell_coin[currency] * target_buy_price

        current_buy_price_currency = buy_coin[currency]

        diff = ((current_buy - trade['buyUnits']) / trade['buyUnits']) * 100

        table.add_row([
            f"{trade['sellUnits']:.2f} {sell_symbol}",
            f"{trade['buyUnits']:.2f} {buy_symbol}",
            f"{current_buy:.8f} {buy_symbol}",
            f"{diff:.2f}%",
            f"{sell_symbol}: {format_currency(sell_coin[currency])}",
            f"{sell_symbol}: {format_currency(target_sell_price_currency)}",
            f"{buy_symbol}: {format_currency(current_buy_price_currency)}",
            f"{buy_symbol}: {format_currency(target_buy_price_currency)}",
        ])

    if table.rows:
        print(table)
        if alert and config['sendEmail']:
            send_email(config, table.get_string())

if __name__ == "__main__":
    main()
