import requests
import json
import os
import time
from typing import List, Dict

# Define cache settings for coin list data
CACHE_FILENAME = os.path.join(os.path.dirname(__file__), 'cache', 'coin_list_cache.json')
CACHE_EXPIRY = 604800  # Cache expiry time in seconds (1 week)

def fetch_data_from_api(url: str):
    """
    Fetches data from the specified API URL. Handles response checking and error handling.

    Parameters:
        url (str): The URL to send the GET request to.

    Returns:
        data (dict): Parsed JSON data from the API response.

    Raises:
        ValueError: If no data is returned from the API.
        requests.HTTPError: If there's a problem with the HTTP response.
        ConnectionError: If there's a problem connecting to the API.
        Exception: If an unexpected error occurs.
    """
    try:
        response = requests.get(url)
        # Check if the response was successful
        if response.status_code == 200:
            data = response.json()
            if not data:
                raise ValueError("No data returned from API")
            return data
        else:
            raise requests.HTTPError(f"HTTP Error getting data from API: {response.status_code} - {response.reason}")
    except requests.RequestException as e:
        raise ConnectionError(f"Failed to connect to API: {e}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred getting data from API: {e}")


def fetch_coin_list():
    """
    Fetches the list of all coins from the CoinGecko API, caches it,
    and converts it to a dictionary for quick lookups.
    Each coin's ID maps to another dictionary containing the 'symbol' and 'name'.
    """
    if not os.path.exists(os.path.dirname(CACHE_FILENAME)):
        os.makedirs(os.path.dirname(CACHE_FILENAME))

    if os.path.exists(CACHE_FILENAME):
        with open(CACHE_FILENAME, 'r') as file:
            cached_data = json.load(file)
            # Check if the cache has expired
            if time.time() - cached_data['timestamp'] < CACHE_EXPIRY:
                return cached_data['data']  # Return cached data if it's still valid

    # If no cache exists or cache is expired, fetch new data from API
    url = "https://api.coingecko.com/api/v3/coins/list"
    coin_list = fetch_data_from_api(url)
    # Convert list to a dictionary with id as key and another dict for symbol and name as value for faster lookups
    coin_dict = {coin['id']: coin for coin in coin_list}

    # Save the fetched data to cache
    with open(CACHE_FILENAME, 'w') as file:
        json.dump({'data': coin_dict, 'timestamp': time.time()}, file)

    return coin_dict


def fetch_price_data(ids: List[str], currencies: List[str] = ['aud', 'usd', 'btc', 'eth']) -> Dict[str, Dict[str, float]]:
    """
    Fetches cryptocurrency prices from the CoinGecko API for given IDs.
    
    Args:
    ids (list of str): List of cryptocurrency IDs as recognized by CoinGecko.
    currencies (list of str): List of currency IDs to fetch prices for.

    Returns:
    dict: A dictionary with cryptocurrency prices.

    Raises:
    ValueError: If the API response is empty or not in expected format.
    HTTPError: If the API response status is not 200.
    ConnectionError: If there is a network problem (e.g., DNS failure, refused connection, etc).
    Exception: For other unforeseen errors.
    """
    # Remove duplicates and format inputs
    ids_set = set(item.lower() for item in ids)
    currencies_set = set(item.lower() for item in currencies)

    ids_str = ','.join(ids_set)
    currencies_str = ','.join(currencies_set)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_str}&vs_currencies={currencies_str}&include_market_cap=false&include_24hr_vol=false&include_24hr_change=true"
    data = fetch_data_from_api(url)

    if len(ids_set) != len(data):
        raise ValueError("Not all coin IDs were found in the API response. Check that all coin IDs are valid. Run coinsearch.py to find valid IDs.")

    return data

def get_coin_info(coin_id, info='all'):
    """
    Retrieves information for a given cryptocurrency ID from the cached coin dictionary.
    By default, it retrieves the symbol, but can also retrieve the name or both.

    Parameters:
        coin_id (str): The CoinGecko ID for which to find the information.
        info (str): The type of information to retrieve ('symbol', 'name', or 'all').

    Returns:
        str or dict: The requested information, or None if no matching ID is found.
    """
    coin_dict = fetch_coin_list()
    if coin_id in coin_dict:
        if info == 'all':
            return coin_dict[coin_id]
        return coin_dict[coin_id][info]
    return None # Return None if no coin matches the given ID

def get_coin_symbol(coin_id):
    """
    Retrieves the symbol for a given cryptocurrency ID from the cached coin list.
    
    Parameters:
        coin_id (str): The CoinGecko ID for which to find the corresponding symbol.
        
    Returns:
        str: The symbol associated with the given ID, or None if no matching ID is found.
    """
    symbol = get_coin_info(coin_id, 'symbol')
    if symbol is not None:
        symbol = symbol.upper()
    return symbol
