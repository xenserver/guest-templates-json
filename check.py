#!/usr/bin/env python3
import unittest
from guesttemplates import loader

class MockLoader(loader.Loader):
    def __init__(self):
        self._confs = {}
        self._by_uuid = {}
        self._by_reflabel = {}

class TestLoader(unittest.TestCase):
    def test_load_templates(self):
        """Tests that the templates can be loaded and converted to XML successfully."""

        loader = MockLoader()
        loader.find_config_files("json/")

        # Loading templates can fail if inconsistencies are found (e.g. uefi and device-model)
        loader.load_templates()

        # Check that we were able to load some templates successfully
        # The exact number depends on how many base templates there are that are skipped.
        self.assertLessEqual(len(loader._by_uuid), len(loader._confs))
        self.assertGreaterEqual(len(loader._by_uuid), 3)

        for i in loader._by_uuid.values():
            i.toxml({})

if __name__ == '__main__':
    unittest.main()
