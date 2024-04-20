from optimaltrade import main
import re

btc_pattern = r"\|\s*1\.00\s*BTC\s*\|\s*20\.00\s*ETH\s*\|\s*20\.92272130\s*ETH\s*\|\s*4\.61%\s*\|\s*BTC:\s*100,000\.00\s*\|\s*BTC:\s*100,000\.00\s*\|\s*ETH:\s*5,000\.00\s*\|\s*ETH:\s*5,000\.00\s*\|"
eth_pattern = r"\|\s*2\.00\s*ETH\s*\|\s*50000\.00\s*XRP\s*\|\s*11743\.22604423\s*XRP\s*\|\s*-76\.51%\s*\|\s*ETH:\s*5,000\.00\s*\|\s*ETH:\s*18,750\.00\s*\|\s*XRP:\s*0\.7500\s*\|\s*XRP:\s*0\.2000\s*\|"

def test_all_trades_show(base_setup):
    mock_stdout = base_setup('optimaltrade_show_all.json')
    main()
    output = mock_stdout.getvalue()

    """
    The following is the expected output

    +----------+--------------+--------------------+---------+--------------------+-------------------+-------------------+------------------+
    |   Sell   |  Target Buy  |    Current Buy     |   Diff  | Current Sell Price | Target Sell Price | Current Buy Price | Target Buy Price |
    +----------+--------------+--------------------+---------+--------------------+-------------------+-------------------+------------------+
    | 1.00 BTC |  20.00 ETH   |  20.92272130 ETH   |  4.61%  |  BTC: 100,000.00   |  BTC: 100,000.00  |   ETH: 5,000.00   |  ETH: 5,000.00   |
    | 2.00 ETH | 50000.00 XRP | 11743.22604423 XRP | -76.51% |   ETH: 5,000.00    |   ETH: 18,750.00  |    XRP: 0.7500    |   XRP: 0.2000    |
    +----------+--------------+--------------------+---------+--------------------+-------------------+-------------------+------------------+
    """

    assert re.search(btc_pattern, output), "BTC data row not found or incorrect format"
    assert re.search(eth_pattern, output), "ETH data row not found or incorrect format"

def test_only_optimal_trades_show(base_setup, tmp_path):
    mock_stdout = base_setup('optimaltrade_show_optimal.json')
    main()
    output = mock_stdout.getvalue()

    assert re.search(btc_pattern, output), "BTC data row not found or incorrect format"
    assert not re.search(eth_pattern, output), "ETH data found when it should be hidden as target price is less than the current price"