import pytest

from dinero import Dinero
from dinero.currencies import USD, EUR, CLP, JPY
from dinero.exceptions import InvalidOperationError
from dinero.tools import (
    calculate_vat,
    calculate_percentage,
    calculate_simple_interest,
    calculate_compound_interest,
    calculate_markup,
)


@pytest.mark.parametrize(
    "amount, vat_rate, expected_vat_amount",
    [
        (Dinero.from_major(100, USD), 7.25, Dinero.from_major("6.76", USD)),
        (Dinero.from_major(50, EUR), 21, Dinero.from_major("8.68", EUR)),
        (Dinero.from_major(500, CLP), 19, Dinero.from_major("80", CLP)),
        (100, 7.25, InvalidOperationError),
        (Dinero.from_major(100, USD), "7.25", TypeError),
        (Dinero.from_major(100, USD), -7.25, ValueError),
    ],
)
def test_calculate_vat(amount, vat_rate, expected_vat_amount):
    if isinstance(expected_vat_amount, type) and issubclass(
        expected_vat_amount,
        Exception,
    ):
        with pytest.raises(expected_vat_amount):
            calculate_vat(amount, vat_rate)
    else:
        vat = calculate_vat(amount, vat_rate)
        assert vat == expected_vat_amount


@pytest.mark.parametrize(
    "amount, percentage, expected_result",
    [
        (Dinero.from_major("3000", USD), 15, Dinero.from_major("450", USD)),
        (Dinero.from_major("3000", USD), 0, Dinero.from_major("0", USD)),
        (Dinero.from_major("3000", USD), 100, Dinero.from_major("3000", USD)),
        (Dinero.from_major("3000", EUR), 15, Dinero.from_major("450", EUR)),
        (Dinero.from_major("3000", EUR), 0, Dinero.from_major("0", EUR)),
        (Dinero.from_major("3000", EUR), 100, Dinero.from_major("3000", EUR)),
        (Dinero.from_major("3000", USD), "15", TypeError),
        (Dinero.from_major("3000", USD), -15, ValueError),
        (3000, 15, InvalidOperationError),
    ],
)
def test_calculate_percentage(amount, percentage, expected_result):
    if isinstance(expected_result, type) and issubclass(expected_result, Exception):
        with pytest.raises(expected_result):
            calculate_percentage(amount, percentage)
    else:
        percentage = calculate_percentage(amount, percentage)
        assert percentage == expected_result


@pytest.mark.parametrize(
    "principal, interest_rate, duration, expected_interest, error",
    [
        (Dinero.from_major(1000, USD), 5, 2, Dinero.from_major(100, USD), None),
        (Dinero.from_major(500, EUR), 3.5, 3, Dinero.from_major(52.5, EUR), None),
        (1000, 5, 2, None, InvalidOperationError),
        (Dinero.from_major(1000, USD), 5, "2.5", None, TypeError),
        (Dinero.from_major(1000, USD), 5, 2.5, None, TypeError),
        (Dinero.from_major(1000, USD), -5, 2, None, ValueError),
        (Dinero.from_major(1000, USD), 5, -2, None, ValueError),
    ],
)
def test_calculate_simple_interest(
    principal, interest_rate, duration, expected_interest, error
):
    if error:
        with pytest.raises(error):
            calculate_simple_interest(
                principal=principal,
                interest_rate=interest_rate,
                duration=duration,
            )
    else:
        interest = calculate_simple_interest(
            principal=principal,
            interest_rate=interest_rate,
            duration=duration,
        )
        assert interest == expected_interest


@pytest.mark.parametrize(
    "principal, interest_rate, duration, compound_frequency, expected, error",
    [
        (
            Dinero.from_major(1000, USD),
            5.0,
            10,
            12,
            Dinero.from_major(647.01, USD),
            None,
        ),
        (Dinero.from_major(500, EUR), 2.5, 5, 4, Dinero.from_major(66.35, EUR), None),
        (Dinero.from_major(2000, JPY), 1.0, 3, 1, Dinero.from_major(60.60, JPY), None),
        (1000, 5.0, 10, 12, None, InvalidOperationError),
        (Dinero.from_major(1000, USD), -5.0, 10, 12, None, ValueError),
        (Dinero.from_major(1000, USD), 5.0, -10, 12, None, ValueError),
        (Dinero.from_major(1000, USD), 5.0, 10, -12, None, ValueError),
    ],
)
def test_calculate_compound_interest(
    principal, interest_rate, duration, compound_frequency, expected, error
):
    if error:
        with pytest.raises(error):
            calculate_compound_interest(
                principal=principal,
                interest_rate=interest_rate,
                duration=duration,
                compound_frequency=compound_frequency,
            )
    else:
        compound_interest = calculate_compound_interest(
            principal=principal,
            interest_rate=interest_rate,
            duration=duration,
            compound_frequency=compound_frequency,
        )
        assert compound_interest.equals_to(expected)


@pytest.mark.parametrize(
    "cost, markup, expected_final_price, error",
    [
        (Dinero.from_major(1000, USD), 15, Dinero.from_major(1150, USD), None),
        (Dinero.from_major(500, EUR), 10, Dinero.from_major(550, EUR), None),
        (Dinero.from_major(2000, CLP), 20, Dinero.from_major(2400, CLP), None),
        (1000, 15, None, InvalidOperationError),
        (Dinero.from_major(1000, USD), "15", None, TypeError),
        (Dinero.from_major(1000, USD), -15, None, ValueError),
    ],
)
def test_calculate_markup(cost, markup, expected_final_price, error):
    if error:
        with pytest.raises(error):
            calculate_markup(cost, markup)
    else:
        calculated_final_price = calculate_markup(cost, markup)
        assert calculated_final_price == expected_final_price
