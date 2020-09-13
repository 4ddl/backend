# Create your tests here.
from django.test import TestCase

from problem import utils


class ProblemTestCase(TestCase):
    def test_manifest_true(self):
        manifest = {
            "spj": False,
            "hash": "a64ea2a1465776358bf077ef49d215c1947757ad022ab8061ac989309c2b8d44",
            "test_cases": [
                {"in": "1.in", "out": "1.out"},
                {"in": "2.in", "out": "2.out"}
            ]}
        self.assertIsNotNone(utils.validate_manifest(manifest))
