#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import unittest

import PTN


class ParseTest(unittest.TestCase):
    def test_parser(self):
        json_input = os.path.join(os.path.dirname(__file__), 'files/input.json')
        with open(json_input) as input_file:
            torrents = json.load(input_file)

        json_output = os.path.join(os.path.dirname(__file__), 'files/output.json')
        with open(json_output) as output_file:
            expected_results = json.load(output_file)

        self.assertEqual(len(torrents), len(expected_results))

        for torrent, expected_result in zip(torrents, expected_results):
            print("Test: " + torrent)
            result = PTN.parse(torrent, keep_raw=True)
            for key in expected_result:
                self.assertIn(key, result)
                self.assertEqual(expected_result[key], result[key], key)
            for key in result.keys():
                if key not in ('group', 'excess', 'encoder'):  # Not needed in tests
                    self.assertIn(key, expected_result)


if __name__ == '__main__':
    unittest.main()
