"""
Edge TTS provider with pitch/volume/rate for Hermes Agent.

Works standalone (dev/testing) and integrates with Hermes
when installed via pip (entry-point ``hermes_agent.plugins``)
or copied to ``~/.hermes/plugins/edge-pitch/``.

Standalone usage:
    python -m edge_pitch "Hello" --voice es-ES-AlvaroNeural --pitch +30Hz
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from typing import Any

import edge_tts

from .i18n import _, init_i18n


# ── Config ────────────────────────────────────────────────────
def _load_config() -> dict[str, Any]:
    """Load config from Hermes, local config.yaml, or env vars."""
    # 1. Hermes
    try:
        from hermes_cli.config import load_config

        return load_config().get("tts", {}).get("edge-pitch", {})
    except Exception:
        pass

    # 2. env vars
    env = {
        "voice": os.environ.get("EDGE_PITCH_VOICE"),
        "pitch": os.environ.get("EDGE_PITCH_PITCH"),
        "volume": os.environ.get("EDGE_PITCH_VOLUME"),
        "rate": os.environ.get("EDGE_PITCH_RATE"),
        "lang": os.environ.get("EDGE_PITCH_LANG"),
    }
    return {k: v for k, v in env.items() if v is not None}


# ── TTSProvider base ──────────────────────────────────────────
# Try Hermes TTSProvider first; fall back to a standalone stub
# so the module is importable without Hermes installed.
try:
    from agent.tts_provider import TTSProvider as TTSProviderBase
except ImportError:
    TTSProviderBase = object  # standalone stub — EdgePitchProvider overrides everything


# ── Provider ──────────────────────────────────────────────────
class EdgePitchProvider(TTSProviderBase):
    """Edge TTS provider with pitch, volume, and rate control.

    Parameter precedence (highest first):
    1. ``**extra`` in synthesize()
    2. config.yaml / Hermes config (``tts.edge-pitch`` section)
    3. defaults
    """

    def __init__(self) -> None:
        self._cfg = _load_config()
        init_i18n(self._cfg)

    @property
    def name(self) -> str:
        return "edge-pitch"

    @property
    def display_name(self) -> str:
        return "Edge TTS (pitch + volume)"

    @property
    def voice_compatible(self) -> bool:
        return True

    def is_available(self) -> bool:
        try:
            import edge_tts  # noqa: F401

            return True
        except ImportError:
            return False

    def list_voices(self) -> list[dict[str, Any]]:
        """Return catalog of available Azure TTS voices."""

        async def _fetch() -> list[dict[str, Any]]:
            from edge_tts import VoicesManager

            voices = await VoicesManager.create()
            return [
                {
                    "id": v["ShortName"],
                    "display": v.get("FriendlyName", v["ShortName"]),
                    "language": v["Locale"],
                    "gender": v["Gender"].lower(),
                }
                for v in voices.voices
            ]

        try:
            return asyncio.run(_fetch())
        except Exception:
            return []

    def synthesize(
        self,
        text: str,
        output_path: str,
        *,
        voice: str | None = None,
        model: str | None = None,
        speed: float | None = None,
        format: str = "mp3",
        **extra: Any,
    ) -> str:
        assert format == "mp3", _("only_mp3", fmt=format)

        cfg = self._cfg
        pitch = extra.get("pitch") or cfg.get("pitch", "+0Hz")
        volume = extra.get("volume") or cfg.get("volume", "+0%")
        voice = voice or extra.get("voice") or cfg.get("voice", "es-ES-AlvaroNeural")

        if speed is not None:
            rate = f"{round((float(speed) - 1.0) * 100):+d}%"
        else:
            rate = extra.get("rate") or cfg.get("rate", "+0%")

        # asyncio.run() is safe here — text_to_speech_tool is synchronous.
        # The built-in Edge TTS provider in Hermes uses the same pattern,
        # optionally wrapped in ThreadPoolExecutor to avoid blocking the main loop.
        async def _run() -> None:
            comm = edge_tts.Communicate(
                text, voice, rate=rate, pitch=pitch, volume=volume
            )
            await comm.save(output_path)

        asyncio.run(_run())
        return output_path


# ── Entry point Hermes ────────────────────────────────────────
def register(ctx: Any) -> None:
    """Register the provider with Hermes (entry-point ``hermes_agent.plugins``)."""
    ctx.register_tts_provider(EdgePitchProvider())


# ── Standalone CLI ────────────────────────────────────────────
def main(argv: list[str] | None = None) -> None:
    init_i18n(_load_config())  # ensure language is set for CLI

    parser = argparse.ArgumentParser(description=_("cli_desc"))
    parser.add_argument("text", nargs="?", default=_("test_text"))
    parser.add_argument("--voice", default=None, help=_("voice_help"))
    parser.add_argument("--pitch", default=None, help=_("pitch_help"))
    parser.add_argument("--volume", default=None, help=_("volume_help"))
    parser.add_argument("--rate", default=None, help=_("rate_help"))
    parser.add_argument("--speed", type=float, default=None, help=_("speed_help"))
    parser.add_argument("--output", "-o", default=None, help=_("output_help"))

    args = parser.parse_args(argv)

    out = args.output or f"/tmp/edge_pitch_{os.getpid()}.mp3"
    kwargs: dict[str, Any] = {}
    if args.voice:
        kwargs["voice"] = args.voice
    if args.pitch:
        kwargs["pitch"] = args.pitch
    if args.volume:
        kwargs["volume"] = args.volume
    if args.rate:
        kwargs["rate"] = args.rate
    if args.speed is not None:
        kwargs["speed"] = args.speed

    provider = EdgePitchProvider()
    try:
        provider.synthesize(args.text, out, **kwargs)
        print(_("ok", path=out))
    except Exception as e:
        print(_("error", msg=e), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
