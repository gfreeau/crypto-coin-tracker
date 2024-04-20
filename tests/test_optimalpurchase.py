from optimalpurchase import main
import re

btc_pattern = r"\|\s*1\s*BTC\s*\|\s*\$100,000\.00\s*AUD\s*\|\s*\$90,000\.00\s*AUD\s*\|\s*\$100,000\.00\s*AUD\s*\|\s*\$90,000\.00\s*AUD\s*\|\s*11\.11%\s*\|"
eth_pattern = r"\|\s*3\s*ETH\s*\|\s*\$15,000\.00\s*AUD\s*\|\s*\$18,000\.00\s*AUD\s*\|\s*\$5,000\.00\s*AUD\s*\|\s*\$6,000\.00\s*AUD\s*\|\s*-16\.67%\s*\|"

def test_all_purchases_show(base_setup):
    mock_stdout = base_setup('optimalpurchase_show_all.json')
    main()
    output = mock_stdout.getvalue()

    """
    The following is the expected output

    +-------+-----------------+----------------+-----------------+-------------------+------------+
    |  Buy  |  Current Price  |  Target Price  |    Unit Price   | Target Unit Price | Price Diff |
    +-------+-----------------+----------------+-----------------+-------------------+------------+
    | 1 BTC | $100,000.00 AUD | $90,000.00 AUD | $100,000.00 AUD |   $90,000.00 AUD  |   11.11%   |
    | 3 ETH |  $15,000.00 AUD | $18,000.00 AUD |  $5,000.00 AUD  |   $6,000.00 AUD   |  -16.67%   |
    +-------+-----------------+----------------+-----------------+-------------------+------------+
    """

    assert re.search(btc_pattern, output), "BTC data row not found or incorrect format"
    assert re.search(eth_pattern, output), "ETH data row not found or incorrect format"

def test_only_optimal_purchases_show(base_setup, tmp_path):
    mock_stdout = base_setup('optimalpurchase_show_optimal.json')
    main()
    output = mock_stdout.getvalue()

    assert not re.search(btc_pattern, output), "BTC data row found when it should be hidden as target price is less than the current price"
    assert re.search(eth_pattern, output), "ETH data row not found or incorrect format"