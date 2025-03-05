from decimal import Decimal

import pytest

from dinero import Dinero
from dinero.currencies import USD
from dinero.exceptions import InvalidOperationError


@pytest.mark.parametrize(
    "amount, multiplicand, total",
    [
        (Dinero.from_major("2.32", USD), 3, Dinero.from_major("6.96", USD)),
        (Dinero.from_major("2.32", USD), Decimal(3), Dinero.from_major("6.96", USD)),
        (Dinero.from_major("2.32", USD), 3.0, Dinero.from_major("6.96", USD)),
        (Dinero.from_major("2.32", USD), Decimal(3.0), Dinero.from_major("6.96", USD)),
    ],
)
def test_multiply_amount_str(amount, multiplicand, total):
    assert amount * multiplicand == total
    assert amount.multiply(multiplicand) == total
    assert amount.multiply(multiplicand).equals_to(total)


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
        amount * addend

    with pytest.raises(InvalidOperationError):
        amount.multiply(addend)
