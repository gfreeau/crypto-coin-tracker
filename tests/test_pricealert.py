from pricealert import main

def test_main_output(base_setup, tmp_path):
    mock_stdout = base_setup('pricealert_valid.json')

    temp_cache_dir = tmp_path / "cache"
    main(temp_cache_dir)

    assert "BTC is now AUD $100,000.00" in mock_stdout.getvalue()
    
    cache_file = temp_cache_dir / "coin_prices_cache.json"
    assert cache_file.exists(), "Cache file was not created"

def test_empty_config(base_setup, check_configuration_errors):
    base_setup('pricealert_empty.json')
    check_configuration_errors(main, "Configuration file validation failed")

def test_malformed_config(base_setup, check_configuration_errors):
    base_setup('pricealert_malformed.json')
    check_configuration_errors(main, "Configuration file validation failed")