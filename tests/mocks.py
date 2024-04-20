def fetch_price_data():
    return {
        'bitcoin': {"aud": 100000, "aud_24h_change": 10.7802749786426911, "btc": 1},
        'ethereum': {"aud": 5000, "aud_24h_change": -0.5307987877419105, "btc": 0.04779493},
        'ripple': {"aud": 0.75, "aud_24h_change": -1.2319184901901987, "btc": 0.00000814}
    }

def get_coin_symbol(id):
    if id == 'bitcoin':
        return 'BTC'
    elif id == 'ethereum':
        return 'ETH'
    elif id == 'ripple':
        return 'XRP'
    return 'Unknown'