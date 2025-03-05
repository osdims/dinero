import pytest

from dinero import Dinero
from dinero.currencies import USD


@pytest.mark.parametrize(
    "amount",
    [
        (Dinero.from_major("3333.259", USD)),
        (Dinero.from_major(3333.259, USD)),
    ],
    ids=["obj_str", "obj_int"],
)
def test_unformatted_dict(amount):
    expected_unformatted_result = {
        "amount": "3333.26",
        "currency": {"code": "USD", "base": 10, "exponent": 2, "symbol": "$"},
    }
    assert amount.to_dict() == expected_unformatted_result


@pytest.mark.parametrize(
    "amount",
    [
        (Dinero.from_major("3333.259", USD)),
        (Dinero.from_major(3333.259, USD)),
    ],
    ids=["obj_str", "obj_int"],
)
def test_formatted_dict(amount):
    expected_result = {
        "amount": "3,333.26",
        "currency": {"code": "USD", "base": 10, "exponent": 2, "symbol": "$"},
    }
    assert amount.to_dict(amount_with_format=True) == expected_result


@pytest.mark.parametrize(
    "amount",
    [
        (Dinero.from_major("3333.2", USD)),
        (Dinero.from_major(3333.2, USD)),
    ],
    ids=["obj_str", "obj_str"],
)
def test_unformatted_json(amount):
    expected_result = '{"amount": "3333.20", "currency": {"code": "USD", "base": 10, "exponent": 2, "symbol": "$"}}'  # noqa: E501
    assert amount.to_json() == expected_result


@pytest.mark.parametrize(
    "amount",
    [
        (Dinero.from_major("3333.2", USD)),
        (Dinero.from_major(3333.2, USD)),
    ],
    ids=["obj_str", "obj_str"],
)
def test_formatted_json(amount):
    expected_result = '{"amount": "3,333.20", "currency": {"code": "USD", "base": 10, "exponent": 2, "symbol": "$"}}'  # noqa: E501
    assert amount.to_json(amount_with_format=True) == expected_result


@pytest.mark.parametrize(
    "amount",
    [
        (Dinero.from_major("3333.259", USD)),
        (Dinero.from_major(3333.259, USD)),
    ],
    ids=["obj_str", "obj_int"],
)
def test_to_db_dict(amount):
    expected_result = {
        "amount": 333326,
        "currency": {"code": "USD", "base": 10, "exponent": 2, "symbol": "$"},
    }
    assert amount.to_db_dict() == expected_result


@pytest.mark.parametrize(
    "amount",
    [
        (Dinero.from_major("3333.2", USD)),
        (Dinero.from_major(3333.2, USD)),
    ],
    ids=["obj_str", "obj_str"],
)
def test_to_db_json(amount):
    expected_result = '{"amount": 333320, "currency": {"code": "USD", "base": 10, "exponent": 2, "symbol": "$"}}'  # noqa: E501
    assert amount.to_db_json() == expected_result


def test_fractional_minor_db_storage():
    """Test to_minor_units and to_db_dict/to_db_json with fractional minor origins"""
    # Create with fractional minor units
    amount = 1050.5  # 1050.5 cents = $10.505
    obj = Dinero.from_fractional_minor(amount, USD)

    # When converted to minor units and stored, fractions should be rounded
    assert obj.to_minor_units() == 1050  # Rounded to nearest cent

    # Check db dict has the rounded amount
    db_dict = obj.to_db_dict()
    assert db_dict["amount"] == 1050

    # Similarly, db_json should have the rounded amount
    import json

    db_json = obj.to_db_json()
    parsed = json.loads(db_json)
    assert parsed["amount"] == 1050
