"""
Dinero allows the user to make exact monetary calculations.

- from_major:: Create a Dinero object from major units (dollars, euros, etc.)
- from_minor:: Create a Dinero object from minor units (cents, centavos, etc.) using whole numbers.
- from_fractional_minor:: Create a Dinero object from fractional minor units (specialized use cases)
- to_minor_units:: Convert the amount to minor units for storage.
- format:: Format a Dinero object with his decimals, symbol and/or code.
- add:: Returns a new Dinero object that represents the sum of two amounts.
- subtract:: Returns a new Dinero object that represents the difference of two amounts.
- multiply:: Returns a new Dinero object that represents the multiplied value by a factor.
- divide:: Returns a new Dinero object that represents the divided value by a factor.
- equals_to:: Checks whether the value represented by this object equals to the other.
- less_than:: Checks whether the value represented by this object is less than the other.
- less_than_or_equal:: Checks whether an object is less than or equal the other.
- greater_than:: Checks whether an object is greater than the other.
- greater_than_or_equal:: Checks whether an object is greater than or equal the other.
- to_dict:: Returns the object's data as a Python Dictionary.
- to_db_dict:: Returns the object's data with amount in minor units for DB storage.
- to_json:: Returns the object's data as a JSON string.
- to_db_json:: Returns the object's data as a JSON string with amount in minor units.
"""

import json
from decimal import Decimal, getcontext
from typing import Any, Dict, Type, TypeVar, Union

from ._utils import DecimalEncoder
from ._validators import Validators
from .exceptions import DifferentCurrencyError, InvalidOperationError
from .types import Currency, OperationType

T = TypeVar("T", bound="Dinero")

validate = Validators()


