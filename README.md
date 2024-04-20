
# Cryptocurrency Tools Suite

This suite of Python applications provides various tools to track and manage your cryptocurrency investments, send e-mail alerts based on price changes, calculate potential purchases in fiat, send e-mail alerts when optimal trades arise, and search for coin details. All tools fetch the latest cryptocurrency data from CoinGecko.

This is an improved version of https://github.com/gfreeau/coin-tracker which was written in go.

I wrote this for personal interest to have a local tool that doesn't require using a third party service to monitor changes in crypto (except the data component from CoinGecko)

## General Requirements

Ensure you have Python and the necessary packages installed. You can install the required packages using the provided `requirements.txt` file:

```bash
pip install -r requirements.txt
```

I recommend using venv. You can create it by opening a terminal in the root of this project and running:

```bash
python3 -m venv venv
source venv/bin/activate
```

I am using Python 3.10

### Contents of `requirements.txt`

The `requirements.txt` file includes the following Python packages:

```
requests
prettytable
colorama
jsonschema
pytest
pytest-mock
```

## Scripts Overview

### 1. Portfolio Tracker (`portfolio.py`)

**Description**: Tracks the user's cryptocurrency portfolio, displaying a detailed summary of investments and their current market values.

**Usage**:
```bash
python portfolio.py config/portfolio.json
```

**Sample Config**: `config/portfolio.json.example`

**Note**: You can configure the currencies displayed. The `defaultCurrency` is used for the 24 hour comparisons and is shown for each crypto holding. The other `currencies` config option allows you to show the total portfolio value in whatever currency you like including crypto such as BTC.

**Note**: Use `coinsearch.py` (documented later in this README) to find the correct coin ids for use in all configuration files. This is needed because some coins use the same symbol like BTC (scams, memes etc). We need to make sure we use the unique coin ID in the configuration files, so for example, don't use BTC, use `bitcoin` instead which `coinsearch.py` will tell you if you search for `BTC`.

Here's what it looks like:

```
+----------------+-------------+--------------+----------------+-------------+-------------+-------------+-------------+
| Return % (AUD) | Total (AUD) | Return (AUD) | 24H Diff (AUD) | 24H % (AUD) | Total (USD) | Total (BTC) | Total (ETH) |
+----------------+-------------+--------------+----------------+-------------+-------------+-------------+-------------+
|    1483.75%    | $158,374.92 | $148,374.92  |   $7,174.69    |    4.53%    | $101,618.08 |     1.55    |    32.61    |
+----------------+-------------+--------------+----------------+-------------+-------------+-------------+-------------+
+------+-------+--------+-------------+-------------+-------------+
| Name | Units | Alloc  | Total (AUD) | Price (AUD) | 24H % (AUD) |
+------+-------+--------+-------------+-------------+-------------+
| BTC  |   1   | 64.40% | $101,992.00 | $101,992.00 |    5.38%    |
| ETH  |   10  | 30.66% |  $48,556.50 |  $4,855.65  |    3.13%    |
| XRP  | 10000 | 4.94%  |  $7,826.42  |   $0.7826   |    2.10%    |
+------+-------+--------+-------------+-------------+-------------+
```

Above AUD is the default currency and USD, BTC and ETH are configured as additional currencies to display.

### 2. Price Alert (`pricealert.py`)

**Description**: Monitors specific cryptocurrency prices for a defined percentage increase and sends email alerts if thresholds are exceeded.

**Usage**:
```bash
python pricealert.py config/pricealert.json
```

**Sample Config**: `config/pricealert.json.example`

**Note**: Percentages are represented by whole numbers in the config so 10 means 10%. See `increasePercent`

Here's what it looks like:

```
BTC is now USD $65,267.00
ETH is now USD $3,113.03
XRP is now AUD $0.7813
XRP is now USD $0.5018
BAT is now USD $0.2514
```

After running it will save a cache file. The output text only appears (and alerts by e-mail) if the coin has increased by the configured threshold (10% by default) and e-mail alerts are turned on. If you are running it the first time, it will always alert before caching the threshold. I recomend configuring this as a cron job to run hourly.

A script like the following works for cron:

```bash
#!/bin/bash

# Define the base directory
BASE_DIR="/path/to/crypto-coin-tracker"

# Activate the virtual environment
source "$BASE_DIR/venv/bin/activate"

# Run the Python script with its configuration
python "$BASE_DIR/pricealert.py" "$BASE_DIR/config/pricealert.json"
```

### 3. Fiat Purchase Simulator (`fiatpurchase.py`)

**Description**: Calculates how much cryptocurrency can be purchased with a specified amount of fiat currency.

**Usage**:
```bash
python fiatpurchase.py config/fiatpurchase.json
```

**Sample Config**: `config/fiatpurchase.json.example`

