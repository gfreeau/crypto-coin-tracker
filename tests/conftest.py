import pytest
import os
from io import StringIO
from unittest.mock import patch, mock_open
import sys

from mocks import fetch_price_data, get_coin_symbol

# add parent directory to import path so we can import the main functions of each script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def base_setup(mocker):
    def do_setup(config_name):
        config_file = os.path.join(os.path.dirname(__file__), 'config', config_name)

        # Mock sys.argv to simulate command line input
        mocker.patch('sys.argv', ['script_name', config_file])

        # Mock stdout to capture print statements
        mock_stdout = StringIO()
        mocker.patch('sys.stdout', mock_stdout)

        # Mock external calls
        mocker.patch('coingecko.fetch_price_data', return_value=fetch_price_data())
        mocker.patch('coingecko.get_coin_symbol', side_effect=get_coin_symbol)

        return mock_stdout
    return do_setup

@pytest.fixture
def check_configuration_errors():
    def do_check(main_func, expected_error_message):
        with patch('sys.exit') as mock_exit:
            mock_exit.side_effect = SystemExit
            with pytest.raises(SystemExit):
                main_func()
            mock_exit.assert_called_once()
            assert expected_error_message in str(mock_exit.call_args[0][0])
    return do_check
