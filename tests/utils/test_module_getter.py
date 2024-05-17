from types import ModuleType
from unittest import TestCase

from dddesign.utils.module_getter import get_module


class TestModuleGetter(TestCase):
    def setUp(self):
        # Create a mock module structure for testing
        self.root_module = ModuleType('root_module')
        self.sub_module_1 = ModuleType('sub_module_1')
        self.sub_module_1_1 = ModuleType('sub_module_1_1')
        self.sub_module_1_2 = ModuleType('sub_module_1_2')

        self.root_module.sub_module_1 = self.sub_module_1
        self.sub_module_1.sub_module_1_1 = self.sub_module_1_1
        self.sub_module_1.sub_module_1_2 = self.sub_module_1_2

    def test_valid_module_retrieval(self):
        # Act & Assert
        self.assertEqual(get_module(self.root_module, ['sub_module_1']), self.sub_module_1)
        self.assertEqual(get_module(self.root_module, ['sub_module_1', 'sub_module_1_1']), self.sub_module_1_1)
        self.assertEqual(get_module(self.root_module, ['sub_module_1', 'sub_module_1_2']), self.sub_module_1_2)

    def test_empty_sub_modules(self):
        # Act & Assert
        self.assertEqual(get_module(self.root_module, []), self.root_module)

    def test_invalid_module_argument(self):
        with self.assertRaises(ValueError) as cm:
            get_module(None, ['sub_module_1'])
        self.assertEqual(str(cm.exception), 'Argument `module` is required')

    def test_invalid_sub_modules_argument(self):
        with self.assertRaises(ValueError) as cm:
            get_module(self.root_module, 'sub_module_1')
        self.assertEqual(str(cm.exception), 'Argument `sub_modules` must be a list of strings')

    def test_non_existent_sub_module(self):
        with self.assertRaises(ValueError) as cm:
            get_module(self.root_module, ['sub_module_1', 'non_existent'])
        self.assertEqual(str(cm.exception), 'Module non_existent not found in sub_module_1')
