from fiatpurchase import main
import re

def test_main_output(base_setup):
    mock_stdout = base_setup('fiatpurchase_valid.json')
    main()
    output = mock_stdout.getvalue()

    """
    The following is the expected output

    +----------+-----------------+--------+------------+-------------+
    | Currency | Currency Amount | Symbol |   Units    |  Unit Price |
    +----------+-----------------+--------+------------+-------------+
    |   AUD    |   $100,000.00   |  BTC   |   1.0000   | $100,000.00 |
    |   AUD    |    $10,000.00   |  XRP   | 13333.3333 |   $0.7500   |
    +----------+-----------------+--------+------------+-------------+
    """

    first_row_pattern = r"\|\s*AUD\s*\|\s*\$100,000.00\s*\|\s*BTC\s*\|\s*1.0000\s*\|\s*\$100,000.00\s*\|"
    second_row_pattern = r"\|\s*AUD\s*\|\s*\$10,000.00\s*\|\s*XRP\s*\|\s*13333.3333\s*\|\s*\$0.7500\s*\|"   
    
    assert re.search(first_row_pattern, output), "Expected first row not found in the output"
    assert re.search(second_row_pattern, output), "Expected second row not found in the output"

def test_empty_config(base_setup, check_configuration_errors):
    base_setup('fiatpurchase_empty.json')
    check_configuration_errors(main, "No purchases found")
