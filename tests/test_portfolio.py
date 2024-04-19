from portfolio import main
import re

def test_main_output(base_setup):
    mock_stdout = base_setup('portfolio_valid.json')
    main()
    output = mock_stdout.getvalue()

    """
    The following is the expected output

    +----------------+-------------+--------------+----------------+-------------+
    | Return % (AUD) | Total (AUD) | Return (AUD) | 24H Diff (AUD) | 24H % (AUD) |
    +----------------+-------------+--------------+----------------+-------------+
    |    550.00%     | $325,000.00 | $275,000.00  |   $32,208.13   |    9.91%    |
    +----------------+-------------+--------------+----------------+-------------+
    +------+-------+--------+-------------+-------------+-------------+
    | Name | Units | Alloc  | Total (AUD) | Price (AUD) | 24H % (AUD) |
    +------+-------+--------+-------------+-------------+-------------+
    | BTC  |   3   | 92.31% | $300,000.00 | $100,000.00 |    10.78%   |
    | ETH  |   5   | 7.69%  |  $25,000.00 |  $5,000.00  |    -0.53%   |
    +------+-------+--------+-------------+-------------+-------------+
    """

    summary_row_pattern = r"\|\s*550\.00%\s*\|\s*\$325,000\.00\s*\|\s*\$275,000\.00\s*\|\s*\$32,208\.13\s*\|\s*9\.91%\s*\|"
    btc_pattern = r"\|\s*BTC\s*\|\s*3\s*\|\s*92\.31%\s*\|\s*\$300,000\.00\s*\|\s*\$100,000\.00\s*\|\s*10\.78%\s*\|"
    eth_pattern = r"\|\s*ETH\s*\|\s*5\s*\|\s*7\.69%\s*\|\s*\$25,000\.00\s*\|\s*\$5,000\.00\s*\|\s*-0\.53%\s*\|"

    assert re.search(summary_row_pattern, output), "Summary row not found or incorrect format"
    assert re.search(btc_pattern, output), "BTC data row not found or incorrect format"
    assert re.search(eth_pattern, output), "ETH data row not found or incorrect format"

def test_empty_config(base_setup, check_configuration_errors):
    base_setup('portfolio_empty.json')
    check_configuration_errors(main, "Error: The portfolio holdings are empty in the supplied config.")

def test_missing_config(base_setup, check_configuration_errors):
    base_setup('portfolio_missing_config.json')
    check_configuration_errors(main, "Error: The portfolio holdings are empty in the supplied config.")

def test_malformed_config(base_setup, check_configuration_errors):
    base_setup('portfolio_malformed.json')
    check_configuration_errors(main, "Should be a number not")
