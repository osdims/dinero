from decimal import Decimal, getcontext

import pytest

from dinero import Dinero
from dinero.currencies import USD, EUR, GBP, JPY
from dinero.exceptions import InvalidOperationError
from dinero._validators import Validators

unit_price = Dinero.from_major(2.32, USD)
money_received = Dinero.from_major("6.96", USD)
number_sold = 3


validate = Validators()


def test_direct_constructor_error():
    """Test that direct constructor raises an error"""
    with pytest.raises(ValueError):
        Dinero(100, USD)


@pytest.mark.parametrize(
    "obj, expected",
    [
        (Dinero.from_major(100, USD), Decimal("100.00")),
        (Dinero.from_major(100.25, USD), Decimal("100.25")),
        (Dinero.from_major(Decimal("100.25"), USD), Decimal("100.25")),
    ],
)
def test_from_major(obj, expected):
    """Test creation from major units"""
    assert obj.raw_amount == expected


@pytest.mark.parametrize(
    "obj, expected",
    [
        (Dinero.from_minor(10025, USD), Decimal("100.25")),
        (Dinero.from_minor("10025", USD), Decimal("100.25")),
        (Dinero.from_minor(Decimal("10025"), USD), Decimal("100.25")),
    ],
)
def test_from_minor(obj, expected):
    """Test creation from minor units"""
    assert obj.raw_amount == expected


@pytest.mark.parametrize(
    "amount",
    [10.5, 100.25, "10.5", Decimal("100.25")],
)
def test_from_minor_rejects_fractional(amount):
    """Test that from_minor rejects fractional numbers"""
    with pytest.raises(ValueError, match="Minor currency units must be whole numbers"):
        Dinero.from_minor(amount, USD)


@pytest.mark.parametrize(
    "obj, expected",
    [
        (Dinero.from_major(100.25, USD), 10025),
        (Dinero.from_major(100.25, EUR), 10025),
        (Dinero.from_major(100, JPY), 100),
    ],
)
def test_to_minor_units(obj, expected):
    """Test conversion to minor units"""
    assert obj.to_minor_units() == expected


@pytest.mark.parametrize(
    "obj, expected",
    [
        (Dinero.from_fractional_minor(10025, USD), Decimal("100.25")),
        (Dinero.from_fractional_minor(10025.5, USD), Decimal("100.260")),
        (Dinero.from_fractional_minor("10025.5", USD), Decimal("100.260")),
        (Dinero.from_fractional_minor(Decimal("10025.5"), USD), Decimal("100.260")),
    ],
)
def test_from_fractional_minor(obj, expected):
    """Test creation from fractional minor units"""
    # Adjust precision for comparison to match the expected value's precision
    precision = len(str(expected).split(".")[-1])
    places = Decimal(f"1e-{precision}")
    assert obj.raw_amount.quantize(places) == expected


@pytest.mark.parametrize(
    "amount",
    [[], (), {}, set(), "abc", "12.x"],
)
def test_from_fractional_minor_invalid_inputs(amount):
    """Test that from_fractional_minor rejects invalid inputs"""
    with pytest.raises(InvalidOperationError):
        Dinero.from_fractional_minor(amount, USD)


@pytest.mark.parametrize(
    "amount, expected",
    [
        (0, Decimal("0.00")),
        (0.00, Decimal("0.00")),
        (0.001, Decimal("0.00000")),  # Test small fractional amount
        (10_000_000.5, Decimal("100000.000")),  # Test large amount with fraction
    ],
)
def test_from_fractional_minor_edge_cases(amount, expected):
    """Test edge cases for from_fractional_minor"""
    obj = Dinero.from_fractional_minor(amount, USD)
    precision = len(str(expected).split(".")[-1])
    places = Decimal(f"1e-{precision}")
    assert obj.raw_amount.quantize(places) == expected


@pytest.mark.parametrize(
    "fractional_minor_amount, major_amount",
    [
        (12.25, 0.1225),  # 12.25 cents = $0.1225
        (1050, 10.50),  # 1050 cents = $10.50
        (333.33, 3.3333),  # 333.33 cents = $3.3333
    ],
)
def test_fractional_minor_equals_major(fractional_minor_amount, major_amount):
    """Test that from_fractional_minor equals from_major with equivalent values"""
    fractional_obj = Dinero.from_fractional_minor(fractional_minor_amount, USD)
    major_obj = Dinero.from_major(major_amount, USD)

    # Increase decimal precision for comparison
    getcontext().prec = 10
    assert fractional_obj.equals_to(major_obj)


@pytest.mark.parametrize(
    "amount, currency, expected",
    [
        (12.25, USD, Decimal("0.1200")),  # USD has exponent 2 (100 cents = 1 dollar)
        (12.25, JPY, Decimal("12.00")),  # JPY has exponent 0 (yen has no minor unit)
        (12.25, EUR, Decimal("0.1200")),  # EUR has exponent 2 (100 cents = 1 euro)
    ],
)
def test_from_fractional_minor_currencies(amount, currency, expected):
    """Test from_fractional_minor with different currencies"""
    obj = Dinero.from_fractional_minor(amount, currency)
    # Need to handle different exponents for different currencies
    precision = len(str(expected).split(".")[-1])
    places = Decimal(f"1e-{precision}")
    assert obj.raw_amount.quantize(places) == expected


