#!/usr/bin/env python

import json
import os
import PTN
import pytest


def load_json_file(file_name):
    with open(file_name) as input_file:
        return json.load(input_file)


def get_test_data(file_name_input, file_name_output):
    json_input = os.path.join(os.path.dirname(__file__), file_name_input)
    torrents = load_json_file(json_input)

    json_output = os.path.join(os.path.dirname(__file__), file_name_output)
    expected_results = load_json_file(json_output)

    return list(zip(torrents, expected_results))


class TestTorrentParser:
    total_excess = 0

    @classmethod
    def setup_class(cls):
        cls.total_excess = 0

    @classmethod
    def teardown_class(cls):
        print(f"\nExcess elements total: {cls.total_excess}")

    @pytest.mark.parametrize("torrent,expected_result", get_test_data("files/input.json", "files/output_raw.json"))
    def test_all_raw(self, torrent, expected_result):
        print(f"Testing raw: {torrent}")
        print(f"Expected raw result: {expected_result}")
        result = PTN.parse(torrent, standardise=False)
        print(f"Parsed raw result: {result}")
        self._check_excess(result)
        self._assert_results(result, expected_result, torrent, check_extras=True)

    @pytest.mark.parametrize("torrent,expected_result", get_test_data("files/input.json", "files/output_standard.json"))
    def test_standardised(self, torrent, expected_result):
        print(f"Testing standardised: {torrent}")
        print(f"Expected standardised result: {expected_result}")
        result = PTN.parse(torrent, standardise=True)
        print(f"Parsed standardised result: {result}")
        self._assert_results(result, expected_result, torrent, check_extras=False)

    def _check_excess(self, result):
        if "excess" in result:
            if isinstance(result["excess"], list):
                self.total_excess += len(result["excess"])
            else:
                self.total_excess += 1

    def _assert_results(self, result, expected_result, torrent, check_extras):
        for key in expected_result:
            assert key in result, f"'{key}' was missing for \n{torrent}"
            assert result[key] == expected_result[key], f"'{key}' failed for \n{torrent}\nExpected: {expected_result[key]}\nFound: {result[key]}"

        if check_extras:
            # Check that there are no unexpected keys in the result for raw test cases
            unexpected_keys = set(result.keys()) - set(expected_result.keys()) - {"encoder", "excess", "site"}
            assert not unexpected_keys, f"Unexpected keys found in result for \n{torrent}: {unexpected_keys}"


if __name__ == "__main__":
    pytest.main()
