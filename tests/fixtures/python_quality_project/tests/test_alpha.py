from sample_pkg.alpha import AlphaFormatter, calculate_alpha


def test_calculate_alpha():
    assert calculate_alpha("1") == 1


def test_format_alpha():
    assert AlphaFormatter().format_alpha("1") == "alpha=1"
