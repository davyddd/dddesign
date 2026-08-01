from typing import Optional, Set
from unittest import TestCase

from dddesign.structure.infrastructure.repositories import Repository
from dddesign.structure.infrastructure.repositories.repository import BASE_ALLOWED_METHODS
from tests.structure.validators import validate_arbitrary_types_allowed, validate_immutable


class TestRepository(TestCase):
    def test_immutable(self):
        validate_immutable(Repository, 'get')

    def test_arbitrary_types_allowed(self):
        validate_arbitrary_types_allowed(Repository, 'get')


class TestRepositoryAllowedMethods(TestCase):
    def test_not_allowed_function_raises(self):
        with self.assertRaisesRegex(TypeError, 'not_allowed_method'):

            class TestRepositoryImpl(Repository):
                def not_allowed_method(self): ...

    def test_not_allowed_staticmethod_raises(self):
        with self.assertRaisesRegex(TypeError, 'not_allowed_method'):

            class TestRepositoryImpl(Repository):
                @staticmethod
                def not_allowed_method(): ...

    def test_not_allowed_classmethod_raises(self):
        with self.assertRaisesRegex(TypeError, 'not_allowed_method'):

            class TestRepositoryImpl(Repository):
                @classmethod
                def not_allowed_method(cls): ...

    def test_base_allowed_methods_include_query_helpers(self):
        self.assertLessEqual({'exists', 'count'}, BASE_ALLOWED_METHODS)

    def test_base_allowed_methods_do_not_raise(self):
        for method_name in BASE_ALLOWED_METHODS:
            with self.subTest(method_name=method_name):
                type('TestRepositoryImpl', (Repository,), {method_name: lambda _self: None})

    def test_base_allowed_staticmethod_does_not_raise(self):
        class TestRepositoryImpl(Repository):
            @staticmethod
            def get(): ...

    def test_base_allowed_classmethod_does_not_raise(self):
        class TestRepositoryImpl(Repository):
            @classmethod
            def get(cls): ...

    def test_external_allowed_methods_do_not_raise(self) -> None:
        class TestRepositoryImpl(Repository):
            EXTERNAL_ALLOWED_METHODS: Optional[Set[str]] = {
                'external_function',
                'external_staticmethod',
                'external_classmethod',
            }

            def external_function(self): ...

            @staticmethod
            def external_staticmethod(): ...

            @classmethod
            def external_classmethod(cls): ...

    def test_dunder_methods_do_not_raise(self):
        class TestRepositoryImpl(Repository):
            def __str__(self):
                return 'repository'

            @staticmethod
            def __format_value__(): ...

            @classmethod
            def __create_instance__(cls): ...
