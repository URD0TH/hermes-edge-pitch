"""Minimal tests for edge-pitch provider.

Requires: pip install -e .  (or uv sync && uv run pytest tests/)
"""

from __future__ import annotations

from edge_pitch import EdgePitchProvider


def test_provider_name() -> None:
    p = EdgePitchProvider()
    assert p.name == "edge-pitch"
    assert p.display_name == "Edge TTS (pitch + volume)"
    assert p.voice_compatible is True


def test_provider_rejects_non_mp3() -> None:
    p = EdgePitchProvider()
    try:
        p.synthesize("hola", "/tmp/test_edge_pitch.wav", format="wav")
        assert False, "should have raised AssertionError"
    except AssertionError as e:
        assert "MP3" in str(e)


def test_provider_accepts_params_via_extra() -> None:
    """Verify **extra accepts pitch/volume/rate."""
    p = EdgePitchProvider()
    kwargs = dict(
        text="test",
        output_path="/tmp/_edge_pitch_extra_test.mp3",
        voice="es-ES-AlvaroNeural",
        pitch="+30Hz",
        volume="-20%",
        rate="+10%",
    )
    try:
        p.synthesize(**kwargs)
    except Exception as exc:
        msg = str(exc).lower()
        assert any(
            kw in msg
            for kw in (
                "connection",
                "connect",
                "reach",
                "dns",
                "timeout",
                "refused",
                "no route",
            )
        ), f"Unexpected failure (not a network error): {exc}"


def test_speed_zero_does_not_crash() -> None:
    """speed=0 produces -100% — formatting must not crash."""
    p = EdgePitchProvider()
    try:
        p.synthesize("x", "/tmp/_edge_pitch_zero_test.mp3", speed=0.0)
    except Exception as exc:
        msg = str(exc).lower()
        if not any(kw in msg for kw in ("connection", "connect", "reach")):
            raise


def test_list_voices_returns_list() -> None:
    """list_voices() returns a list of voice dicts (may be empty if offline)."""
    p = EdgePitchProvider()
    voices = p.list_voices()
    assert isinstance(voices, list)
    if voices:
        v = voices[0]
        assert "id" in v
        assert "display" in v
        assert "language" in v
