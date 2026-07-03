"""Lightweight i18n for edge-pitch plugin messages.

Usage:
    from .i18n import init_i18n, _

    init_i18n({"lang": "es"})
    print(_("ok", path="/tmp/out.mp3"))
"""

from __future__ import annotations

from typing import Any

_MESSAGES: dict[str, dict[str, str]] = {
    "en": {
        "only_mp3": "edge-tts outputs MP3 only. Hermes converts to Opus for voice bubbles when voice_compatible=True, not '{fmt}'",
        "ok": "OK → {path}",
        "error": "ERROR: {msg}",
        "cli_desc": "Edge TTS — synthesize text with pitch, volume, and rate control",
        "voice_help": "Voice (e.g. es-ES-AlvaroNeural)",
        "pitch_help": "Pitch (e.g. +0Hz, -30Hz, +50Hz)",
        "volume_help": "Volume (e.g. +0%, -50%, +50%)",
        "rate_help": "Rate (e.g. +0%, -20%, +50%)",
        "speed_help": "Speed multiplier (1.0=normal, 1.5=+50%%)",
        "output_help": "Output file (default: /tmp/edge_pitch_*.mp3)",
        "test_text": "Hello, this is a test of synthetic speech.",
    },
    "es": {
        "only_mp3": "edge-tts solo genera MP3. Hermes convierte a Opus para voice bubbles si voice_compatible=True, no '{fmt}'",
        "ok": "OK → {path}",
        "error": "ERROR: {msg}",
        "cli_desc": "Edge TTS — sintetiza texto con control de pitch, volume y rate",
        "voice_help": "Voz (ej: es-ES-AlvaroNeural)",
        "pitch_help": "Tono (ej: +0Hz, -30Hz, +50Hz)",
        "volume_help": "Volumen (ej: +0%, -50%, +50%)",
        "rate_help": "Velocidad (ej: +0%, -20%, +50%)",
        "speed_help": "Velocidad como multiplicador (1.0=normal, 1.5=+50%%)",
        "output_help": "Archivo de salida (default: /tmp/edge_pitch_*.mp3)",
        "test_text": "Hola, esto es una prueba de voz sintética.",
    },
}

_lang: str = "en"


def init_i18n(cfg: dict[str, Any]) -> None:
    """Set language from config (key ``lang``, default ``"en"``)."""
    global _lang
    _lang = cfg.get("lang", "en")


def _(key: str, **kw: Any) -> str:
    """Translate ``key`` with optional format kwargs, falling back to key itself."""
    msg = _MESSAGES.get(_lang, _MESSAGES["en"]).get(key, key)
    return msg.format(**kw) if kw else msg
