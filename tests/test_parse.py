#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import unittest

import PTN


class ParseTest(unittest.TestCase):
    def test_all_raw(self):
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

    def test_standardised(self):
        inputs_with_expected = [
            ('Interstellar (2014) CAM ENG x264 AAC-CPG',
             {'codec': 'H.264'}),
            ('The French Connection (1971) Remastered 1080p BluRay x265 HEVC EAC3-SARTRE',
             {'codec': 'H.265', 'audio': 'Dolby Digital Plus'}),
            ('Boku.Unmei.no.Hito.desu.Ep07.Chi_Jap.HDTVrip.1280X720-ZhuixinFan.mp4',
             {'resolution': '720p', 'container': 'MP4'}),
            ('Brave.2012.R5.DVDRip.XViD.LiNE-UNiQUE',
             {'codec': 'Xvid', 'audio': 'LiNE'}),
            ('X-Men.Days.of.Future.Past.2014.1080p.WEB-DL.DD5.1.H264-RARBG',
             {'codec': 'H.264', 'audio': 'Dolby Digital 5.1'}),
            ('Annabelle.2014.1080p.PROPER.HC.WEBRip.x264.AAC.2.0-RARBG',
             {'codec': 'H.264', 'audio': 'AAC 2.0'}),
            ('Lucy 2014 Dual-Audio 720p WEBRip',
             {'audio': 'Dual Audio'}),
            ('Ant-Man.2015.3D.1080p.BRRip.Half-SBS.x264.AAC-m2g',
             {'codec': 'H.264', 'audio': 'AAC', 'sbs': 'Half SBS'}),
            ('Dawn.Of.The.Planet.of.The.Apes.2014.1080p.WEB-DL.DD51.H264-RARBG',
             {'codec': 'H.264', 'audio': 'Dolby Digital 5.1'})
        ]

        for test in inputs_with_expected:
            input = test[0]
            expected = test[1]
            print("Test: {}\nin {}\n".format(expected, input))
            result = PTN.parse(input, keep_raw=False)
            for key in expected:
                self.assertIn(key, result)
                self.assertEqual(expected[key], result[key], key)


if __name__ == '__main__':
    unittest.main()
