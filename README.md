# hermes-edge-pitch

[🇪🇸 Español](https://github.com/URD0TH/hermes-edge-pitch/blob/main/README.es.md)

Plugin for [Hermes Agent](https://github.com/NousResearch/hermes-agent) that adds a custom TTS provider using [edge-tts](https://github.com/rany2/edge-tts) with full control over **pitch**, **volume**, and **rate**.

---

## Requirements

- Python ≥ 3.10
- [Hermes Agent](https://github.com/NousResearch/hermes-agent) installed
- [edge-tts](https://github.com/rany2/edge-tts) (installed automatically as a pip dependency)
- Internet connection (edge-tts uses the Azure Cognitive Services API)

## Installation

### Option 1: Pip 

```sh
cd /path/to/repo
pip install -e .
hermes gateway restart
hermes plugins list
# → edge-pitch  ✓ enabled
```

### Option 2: Git (recommended)

```sh
hermes plugins install https://github.com/URD0TH/hermes-edge-pitch --enable
hermes gateway restart
# or if you didn't use --enable:
hermes plugins enable edge-pitch
hermes gateway restart
```

### Option 3: Directory copy

```sh
cp -r /path/to/repo ~/.hermes/plugins/edge-pitch
hermes plugins enable edge-pitch
hermes gateway restart
```

### Option 4: Standalone (testing without Hermes)

```sh
cd /path/to/repo
pip install edge-tts
python -m edge_pitch "Hello world" --pitch +30Hz --volume +20% --rate +10%
```

## Configuration

In `~/.hermes/config.yaml`:

```yaml
tts:
  provider: edge-pitch
  edge-pitch:
    voice: es-ES-AlvaroNeural
    pitch: "+5Hz"
    volume: "+0%"
    rate: "+0%"
```

### `edge-pitch` parameters

| Parameter | Format | Range | Default | Description |
|-----------|--------|-------|---------|-------------|
| `voice`   | `es-ES-AlvaroNeural` | — | `es-ES-AlvaroNeural` | Azure TTS voice |
| `pitch`   | `±NHz` | `-100Hz` to `+100Hz` | `+0Hz` | Voice pitch |
| `volume`  | `±N%`  | `-100%` to `+100%` | `+0%` | Volume |
| `rate`    | `±N%`  | `-100%` to `+100%` | `+0%` | Speed (native edge-tts format) |
| `lang`    | `en` / `es` | — | `en` | Plugin messages language |

### `speed` vs `rate` — two ways to control speed

The plugin accepts **two mutually exclusive paths**:

| Path | Where it's defined | Format | Example |
|------|-------------------|--------|---------|
| `speed` | `tts.speed` in global config (passed by Hermes dispatcher) | Float multiplier | `1.0` = normal, `1.5` = +50%, `0.95` = -5%, `0.5` = -50% |
| `rate` | `tts.edge-pitch.rate` in plugin config | `±N%` string | `"+0%"` = normal, `"-5%"` = -5%, `"+50%"` = +50% |

**Rule:** if the dispatcher passes `speed` (it does when defined in `config.yaml`), the plugin **converts** `speed` to `±N%` format and **ignores** `rate` entirely. If `speed` is not defined, it uses `rate` directly.

| ❌ Wrong | ✅ Correct (using rate) | ✅ Correct (using speed) |
|---|---|---|
| `speed: 1.0` + `rate: "-5%"` | `rate: "-5%"` (no speed) | `speed: 0.95` (no rate) |
| `speed: 1.0` → forces `+0%` | `rate: "-5%"` → actual -5% | `speed: 0.95` → actual -5% |

**TL;DR:** use `rate` for fine-grained control, use `speed` for the standard Hermes multiplier. **Never both.**

### Parameter precedence

1. `**extra` — direct parameters in `synthesize()` (used by dispatcher)
2. Config — `edge-pitch` section in `config.yaml`
3. Defaults — plugin hardcoded values

## Verification

```sh
hermes plugins list
# edge-pitch  ✓ enabled

# With detailed logs
HERMES_PLUGINS_DEBUG=1 hermes plugins list
```

## Tests

```sh
cd /path/to/repo
pip install edge-tts
pytest tests/ -v
```

## Links

| Resource | URL |
|----------|-----|
| Hermes Agent | https://github.com/NousResearch/hermes-agent |
| edge-tts | https://github.com/rany2/edge-tts |
| DeepWiki (Hermes plugins guide) | https://deepwiki.com/wiki/NousResearch/hermes-agent#10.7 |
| DeepWiki (TTS in Hermes) | https://deepwiki.com/wiki/NousResearch/hermes-agent#11 |
| DeepWiki | https://deepwiki.com |

## Project structure

```
├── __init__.py               # re-export for directory-based install
├── plugin.yaml               # Hermes metadata
├── pyproject.toml            # pip install + entry-point hermes_agent.plugins
├── config.example.yaml       # configuration guide
├── .gitignore
├── .python-version
├── edge_pitch/
│   └── __init__.py           # provider source code + register() + CLI
└── tests/
    └── test_provider.py      # pytest tests
```