@pytest.mark.parametrize(
    "minor_method, fractional_method, amount, expected",
    [
        (Dinero.from_minor, Dinero.from_fractional_minor, 1000, Decimal("10.00")),
        (Dinero.from_minor, Dinero.from_fractional_minor, "1000", Decimal("10.00")),
        (
            Dinero.from_minor,
            Dinero.from_fractional_minor,
            Decimal("1000"),
            Decimal("10.00"),
        ),
    ],
)
def test_minor_equals_fractional_for_integers(
    minor_method, fractional_method, amount, expected
):
    """Test that from_minor and from_fractional_minor produce same results for whole numbers"""
    minor_obj = minor_method(amount, USD)
    fractional_obj = fractional_method(amount, USD)

    assert minor_obj.equals_to(fractional_obj)
    assert minor_obj.raw_amount == expected


@pytest.mark.parametrize(
    "amount",
    [
        (Dinero.from_major(24, USD)),
        (Dinero.from_major(24.5, USD)),
        (Dinero.from_major("24.5", USD)),
    ],
)
def test_dinero_amount_validator(amount):
    assert isinstance(amount, Dinero)


@pytest.mark.parametrize(
    "amount",
    [[], (), {}, set()],
)
def test_error_dinero_amount_validator(amount):
    with pytest.raises(InvalidOperationError):
        Dinero.from_major(amount, USD)


@pytest.mark.parametrize(
    "obj, amount, raw_type",
    [
        (Dinero.from_major(2.32, USD), Decimal(2.32), Decimal),
        (Dinero.from_major("6.96", USD), Decimal(6.96), Decimal),
    ],
)
def test_raw_amount(obj, amount: Decimal, raw_type):
    places = Decimal(f"1e-{USD['exponent']}")

    assert obj.raw_amount == amount.quantize(places)
    assert isinstance(obj.raw_amount, raw_type)


usd_obj = Dinero.from_major(2.32, USD)
eur_obj = Dinero.from_major(2.32, EUR)
gbp_obj = Dinero.from_major(2.32, GBP)


@pytest.mark.parametrize(
    "obj, symbol, code, exponent, precision",
    [
        (usd_obj, "$", "USD", 2, 10),
        (eur_obj, "€", "EUR", 2, 10),
        (gbp_obj, "£", "GBP", 2, 10),
    ],
)
def test_obj_properties(obj, symbol, code, exponent, precision):
    assert obj.symbol == symbol
    assert obj.code == code
    assert obj.exponent == exponent
    assert obj.precision == precision


@pytest.mark.parametrize(
    "obj, number, symbol, currency, full",
    [
        (usd_obj, "2.32", "$2.32", "2.32 USD", "$2.32 USD"),
        (eur_obj, "2.32", "€2.32", "2.32 EUR", "€2.32 EUR"),
        (gbp_obj, "2.32", "£2.32", "2.32 GBP", "£2.32 GBP"),
    ],
)
def test_obj_formatted(obj, number, symbol, currency, full):
    assert obj.format() == number
    assert obj.format(symbol=True) == symbol
    assert obj.format(currency=True) == currency
    assert obj.format(symbol=True, currency=True) == full


@pytest.mark.parametrize(
    "method, amount, expected_format",
    [
        (
            Dinero.from_fractional_minor,
            12.25,
            "0.12",
        ),  # 12.25 cents = $0.1225 → $0.12 (rounded)
        (
            Dinero.from_fractional_minor,
            1050.5,
            "10.50",
        ),  # 1050.5 cents = $10.505 → $10.50 (rounded)
        (
            Dinero.from_fractional_minor,
            333.33,
            "3.33",
        ),  # 333.33 cents = $3.3333 → $3.33 (rounded)
    ],
)
def test_fractional_minor_formatted(method, amount, expected_format):
    """Test that from_fractional_minor formats correctly"""
    obj = method(amount, USD)
    assert obj.format() == expected_format


@pytest.mark.parametrize(
    "unit_price, units_sold, money_received",
    [
        (Dinero.from_major("2.32", USD), 3, Dinero.from_major("6.96", USD)),
        (Dinero.from_major("2.32", USD), Decimal(3), Dinero.from_major("6.96", USD)),
        (Dinero.from_major("2.32", USD), 3.0, Dinero.from_major("6.96", USD)),
        (Dinero.from_major("2.32", USD), Decimal(3.0), Dinero.from_major("6.96", USD)),
    ],
)
def test_balance_ok(unit_price, units_sold, money_received):
    assert unit_price.multiply(units_sold).equals_to(money_received)
    assert unit_price * units_sold == money_received


@pytest.mark.parametrize(
    "unit_price, units_sold, money_received",
    [
        (Dinero.from_major("2.38", USD), 3, Dinero.from_major("6.96", USD)),
        (Dinero.from_major("2.38", USD), Decimal(3), Dinero.from_major("6.96", USD)),
        (Dinero.from_major("2.32", USD), 2.33, Dinero.from_major("5.38", USD)),
        (Dinero.from_major("2.32", USD), Decimal(2.33), Dinero.from_major("5.38", USD)),
    ],
)
def test_balance_wrong(unit_price, units_sold, money_received):
    assert unit_price.multiply(units_sold).equals_to(money_received) is False
    assert unit_price * units_sold != money_received
