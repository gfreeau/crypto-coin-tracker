from coingecko import fetch_coin_list
from colorama import Fore, Style, init
from typing import List, Dict

init(autoreset=True)  # Ensures that colorama styles reset after each print

def search_coins(symbol: str, coin_dict: Dict[str, Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Searches through the coin dictionary to find all coins whose symbol matches the given symbol.
    
    Parameters:
        symbol (str): The symbol to search for.
        coin_dict (dict): The dictionary of coins where each key is a coin ID and
                          each value is another dict with 'symbol' and 'name'.
    
    Returns:
        list of dict: A list of dictionaries for each coin that matches the symbol.
    """
    # Convert the input symbol to lowercase to make the search case-insensitive
    symbol = symbol.lower()
    # Iterate over all coins in the dictionary and select those whose symbol matches the input symbol
    return [{'id': coin_id, 'symbol': coin['symbol'], 'name': coin['name']}
            for coin_id, coin in coin_dict.items() if coin['symbol'].lower() == symbol]

def get_coin_info(coin):
    """Generate and print information for a single coin."""
    coin_id = coin['id']
    coin_link = f"https://www.coingecko.com/en/coins/{coin_id}"
    return f"{coin['name']} (Symbol: {coin['symbol'].upper()}, ID: {Fore.GREEN}{coin_id}{Style.RESET_ALL}, Link: {coin_link})"

def main():
    coin_list = fetch_coin_list()
    symbol = input("Enter the cryptocurrency symbol you are looking for: ").strip()
    matching_coins = search_coins(symbol, coin_list)
    
    if not matching_coins:
        print("No matching cryptocurrencies found.")
        return
    
    if len(matching_coins) == 1:
        coin_info = get_coin_info(matching_coins[0])
        print(f"Only one cryptocurrency found: {coin_info}")
        print("Please record this ID for use in your config files.")
    else:
        print("Multiple cryptocurrencies found. Please refer to the following list to identify the correct one and record the ID for use in your config files.")
        print(Fore.RED + "Warning:" + Style.RESET_ALL + " Be cautious of meme or scam coins that might use the same symbol as legitimate coins. Click on the provided link to verify the correct coin.")
        for index, coin in enumerate(matching_coins):
            coin_info = get_coin_info(coin)
            print(f"{index + 1}. {coin_info}")

if __name__ == "__main__":
    main()
