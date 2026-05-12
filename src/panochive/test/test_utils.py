import pytest

from panochive.utils import format_duration


@pytest.mark.parametrize(
    "seconds, expected",
    [
        (0.0, "0.00s"),
        (33.33, "33.33s"),
        (30.0, "30.00s"),
        (60.0, "1.00m"),
        (75.0, "1.25m"),
        (90.0, "1.50m"),
        (3600.0, "1h 0.00m"),
        (3665.0, "1h 1.08m"),
        (5430.0, "1h 30.50m"),
    ],
)
def test_format_duration(seconds, expected):
    assert format_duration(seconds) == expected