Here's what it looks like:

```
+----------+-----------------+--------+------------+-------------+
| Currency | Currency Amount | Symbol |   Units    |  Unit Price |
+----------+-----------------+--------+------------+-------------+
|   AUD    |   $101,601.00   |  BTC   |   1.0000   | $101,601.00 |
|   AUD    |    $20,000.00   |  XRP   | 25608.1946 |   $0.7810   |
+----------+-----------------+--------+------------+-------------+
```

In the config you can set the `unitAmount` or `currencyAmount` depending your preference. The first row in the table above shows the price for 1 unit of BTC (`unitAmount`). The second row shows the price for 20,000 AUD of XRP (`currencyAmount`). Trading fees are not considered. You can configure any currency you like that CoinGecko supports.

### 4. Optimal Trade Calculator (`optimaltrade.py`)

**Description**: Calculates the optimal trade amounts between different cryptocurrencies and sends email alerts if specified trade conditions are met.

**Usage**:
```bash
python optimaltrade.py config/optimaltrade.json
```

**Sample Config**: `config/optimaltrade.json.example`

Here's what it looks like:

```
+--------------+-------------+-------------------+--------+--------------------+-------------------+-------------------+------------------+
|     Sell     |  Target Buy |    Current Buy    |  Diff  | Current Sell Price | Target Sell Price | Current Buy Price | Target Buy Price |
+--------------+-------------+-------------------+--------+--------------------+-------------------+-------------------+------------------+
|   1.00 BTC   |  20.00 ETH  |  20.95078430 ETH  | 4.75%  |  BTC: 101,541.00   |   BTC: 96,920.60  |   ETH: 4,846.03   |  ETH: 5,077.05   |
| 10000.00 BAT | 4000.00 XRP | 5012.98701299 XRP | 25.32% |    BAT: 0.3923     |    BAT: 0.3126    |    XRP: 0.7815    |   XRP: 0.9808    |
+--------------+-------------+-------------------+--------+--------------------+-------------------+-------------------+------------------+
```

Though it doesn't account for trading fees, this tool shows you how much one crypto is in another, even if a trading pair doesn't exist. It can alert you by e-mail when a specific amount you specify costs equal or less. It shows you how much the price of either crypto needs to move to make the trade optimal per your configuration. I recommend setting this up as a cron job.

### 5. Price Percent Alert (`pricepercentalert.py`)

**Description**: Monitors cryptocurrency price changes by a defined percentage (absolute value change so positive or negative) and sends email alerts if those thresholds are met.

**Usage**:
```bash
python pricepercentalert.py config/pricepercentalert.json
```

**Sample Config**: `config/pricepercentalert.json.example`

This command is very similar to `pricepercent.py` except it can be more noisy as it notifies based on absolute percent change (positive or negative). Just depends on your preference. The default `alertPercent` is 10% change. I recommend setting it up as a cron job.

### 6. Coin Search (`coinsearch.py`)

**Description**: Helps users find CoinGecko IDs for cryptocurrencies by symbol, which are needed for the configuration files of other scripts in this suite.

**Usage**:
```bash
python coinsearch.py
```

**Functionality**: Interactive prompt for coin symbol, displays matching coin details including links for verification as some scam coins use the same symbols as the popular ones.

Here's what it looks like:

```
Enter the cryptocurrency symbol you are looking for: btc
Multiple cryptocurrencies found. Please refer to the following list to identify the correct one and record the ID for use in your config files.
Warning: Be cautious of meme or scam coins that might use the same symbol as legitimate coins. Click on the provided link to verify the correct coin.
1. batcat (Symbol: BTC, ID: batcat, Link: https://www.coingecko.com/en/coins/batcat)
2. Bitcoin (Symbol: BTC, ID: bitcoin, Link: https://www.coingecko.com/en/coins/bitcoin)
3. BlackrockTradingCurrency (Symbol: BTC, ID: blackrocktradingcurrency, Link: https://www.coingecko.com/en/coins/blackrocktradingcurrency)
```

Above is an example why we don't use common symbols like BTC in our config and rely on the ID instead.

## Configuration and Error Handling

Each script requires a JSON configuration file to specify user settings and preferences. Validate these configurations against the provided examples to ensure they match the expected schema, which is crucial for proper script operation.

If a configuration file is missing or improperly formatted, the scripts will terminate and provide an error message detailing the issue.

## Sending Email Alerts

Scripts that send email alerts require SMTP configuration. Ensure that your `config.json` includes the correct SMTP server details and credentials for successful email delivery. See the example config for details. I recommend using an e-mail delivery provider like sendgrid or similar.

## Testing

Tests can be run using the following command:

```bash
pytest tests
```

Ensure you have `pytest` and `pytest-mock` installed as indicated in the `requirements.txt` to run the tests successfully.