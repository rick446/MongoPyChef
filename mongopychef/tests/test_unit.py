import sys
from unittest import TestCase

from ming import schema as S

from mongopychef.lib import validators as V

class TestNumVersions(TestCase):

    def setUp(self):
        self.val = V.NumVersions(if_missing=1)

    def test_missing(self):
        self.assertEqual(self.val.validate(S.Missing), 1)

    def test_all(self):
        self.assertEqual(self.val.validate('all'), sys.maxint)
        
    def test_normal(self):
        self.assertEqual(self.val.validate(42), 42)

    def test_invalid(self):
        self.assertRaises(S.Invalid, self.val.validate, 'None')
        
