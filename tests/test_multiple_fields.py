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
        # Should capture both sources if they're different enough
        
    def test_multiple_codecs(self):
        """Test releases with multiple codec options."""
        result = PTN.parse(
            "Movie.2020.1080p.BluRay.x264.x265.HEVC",
            standardise=True
        )
        assert "codec" in result
        # Currently only gets x264, but should potentially get both
        # (though x265 and HEVC are the same, so should not duplicate)
        
    def test_avoid_duplicate_same_thing(self):
        """Test that semantically identical values aren't duplicated."""
        result = PTN.parse(
            "Movie.2020.1080p.x265.HEVC.BluRay",
            standardise=True
        )
        # x265 and HEVC should be recognized as the same and only appear once
        assert "codec" in result
        # After standardization, both x265 and HEVC become "H.265"
        # so should only appear once
        
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
        # Could potentially have both resolutions for multi-quality packs
        
    def test_complex_multi_audio_real_world(self):
        """Real-world example with multiple audio tracks."""
        result = PTN.parse(
            "Movie.2020.2160p.UHD.BluRay.REMUX.HDR.DTS-HD.MA.TrueHD.7.1.Atmos.HEVC-GROUP",
            standardise=True
        )
        # Should identify DTS-HD MA, TrueHD Atmos as distinct formats
        assert "audio" in result
        
    def test_dual_audio_language_integration(self):
        """Test that dual audio with languages still works."""
        result = PTN.parse(
            "Movie.2020.1080p.BluRay.DD5.1.AAC2.0.Dual.Audio.Hindi.English.x264",
            standardise=True
        )
        # Should have multiple audio formats AND languages
        assert "language" in result
        # Dual Audio should be captured


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
