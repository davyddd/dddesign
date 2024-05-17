from datetime import date, datetime, time, timedelta
from decimal import Decimal
from ipaddress import IPv4Address, IPv6Address
from typing import Optional, Union
from unittest import TestCase
from uuid import UUID

from dddesign.utils.type_helpers import get_python_type


class TestGetPythonType(TestCase):
    def test_basic_python_types(self):
        self.assertEqual(get_python_type(str), str)
        self.assertEqual(get_python_type(bool), bool)
        self.assertEqual(get_python_type(int), int)
        self.assertEqual(get_python_type(float), float)
        self.assertEqual(get_python_type(bytes), bytes)
        self.assertEqual(get_python_type(tuple), tuple)
        self.assertEqual(get_python_type(list), list)
        self.assertEqual(get_python_type(dict), dict)
        self.assertEqual(get_python_type(date), date)
        self.assertEqual(get_python_type(time), time)
        self.assertEqual(get_python_type(datetime), datetime)
        self.assertEqual(get_python_type(timedelta), timedelta)
        self.assertEqual(get_python_type(UUID), UUID)
        self.assertEqual(get_python_type(Decimal), Decimal)
        self.assertEqual(get_python_type(IPv4Address), IPv4Address)
        self.assertEqual(get_python_type(IPv6Address), IPv6Address)

    def test_optional_type(self):
        self.assertEqual(get_python_type(Optional[int]), int)
        self.assertEqual(get_python_type(Optional[str]), str)
        self.assertEqual(get_python_type(Optional[datetime]), datetime)

    def test_union_type(self):
        self.assertEqual(get_python_type(Union[int, None]), int)
        self.assertEqual(get_python_type(Union[None, int]), int)
        self.assertEqual(get_python_type(Union[str, None]), str)
        self.assertEqual(get_python_type(Union[None, str]), str)
        self.assertEqual(get_python_type(Union[datetime, None]), datetime)
        self.assertEqual(get_python_type(Union[None, datetime]), datetime)

    def test_nested_optional_type(self):
        self.assertEqual(get_python_type(Optional[Optional[int]]), int)
        self.assertEqual(get_python_type(Optional[Optional[datetime]]), datetime)

    def test_nested_union_type(self):
        self.assertEqual(get_python_type(Union[None, Union[None, int]]), int)
        self.assertEqual(get_python_type(Union[None, Union[None, datetime]]), datetime)

    def test_unknown_type(self):
        with self.assertRaises(TypeError):
            get_python_type(frozenset)
