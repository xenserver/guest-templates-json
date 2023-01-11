#!/usr/bin/env python3
import glob
import json
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

        all_uuids = []
        all_reflabels = []
        for i in glob.glob("json/*"):
            with open(i, 'r') as f:
                template = json.load(f)
                if 'uuid' in template:
                    all_uuids.append(template['uuid'])
                if 'reference_label' in template:
                    all_reflabels.append(template['reference_label'])

        self.assertEqual(sorted(loader._by_uuid.keys()), sorted(all_uuids))
        self.assertEqual(sorted(loader._by_reflabel.keys()), sorted(all_reflabels))


if __name__ == '__main__':
    unittest.main()