class Dinero:
    """A Dinero object is an immutable data structure representing a specific monetary value.
    It comes with methods for creating, parsing, manipulating, testing and formatting them.
    """

    def __init__(
        self,
        amount: Union[int, float, str, Decimal],
        currency: Currency,
        *,
        _internal: bool = False,
    ) -> None:
        """Initialize a Dinero object with an amount in major units.

        Note: Direct constructor use is discouraged. Use factory methods instead.
        """
        # Prevent direct construction
        if not _internal and type(self) is Dinero:
            raise ValueError(
                "Direct constructor use is ambiguous. Use Dinero.from_major(), "
                "Dinero.from_minor(), or Dinero.from_fractional_minor() to clarify "
                "your intention."
            )

        # Validate and convert amount
        validate.dinero_amount(amount)

        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))

        self.amount = amount
        self.currency = currency

    @classmethod
    def from_major(
        cls: Type[T], amount: Union[int, float, str, Decimal], currency: Currency
    ) -> T:
        """Create a Dinero object from major currency units.

        Major units are the primary denomination of a currency:
        - USD: dollars (not cents)
        - EUR: euros (not cents)
        - JPY: yen (not sen)
        - GBP: pounds (not pence)

        Examples:
            >>> Dinero.from_major(25.50, USD)  # $25.50 (25 dollars, 50 cents)
            25.50

            >>> Dinero.from_major("99.99", EUR)  # €99.99 (99 euros, 99 cents)
            99.99

            >>> # Same amount represented in two ways:
            >>> Dinero.from_major(10.50, USD)  # $10.50
            10.50
            >>> Dinero.from_minor(1050, USD)   # also $10.50
            10.50

        Args:
            amount (int, float, str, Decimal): The amount in major units
            currency (Currency): The currency object defining code, base, exponent, etc.

        Returns:
            DINERO: A new Dinero object with the specified amount and currency
        """
        # Just call init with the internal flag
        return cls(amount, currency, _internal=True)

    @classmethod
    def from_minor(
        cls: Type[T], amount: Union[int, str, Decimal], currency: Currency
    ) -> T:
        """Create a Dinero object from minor currency units.

        Minor units are the fractional denomination of a currency and must be whole numbers:
        - USD: cents (100 cents = 1 dollar)
        - EUR: cents (100 cents = 1 euro)
        - JPY: sen (100 sen = 1 yen, though practically not used)
        - GBP: pence (100 pence = 1 pound)

        The exponent in the currency object determines the conversion rate between
        minor and major units (typically 2, meaning 10^2 or 100 minor units = 1 major unit).

        Examples:
            >>> Dinero.from_minor(2550, USD)  # 2550 cents = $25.50
            25.50

            >>> Dinero.from_minor("9999", EUR)  # 9999 cents = €99.99
            99.99

            >>> # Same amount represented in two ways:
            >>> Dinero.from_minor(1050, USD)   # 1050 cents = $10.50
            10.50
            >>> Dinero.from_major(10.50, USD)  # also $10.50
            10.50

        Args:
            amount (int, str, Decimal): The amount in minor units (must be a whole number)
            currency (Currency): The currency object defining code, base, exponent, etc.

        Returns:
            DINERO: A new Dinero object with the amount converted to major units

        Raises:
            InvalidOperationError: If the amount is invalid
            ValueError: If the amount is not a whole number

        Note:
            For fractional minor units (rare in most financial contexts),
            use from_fractional_minor() instead.
        """
        validate.dinero_amount(amount)

        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))

        # Validate that the amount is a whole number
        if amount % 1 != 0:
            raise ValueError(
                "Minor currency units must be whole numbers. "
                "For fractional minor units, use from_fractional_minor()."
            )

        exponent = currency["exponent"]
        major_amount = amount / Decimal(10**exponent)

        # Use init properly
        return cls(major_amount, currency, _internal=True)

    def to_minor_units(self) -> int:
        """Convert the amount to minor units for storage.

        Examples:
            >>> Dinero.from_major(25.50, USD).to_minor_units()
            2550

            >>> Dinero.from_major(99.99, EUR).to_minor_units()
            9999

        Returns:
            INT: Integer representing the amount in minor units
        """
        exponent = self.currency["exponent"]
        # Calculate minor units using normalized amount
        return int(self._normalize(quantize=True) * (10**exponent))

    @classmethod
    def from_fractional_minor(
        cls: Type[T], amount: Union[int, float, str, Decimal], currency: Currency
    ) -> T:
        """Create a Dinero object from fractional minor currency units.

        This method accepts fractional minor units as input, but the resulting Dinero object
        will follow standard currency precision rules. The value will be quantized to the
        currency's exponent (e.g., 2 decimal places for USD) in operations like format()
        and to_minor_units(). This behavior follows standard financial calculation practices.

        Use cases for fractional minor units might include:
        - Gas pricing (e.g., $3.999 per gallon in the US)
        - Commodity pricing
        - Interest calculations resulting in fractional cents
        - Cryptocurrency with many decimal places

        Examples:
            >>> Dinero.from_fractional_minor(12.25, USD)  # 12.25 cents = $0.1225
            0.12  # Note: quantized to currency's precision (2 decimal places for USD)

            >>> Dinero.from_fractional_minor(10.505, USD)  # 10.505 cents = $0.10505
            0.11  # Rounded to currency precision using banker's rounding

            >>> Dinero.from_fractional_minor("3.5", EUR)  # 3.5 cents = €0.035
            0.04  # Quantized to currency precision

        Args:
            amount (int, float, str, Decimal): The amount in fractional minor units
            currency (Currency): The currency object defining code, base, exponent, etc.

        Returns:
            DINERO: A new Dinero object with the amount converted to major units
                   and quantized according to currency precision

        Raises:
            InvalidOperationError: If the amount is invalid
        """
        validate.dinero_amount(amount)

        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))

        exponent = currency["exponent"]
        major_amount = amount / Decimal(10**exponent)

        # Use init properly
        return cls(major_amount, currency, _internal=True)

    # Properties
    @property
    def symbol(self) -> str:
        return self.currency.get("symbol", "$")

    @property
    def code(self) -> str:
        return self.currency.get("code")

    @property
    def exponent(self) -> int:
        return self.currency.get("exponent")

    @property
    def precision(self) -> int:
        return self.currency.get("base")

    @property
    def _formatted_amount(self) -> str:
        currency_format = f",.{self.exponent}f"
        return f"{self._normalize(quantize=True):{currency_format}}"

    @property
    def raw_amount(self) -> Decimal:
        return self._normalize(quantize=True)

    # Utilities
    def _normalize(self, quantize: bool = False) -> Decimal:
        """Return a Decimal object, that can be quantize.

        Args:
            quantize (bool): Only for the final result. Defaults to False.

        Returns
            Decimal: Decimal object.
        """
        # Increase precision to handle large numbers
        getcontext().prec = max(self.precision, len(str(self.amount)) + self.exponent)
        normalized_amount = Decimal(self.amount).normalize()

        if quantize:
            places = Decimal(f"1e-{self.exponent}")
            normalized_amount = normalized_amount.quantize(places)

        return normalized_amount

    def _get_instance(self, amount: Union["OperationType", "Dinero"]) -> "Dinero":
        """Return a Dinero object after checking the currency codes are equal and
        transforming it to Dinero if needed.

        Args:
            amount: amount to be instantiated

        Returns:
            Dinero object.

        Raises:
            DifferentCurrencyError: Currencies can not be different
        """
        amount_obj = (
            amount
            if isinstance(amount, Dinero)
            else type(self).from_major(amount, self.currency)
        )

        if amount_obj.code != self.code:
            raise DifferentCurrencyError("Currencies can not be different")

        return amount_obj

    # Format and output methods
    def format(self, symbol: bool = False, currency: bool = False) -> str:
        """Format a Dinero object with his decimals, symbol and/or code.

        Examples:
            >>> Dinero.from_major('234342.3010', USD).format()
            234,342.30

            >>> Dinero.from_major('234342.3010', USD).format(symbol=True)
            $234,342.30

            >>> Dinero.from_major('234342.3010', USD).format(currency=True)
            234,342.30 USD

            >>> Dinero.from_major('234342.3010', USD).format(symbol=True, currency=True)
            $234,342.30 USD

        Args:
            symbol (bool): Add the country currency symbol. Defaults to False.
            currency (bool): Add the country currency code. Defaults to False.

        Returns:
            STR: Formatted string representation of a Dinero object.
        """
        currency_symbol = self.symbol if symbol else ""
        currency_code = f" {self.code}" if currency else ""
        return f"{currency_symbol}{self._formatted_amount}{currency_code}"

    def to_dict(self, amount_with_format: bool = False) -> Dict[str, Any]:
        """Returns the object's data as a Python Dictionary.

        Examples:
            >>> Dinero.from_major("3333.259", USD).to_dict()
            {
                'amount': '3333.26',
                'currency':
                    {
                        'code': 'USD',
                        'base': 10,
                        'exponent': 2,
                        'symbol': '$'
                    }
            }

            >>> Dinero.from_major('3333.26', USD).to_dict(amount_with_format=True)
            {
                'amount': '3,333.26',
                'currency':
                    {
                        'code': 'USD',
                        'base': 10,
                        'exponent': 2,
                        'symbol': '$'
                    }
            }

        Args:
            amount_with_format (bool): If the amount is formatted or not. Defaults to False.

        Returns:
            DICT: The object's data as a Python Dictionary.
        """
        normalized_amount = self._normalize(quantize=True)
        amount = (
            self._formatted_amount if amount_with_format else str(normalized_amount)
        )

        return {"amount": amount, "currency": {**self.currency, "symbol": self.symbol}}

    def to_db_dict(self) -> Dict[str, Any]:
        """Returns the object's data as a Python Dictionary with amount in minor units for DB storage.

        Examples:
            >>> Dinero.from_major(3333.26, USD).to_db_dict()
            {
                'amount': 333326,
                'currency':
                    {
                        'code': 'USD',
                        'base': 10,
                        'exponent': 2,
                        'symbol': '$'
                    }
            }

        Returns:
            DICT: The object's data with amount in minor units
        """
        return {
            "amount": self.to_minor_units(),
            "currency": {**self.currency, "symbol": self.symbol},
        }

    def to_json(self, amount_with_format: bool = False) -> str:
        """Returns the object's data as a JSON string.

        Examples:
            >>> Dinero.from_major('3333.26', USD).to_json()
            '{"amount": "3333.26", "currency": {"code": "USD", "base": 10...'

            >>> Dinero.from_major('3333.26', USD).to_json(amount_with_format=True)
            '{"amount": "3,333.26", "currency": {"code": "USD", "base": 10...'

        Args:
            amount_with_format (bool): If the amount is formatted or not. Defaults to False.

        Returns:
            STR: The object's data as JSON.
        """
        dict_representation = self.to_dict(amount_with_format)
        return json.dumps(dict_representation, cls=DecimalEncoder)

    def to_db_json(self) -> str:
        """Returns the object's data as a JSON string with amount in minor units for DB storage.

        Examples:
            >>> Dinero.from_major(3333.26, USD).to_db_json()
            '{"amount": 333326, "currency": {"code": "USD", "base": 10, "exponent": 2, "symbol": "$"}}'

        Returns:
            STR: JSON representation with amount in minor units
        """
        dict_representation = self.to_db_dict()
        return json.dumps(dict_representation, cls=DecimalEncoder)

    # Operation methods
    def add(self, addend: Union["OperationType", "Dinero"]) -> "Dinero":
        """Returns a new Dinero object that represents the sum of this and an other object.

        If the addend is not a Dinero object, it will be transformed to one using the
        same currency.

        Examples:
            >>> amount_1 = Dinero.from_major("2.32", USD)
            >>> amount_2 = Dinero.from_major("2.32", USD)
            >>> amount_1.add(amount_2)
            4.64

            >>> amount = Dinero.from_major("2.32", USD)
            >>> amount.add("2.32")
            4.64

            >>> Dinero.from_major("2.32", USD) + Dinero.from_major("2.32", USD)
            4.64

            >>> Dinero.from_major("2.32", USD) + "2.32"
            4.64

        Args:
            addend: The addend.

        Raises:
            DifferentCurrencyError: Different currencies were used.
            InvalidOperationError: An operation between unsupported types was executed.

        Returns:
            DINERO: Dinero object.
        """
        return self.__add__(addend)

    def subtract(self, subtrahend: Union["OperationType", "Dinero"]) -> "Dinero":
        """Returns a new Dinero object that represents the difference of this and an other object.

        If the subtrahend is not a Dinero object, it will be transformed to one using the
        same currency.

        Examples:
            >>> amount_1 = Dinero.from_major("2.32", USD)
            >>> amount_2 = Dinero.from_major("2", USD)
            >>> amount_1.subtract(amount_2)
            0.32

            >>> amount = Dinero.from_major("2.32", USD)
            >>> amount.subtract(2)
            0.32

            >>> Dinero.from_major("2.32", USD) - Dinero.from_major("2", USD)
            0.32

            >>> Dinero.from_major("2.32", USD) - "2"
            0.32

        Args:
            subtrahend: The subtrahend.

        Raises:
            DifferentCurrencyError: Different currencies were used.
            InvalidOperationError: An operation between unsupported types was executed.

        Returns:
            DINERO: Dinero object.
        """
        return self.__sub__(subtrahend)

    def multiply(self, amount: Union[int, float, Decimal]) -> "Dinero":
        """Returns a new Dinero object that represents the multiplied value by the given factor.

        Examples:
            >>> amount = Dinero.from_major("2.32", USD)
            >>> amount.multiply(3)
            6.96

            >>> Dinero.from_major("2.32", USD) * 3
            6.96

        Args:
            amount: The multiplicand.

        Raises:
            InvalidOperationError: An operation between unsupported types was executed.

        Returns:
            DINERO: Dinero object.
        """
        return self.__mul__(amount)

    def divide(self, amount: Union[int, float, Decimal]) -> "Dinero":
        """Returns a new Dinero object that represents the divided value by the given factor.

        Examples:
            >>> amount = Dinero.from_major("2.32", USD)
            >>> amount.divide(3)
            0.77

            >>> Dinero.from_major("2.32", USD) / 3
            0.77

        Args:
            amount: The divisor.

        Raises:
            InvalidOperationError: An operation between unsupported types was executed.

        Returns:
            DINERO: Dinero object.
        """
        return self.__truediv__(amount)

    # Comparison methods
    def equals_to(self, amount: "Dinero") -> bool:
        """Checks whether the value represented by this object equals to other Dinero instance.

        Examples:
            >>> amount_1 = Dinero.from_major("2.32", USD)
            >>> amount_2 = Dinero.from_major("2.32", USD)
            >>> amount_1.equals_to(amount_2)
            True

            >>> Dinero.from_major("2.32", USD) == Dinero.from_major("2.32", USD)
            True

        Args:
            amount: The object to compare to.

        Raises:
            DifferentCurrencyError: Different currencies were used.
            InvalidOperationError: An operation between unsupported types was executed.

        Returns:
            BOOL: Whether the value represented is equals to the other.
        """
        return self.__eq__(amount)

    def less_than(self, amount: "Dinero") -> bool:
        """Checks whether the value represented by this object is less than the other.

        Examples:
            >>> amount_1 = Dinero.from_major(24, USD)
            >>> amount_2 = Dinero.from_major(25, USD)
            >>> amount_1.less_than(amount_2)
            True

            >>> Dinero.from_major(24, USD) < Dinero.from_major(25, USD)
            True

        Args:
            amount: The object to compare to.

        Raises:
            DifferentCurrencyError: Different currencies were used.
            InvalidOperationError: An operation between unsupported types was executed.

        Returns:
            BOOL: Whether the value represented is less than to the other.
        """
        return self.__lt__(amount)

    def less_than_or_equal(self, amount: "Dinero") -> bool:
        """Checks whether the value represented by this object is less than or equal the other.

        Examples:
            >>> amount_1 = Dinero.from_major(24, USD)
            >>> amount_2 = Dinero.from_major(25, USD)
            >>> amount_1.less_than_or_equal(amount_2)
            True

            >>> Dinero.from_major(24, USD) <= Dinero.from_major(25, USD)
            True

        Args:
            amount: The object to compare to.

        Raises:
            DifferentCurrencyError: Different currencies were used.
            InvalidOperationError: An operation between unsupported types was executed.

        Returns:
            BOOL: Whether the value represented is less than or equal to the other.
        """
        return self.__le__(amount)

    def greater_than(self, amount: "Dinero") -> bool:
        """Checks whether the value represented by this object is greater than the other.

        Examples:
            >>> amount_1 = Dinero.from_major(25, USD)
            >>> amount_2 = Dinero.from_major(24, USD)
            >>> amount_1.greater_than(amount_2)
            True

            >>> Dinero.from_major(25, USD) > Dinero.from_major(24, USD)
            True

        Args:
            amount: The object to compare to.

        Raises:
            DifferentCurrencyError: Different currencies were used.
            InvalidOperationError: An operation between unsupported types was executed.

        Returns:
            BOOL: Whether the value represented is greater than to the other.
        """
        return self.__gt__(amount)

    def greater_than_or_equal(self, amount: "Dinero") -> bool:
        """Checks whether the value represented by this object is greater than or equal the other.

        Examples:
            >>> amount_1 = Dinero.from_major(25, USD)
            >>> amount_2 = Dinero.from_major(24, USD)
            >>> amount_1.greater_than_or_equal(amount_2)
            True

            >>> Dinero.from_major(25, USD) >= Dinero.from_major(24, USD)
            True

        Args:
            amount: The object to compare to.

        Raises:
            DifferentCurrencyError: Different currencies were used.
            InvalidOperationError: An operation between unsupported types was executed.

        Returns:
            BOOL: Whether the value represented is greater than or equal to the other.
        """
        return self.__ge__(amount)

    # Operator Overloads
    def __add__(self, addend: Union["OperationType", "Dinero"]) -> "Dinero":
        validate.addition_and_subtraction_amount(addend)
        addend_obj = self._get_instance(addend)
        total = self._normalize() + addend_obj._normalize()
        return type(self).from_major(total, self.currency)

    def __radd__(self, obj):
        return self

    def __sub__(self, subtrahend: Union["OperationType", "Dinero"]) -> "Dinero":
        validate.addition_and_subtraction_amount(subtrahend)
        subtrahend_obj = self._get_instance(subtrahend)
        total = self._normalize() - subtrahend_obj._normalize()
        return type(self).from_major(total, self.currency)

    def __mul__(self, multiplicand: Union[int, float, Decimal]) -> "Dinero":
        validate.multiplication_and_division_amount(multiplicand)
        multiplicand_obj = self._get_instance(multiplicand)
        total = self._normalize() * multiplicand_obj._normalize()
        return type(self).from_major(total, self.currency)

    def __truediv__(self, divisor: Union[int, float, Decimal]) -> "Dinero":
        validate.multiplication_and_division_amount(divisor)
        divisor_obj = self._get_instance(divisor)
        total = self._normalize() / divisor_obj._normalize()
        return type(self).from_major(total, self.currency)

    def __eq__(self, amount: object) -> bool:
        if not isinstance(amount, Dinero):
            raise InvalidOperationError(InvalidOperationError.comparison_msg)

        num_2 = self._get_instance(amount)._normalize(quantize=True)
        num_1 = self._normalize(quantize=True)
        return bool(num_1 == num_2)

    def __lt__(self, amount: object) -> bool:
        if not isinstance(amount, Dinero):
            raise InvalidOperationError(InvalidOperationError.comparison_msg)

        num_1 = self._normalize(quantize=True)
        num_2 = self._get_instance(amount)._normalize(quantize=True)
        return bool(num_1 < num_2)

    def __le__(self, amount: object) -> bool:
        if not isinstance(amount, Dinero):
            raise InvalidOperationError(InvalidOperationError.comparison_msg)

        num_1 = self._normalize(quantize=True)
        num_2 = self._get_instance(amount)._normalize(quantize=True)
        return bool(num_1 <= num_2)

    def __gt__(self, amount: object) -> bool:
        if not isinstance(amount, Dinero):
            raise InvalidOperationError(InvalidOperationError.comparison_msg)

        num_1 = self._normalize(quantize=True)
        num_2 = self._get_instance(amount)._normalize(quantize=True)
        return bool(num_1 > num_2)

    def __ge__(self, amount: object) -> bool:
        if not isinstance(amount, Dinero):
            raise InvalidOperationError(InvalidOperationError.comparison_msg)

        num_1 = self._normalize(quantize=True)
        num_2 = self._get_instance(amount)._normalize(quantize=True)
        return bool(num_1 >= num_2)

    def __repr__(self):
        return f"Dinero(amount={self.amount}, currency={self.currency})"

    def __str__(self):
        formatted_output = self.format()
        return f"{formatted_output}"
