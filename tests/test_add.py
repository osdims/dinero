import pytest

from dinero import Dinero
from dinero.currencies import USD, EUR
from dinero.exceptions import DifferentCurrencyError, InvalidOperationError


@pytest.mark.parametrize(
    "amount, addend, total",
    [
        (
            Dinero.from_major("24.5", USD),
            Dinero.from_major("1", USD),
            Dinero.from_major("25.50", USD),
        ),
        (Dinero.from_major("24.5", USD), "1", Dinero.from_major("25.50", USD)),
    ],
    ids=["obj_obj_obj", "obj_str_obj"],
)
def test_add_amount_str(amount, addend, total):
    assert amount + addend == total
    assert amount.add(addend) == total
    assert amount.add(addend).equals_to(total)


@pytest.mark.parametrize(
    "amount, addend, total",
    [
        (
            Dinero.from_major(24.5, USD),
            Dinero.from_major(1, USD),
            Dinero.from_major(25.50, USD),
        ),
        (Dinero.from_major(24.5, USD), 1, Dinero.from_major(25.50, USD)),
    ],
    ids=["obj_obj_obj", "obj_str_obj"],
)
def test_add_amount_number(amount, addend, total):
    assert amount + addend == total
    assert amount.add(addend) == total
    assert amount.add(addend).equals_to(total)


@pytest.mark.parametrize(
    "amount, addend, total",
    [
        (
            Dinero.from_major(24.5, USD),
            Dinero.from_major("1", USD),
            Dinero.from_major("25.50", USD),
        ),
        (
            Dinero.from_major("24.5", USD),
            Dinero.from_major(1, USD),
            Dinero.from_major("25.50", USD),
        ),
        (
            Dinero.from_major("24.5", USD),
            Dinero.from_major("1", USD),
            Dinero.from_major(25.50, USD),
        ),
        (
            Dinero.from_major(24.5, USD),
            Dinero.from_major(1, USD),
            Dinero.from_major("25.50", USD),
        ),
        (
            Dinero.from_major("24.5", USD),
            Dinero.from_major(1, USD),
            Dinero.from_major(25.50, USD),
        ),
        (
            Dinero.from_major(24.5, USD),
            Dinero.from_major("1", USD),
            Dinero.from_major(25.50, USD),
        ),
        # ----
        (Dinero.from_major(24.5, USD), "1", Dinero.from_major("25.50", USD)),
        (Dinero.from_major("24.5", USD), 1, Dinero.from_major("25.50", USD)),
        (Dinero.from_major("24.5", USD), "1", Dinero.from_major(25.50, USD)),
        (Dinero.from_major(24.5, USD), 1, Dinero.from_major("25.50", USD)),
        (Dinero.from_major("24.5", USD), 1, Dinero.from_major(25.50, USD)),
        (Dinero.from_major(24.5, USD), "1", Dinero.from_major(25.50, USD)),
    ],
)
def test_add_amount_mixed(amount, addend, total):
    assert amount + addend == total
    assert amount.add(addend) == total
    assert amount.add(addend).equals_to(total)


@pytest.mark.parametrize(
    "amount, addend, total",
    [
        (
            Dinero.from_major(24.5, USD),
            Dinero.from_major("1", USD),
            Dinero.from_major("25.50", USD),
        ),
        (
            Dinero.from_major("24.5", USD),
            Dinero.from_major(1, USD),
            Dinero.from_major("25.50", USD),
        ),
        (
            Dinero.from_major("24.5", USD),
            Dinero.from_major("1", USD),
            Dinero.from_major(25.50, USD),
        ),
        (
            Dinero.from_major(24.5, USD),
            Dinero.from_major(1, USD),
            Dinero.from_major("25.50", USD),
        ),
        (
            Dinero.from_major("24.5", USD),
            Dinero.from_major(1, USD),
            Dinero.from_major(25.50, USD),
        ),
        (
            Dinero.from_major(24.5, USD),
            Dinero.from_major("1", USD),
            Dinero.from_major(25.50, USD),
        ),
        # ----
        (Dinero.from_major(24.5, USD), "1", Dinero.from_major("25.50", USD)),
        (Dinero.from_major("24.5", USD), 1, Dinero.from_major("25.50", USD)),
        (Dinero.from_major("24.5", USD), "1", Dinero.from_major(25.50, USD)),
        (Dinero.from_major(24.5, USD), 1, Dinero.from_major("25.50", USD)),
        (Dinero.from_major("24.5", USD), 1, Dinero.from_major(25.50, USD)),
        (Dinero.from_major(24.5, USD), "1", Dinero.from_major(25.50, USD)),
    ],
)
def test_sum_amount_mixed(amount, addend, total):
    assert sum([amount, addend, 0]) == total


@pytest.mark.parametrize(
    "amount, addend",
    [
        (Dinero.from_major(24.5, USD), Dinero.from_major(1, EUR)),
        (Dinero.from_major(24.5, USD), Dinero.from_major("1", EUR)),
        (Dinero.from_major("24.5", USD), Dinero.from_major("1", EUR)),
        (Dinero.from_major("24.5", USD), Dinero.from_major(1, EUR)),
    ],
)
def test_different_currencies_error(amount, addend):
    with pytest.raises(DifferentCurrencyError):
        amount + addend

    with pytest.raises(DifferentCurrencyError):
        amount.add(addend)


@pytest.mark.parametrize(
    "amount, addend",
    [
        (Dinero.from_major(24.5, USD), []),
        (Dinero.from_major(24.5, USD), ()),
        (Dinero.from_major("24.5", USD), {}),
    ],
)
def test_invalid_operation_error(amount, addend):
    with pytest.raises(InvalidOperationError):
        amount + addend

    with pytest.raises(InvalidOperationError):
        amount.add(addend)


@pytest.mark.parametrize(
    "amount1, amount2, expected",
    [
        # Mix of factory methods
        (
            Dinero.from_major(10.50, USD),
            Dinero.from_minor(550, USD),
            Dinero.from_major(16.00, USD),
        ),
        (
            Dinero.from_minor(1050, USD),
            Dinero.from_fractional_minor(550.5, USD),
            Dinero.from_major(16.00, USD),
        ),
        (
            Dinero.from_fractional_minor(1050.5, USD),
            Dinero.from_major(5.50, USD),
            Dinero.from_major(16.00, USD),
        ),
    ],
    ids=["major+minor", "minor+fractional", "fractional+major"],
)
def test_cross_factory_method_operations(amount1, amount2, expected):
    """Test that objects created with different factory methods interact correctly"""
    assert amount1 + amount2 == expected
