#!/usr/bin/env python2
import unittest
from guesttemplates import loader

class MockLoader(loader.Loader):
    def __init__(self):
        self._confs = {}
        self._by_uuid = {}
        self._by_reflabel = {}

class TestLoader(unittest.TestCase):
    def test_load_templates(self):
        loader = MockLoader()
        loader.find_config_files("json/")
        loader.load_templates()
        self.assertLessEqual(len(loader._by_uuid), len(loader._confs))
        self.assertGreaterEqual(len(loader._by_uuid), 3)

        for i in loader._by_uuid.itervalues():
            i.toxml({})

if __name__ == '__main__':
    unittest.main()
