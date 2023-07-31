#!/usr/bin/env python

import json
import os
import PTN
import pytest


def load_json_file(file_name):
    with open(file_name) as input_file:
        return json.load(input_file)


def get_raw_data():
    json_input = os.path.join(os.path.dirname(__file__), "files/input.json")
    torrents = load_json_file(json_input)

    json_output = os.path.join(os.path.dirname(__file__), "files/output_raw.json")
    expected_results = load_json_file(json_output)

    return zip(torrents, expected_results)


def get_standard_data():
    json_input = os.path.join(os.path.dirname(__file__), "files/input.json")
    torrents = load_json_file(json_input)

    json_output = os.path.join(os.path.dirname(__file__), "files/output_standard.json")
    expected_results = load_json_file(json_output)

    return zip(torrents, expected_results)


total_excess = 0


@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    global total_excess
    total_excess = 0
    yield  # where testing happens
    print("\nExcess elements total: {}".format(total_excess))


@pytest.mark.parametrize("torrent,expected_result", get_raw_data())
def test_all_raw(torrent, expected_result):
    global total_excess
    result = PTN.parse(torrent, standardise=False)
    if "excess" in result:
        if isinstance(result["excess"], list):
            total_excess += len(result["excess"])
        else:
            total_excess += 1
    for key in expected_result:
        assert key in result, "'{}' was missing for \n{}".format(key, torrent)
        assert result[key] == expected_result[key], "'{}' failed for \n{}".format(
            key, torrent
        )
    for key in result.keys():
        if key not in ("encoder", "excess", "site"):  # Not needed in tests
            assert key in expected_result


@pytest.mark.parametrize("torrent,expected_result", get_standard_data())
def test_standardised(torrent, expected_result):
    result = PTN.parse(torrent, standardise=True)
    for key in expected_result:
        assert key in result, "'{}' was missing for \n{}".format(key, torrent)
        assert result[key] == expected_result[key], "'{}' failed for \n{}".format(
            key, torrent
        )
