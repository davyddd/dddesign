from typing import List, Optional
from unittest import TestCase

from pydantic import BaseModel

from dddesign.utils.base_model import flatten_model_dump


class Headers(BaseModel):
    authorization: str
    content_type: str


class Pagination(BaseModel):
    page: int
    size: int


class Filters(BaseModel):
    pagination: Pagination
    query: str


class Request(BaseModel):
    headers: Headers
    body: str
    tags: List[str]
    filters: Optional[Filters] = None


class Flat(BaseModel):
    a: int
    b: str


class TestFlattenModelDump(TestCase):
    def test_flat_model(self):
        # Arrange
        data = Flat(a=1, b='x')

        # Act & Assert
        self.assertEqual(flatten_model_dump(data), {'a': 1, 'b': 'x'})

    def test_one_level_nesting(self):
        # Arrange
        request = Request(
            headers=Headers(authorization='Bearer token', content_type='application/json'), body='data', tags=['a', 'b']
        )

        # Act & Assert
        self.assertEqual(
            flatten_model_dump(request),
            {
                'headers.authorization': 'Bearer token',
                'headers.content_type': 'application/json',
                'body': 'data',
                'tags': ['a', 'b'],
                'filters': None,
            },
        )

    def test_deep_nesting(self):
        # Arrange
        request = Request(
            headers=Headers(authorization='Bearer token', content_type='application/json'),
            body='data',
            tags=[],
            filters=Filters(pagination=Pagination(page=1, size=10), query='test'),
        )

        # Act & Assert
        self.assertEqual(
            flatten_model_dump(request),
            {
                'headers.authorization': 'Bearer token',
                'headers.content_type': 'application/json',
                'body': 'data',
                'tags': [],
                'filters.pagination.page': 1,
                'filters.pagination.size': 10,
                'filters.query': 'test',
            },
        )

    def test_custom_separator(self):
        # Arrange
        request = Request(headers=Headers(authorization='Bearer token', content_type='application/json'), body='data', tags=[])

        # Act
        result = flatten_model_dump(request, separator='__')

        # Assert
        self.assertIn('headers__authorization', result)
        self.assertIn('headers__content_type', result)

    def test_model_dump_kwargs_exclude(self):
        # Arrange
        request = Request(headers=Headers(authorization='Bearer token', content_type='application/json'), body='data', tags=[])

        # Act
        result = flatten_model_dump(request, exclude={'headers'})

        # Assert
        self.assertNotIn('headers.authorization', result)
        self.assertNotIn('headers.content_type', result)
        self.assertIn('body', result)
