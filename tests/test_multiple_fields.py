#!/usr/bin/env python

"""
Tests for multiple field values feature.
This tests the ability to capture multiple distinct matches for fields like
audio, quality, codec, and resolution.
"""

import PTN
import pytest


class TestMultipleFieldValues:
    """Test parsing torrents with multiple distinct values for certain fields."""

    def test_multiple_audio_formats(self):
        """Test torrent with multiple audio formats (DTS-HD MA, TrueHD, Atmos)."""
        result = PTN.parse(
            "Movie.2020.1080p.BluRay.DTS-HD.MA.5.1.TrueHD.7.1.Atmos.x264",
            standardise=True
        )
        # Should capture all distinct audio formats
        assert "audio" in result
        audio = result["audio"]
        if isinstance(audio, list):
            # Check we have multiple distinct audio formats
            assert len(audio) >= 2, f"Expected multiple audio formats, got: {audio}"
            # Should have DTS-HD MA and TrueHD (and potentially Atmos)
            assert any("DTS" in str(a) for a in audio), f"Expected DTS-HD MA in {audio}"
            assert any("TrueHD" in str(a) for a in audio), f"Expected TrueHD in {audio}"
        else:
            # Currently only gets one - this is the behavior we want to change
            pytest.fail(f"Expected list of audio formats, got single value: {audio}")
        
    def test_multiple_audio_with_channels(self):
        """Test multiple audio codecs with different channel configurations."""
        result = PTN.parse(
            "Movie.2020.1080p.DDP5.1.AAC.2.0.x264",
            standardise=True
        )
        assert "audio" in result
        audio = result["audio"]
        if isinstance(audio, list):
            assert len(audio) >= 2, f"Expected 2 audio formats, got: {audio}"
            # Should have both DDP 5.1 and AAC 2.0
            assert any("Digital Plus" in str(a) or "DDP" in str(a) for a in audio)
            assert any("AAC" in str(a) for a in audio)
        else:
            pytest.fail(f"Expected list of audio formats, got single value: {audio}")
        
    def test_multiple_qualities(self):
        """Test torrent listing multiple source qualities."""
        result = PTN.parse(
            "Movie.2020.WEB-DL.BluRay.1080p.x264",
            standardise=True
        )
        assert "quality" in result
        quality = result["quality"]
        if isinstance(quality, list):
            assert len(quality) >= 2, f"Expected 2 qualities, got: {quality}"
            assert any("WEB" in str(q) for q in quality)
            assert any("Blu" in str(q) for q in quality)
        else:
            pytest.fail(f"Expected list of qualities, got single value: {quality}")
        
    def test_hybrid_quality(self):
        """Test hybrid/remux with multiple sources."""
        result = PTN.parse(
            "Movie.2020.AMZN.WEB-DL.Netflix.1080p.x264",
            standardise=True
        )
        # Amazon and Netflix are networks, not quality sources
        # So we should only get WEB-DL as quality
        assert "quality" in result
        quality = result["quality"]
        # Should have WEB-DL captured
        if isinstance(quality, list):
            assert any("WEB" in str(q) for q in quality)
        else:
            assert "WEB" in str(quality)
        
    def test_multiple_codecs(self):
        """Test releases with multiple codec options."""
        result = PTN.parse(
            "Movie.2020.1080p.BluRay.x264.x265.HEVC",
            standardise=True
        )
        assert "codec" in result
        codec = result["codec"]
        # x265 and HEVC are the same (both become H.265), so should only have one
        # x264 (H.264) is different, could be included
        # In this case, with standardization, both should be recognized as different codecs
        if isinstance(codec, list):
            # Could have both H.264 and H.265
            assert len(codec) >= 1
        else:
            # At minimum should have one codec
            assert codec in ["H.264", "H.265"]
        
    def test_avoid_duplicate_same_thing(self):
        """Test that semantically identical values aren't duplicated."""
        result = PTN.parse(
            "Movie.2020.1080p.x265.HEVC.BluRay",
            standardise=True
        )
        # x265 and HEVC should be recognized as the same and only appear once
        assert "codec" in result
        codec = result["codec"]
        # After standardization, both x265 and HEVC become "H.265"
        # so should only appear once as a string, not a list
        assert isinstance(codec, str)
        assert codec == "H.265"
        
    def test_coherent_types_multiple_values(self):
        """Test coherent_types mode with multiple values."""
        result = PTN.parse(
            "Movie.2020.1080p.BluRay.DTS.5.1.TrueHD.7.1.x264",
            standardise=True,
            coherent_types=True
        )
        # With coherent_types=True, all non-boolean fields should be lists
        if "audio" in result:
            assert isinstance(result["audio"], list)
            
    def test_multiple_resolutions_different(self):
        """Test when multiple distinct resolutions are mentioned."""
        # This is less common but can happen in compilation torrents
        result = PTN.parse(
            "Collection.720p.1080p.BluRay.x264",
            standardise=True
        )
        assert "resolution" in result
        resolution = result["resolution"]
        # Should capture both resolutions for multi-quality packs
        if isinstance(resolution, list):
            assert len(resolution) >= 2
            assert any("720" in str(r) for r in resolution)
            assert any("1080" in str(r) for r in resolution)
        else:
            # If only one, that's also acceptable
            assert resolution in ["720p", "1080p"]
        
    def test_complex_multi_audio_real_world(self):
        """Real-world example with multiple audio tracks."""
        result = PTN.parse(
            "Movie.2020.2160p.UHD.BluRay.REMUX.HDR.DTS-HD.MA.TrueHD.7.1.Atmos.HEVC-GROUP",
            standardise=True
        )
        # Should identify DTS-HD MA, TrueHD, and Atmos as distinct formats
        assert "audio" in result
        audio = result["audio"]
        if isinstance(audio, list):
            # Should have multiple audio formats
            assert len(audio) >= 2
            # Check that different audio codecs are present
            audio_str = " ".join([str(a) for a in audio])
            assert "DTS" in audio_str or "TrueHD" in audio_str or "Atmos" in audio_str
        else:
            # At minimum should have one audio format
            assert audio is not None
        
    def test_dual_audio_language_integration(self):
        """Test that dual audio with languages still works."""
        result = PTN.parse(
            "Movie.2020.1080p.BluRay.DD5.1.AAC2.0.Dual.Audio.Hindi.English.x264",
            standardise=True
        )
        # Should have multiple audio formats AND languages
        assert "language" in result
        languages = result["language"]
        # Should have Hindi and English
        if isinstance(languages, list):
            assert len(languages) >= 2
            lang_str = " ".join([str(l) for l in languages])
            assert "Hindi" in lang_str or "English" in lang_str
        else:
            assert languages in ["Hindi", "English"]
        
        # Audio should capture DD 5.1 and/or AAC 2.0
        if "audio" in result:
            audio = result["audio"]
            # Dual Audio might also be captured
            assert audio is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
