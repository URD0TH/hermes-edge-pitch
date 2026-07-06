# hermes-edge-pitch

[🇬🇧 English](https://github.com/URD0TH/hermes-edge-pitch/blob/main/README.md)

Plugin de [Hermes Agent](https://github.com/NousResearch/hermes-agent) que agrega un proveedor TTS personalizado de [edge-tts](https://github.com/rany2/edge-tts) con control completo de **pitch** (tono), **volume** (volumen) y **rate** (velocidad).

---

## Requisitos

- Python ≥ 3.10
- [Hermes Agent](https://github.com/NousResearch/hermes-agent) instalado
- [edge-tts](https://github.com/rany2/edge-tts) (se instala automáticamente como dependencia pip)
- Conexión a internet (edge-tts consume la API de Azure Cognitive Services)

## Instalación

### Opción 1: Pip 

```sh
cd ruta/del/repo
pip install -e .
hermes gateway restart
hermes plugins list
# → edge-pitch  ✓ enabled
```

### Opción 2: Git (recomendada)

```sh
hermes plugins install https://github.com/URD0TH/hermes-edge-pitch --enable
hermes gateway restart
# o si no usaste --enable:
hermes plugins enable edge-pitch
hermes gateway restart
```

### Opción 3: Copia directa

```sh
cp -r ruta/del/repo ~/.hermes/plugins/edge-pitch
hermes plugins enable edge-pitch
hermes gateway restart
```

### Opción 4: Standalone (pruebas sin Hermes)

```sh
cd ruta/del/repo
pip install edge-tts
python -m edge_pitch "Hola mundo" --pitch +30Hz --volume +20% --rate +10%
```

## Configuración

En `~/.hermes/config.yaml`:

```yaml
tts:
  provider: edge-pitch
  edge-pitch:
    voice: es-ES-AlvaroNeural
    pitch: "+5Hz"
    volume: "+0%"
    rate: "+0%"
```

### Parámetros de `edge-pitch`

| Parámetro | Formato | Rango | Default | Descripción |
|-----------|---------|-------|---------|-------------|
| `voice`   | `es-ES-AlvaroNeural` | — | `es-ES-AlvaroNeural` | Voz de Azure TTS |
| `pitch`   | `±NHz` | `-100Hz` a `+100Hz` | `+0Hz` | Tono de la voz |
| `volume`  | `±N%`  | `-100%` a `+100%` | `+0%` | Volumen |
| `rate`    | `±N%`  | `-100%` a `+100%` | `+0%` | Velocidad (formato edge-tts nativo) |
| `lang`    | `en` / `es` | — | `en` | Idioma de mensajes del plugin |

### `speed` vs `rate` — dos formas de controlar la velocidad

El plugin acepta **dos vías mutuamente excluyentes**:

| Vía | Dónde se define | Formato | Ejemplo |
|-----|----------------|---------|---------|
| `speed` | `tts.speed` en config global (lo pasa el dispatcher de Hermes) | Multiplicador float | `1.0` = normal, `1.5` = +50%, `0.95` = -5%, `0.5` = -50% |
| `rate` | `tts.edge-pitch.rate` en config del plugin | Cadena `±N%` | `"+0%"` = normal, `"-5%"` = -5%, `"+50%"` = +50% |

**Regla:** si el dispatcher pasa `speed` (lo hace si está definido en `config.yaml`), el plugin **convierte** `speed` a formato `±N%` y **ignora** `rate` completamente. Si `speed` no está definido, usa `rate` directamente.

| ❌ Incorrecto | ✅ Correcto (usando rate) | ✅ Correcto (usando speed) |
|---|---|---|
| `speed: 1.0` + `rate: "-5%"` | `rate: "-5%"` (sin speed) | `speed: 0.95` (sin rate) |
| `speed: 1.0` → fuerza `+0%` | `rate: "-5%"` → -5% real | `speed: 0.95` → -5% real |

**En resumen:** usa `rate` si quieres control fino, usa `speed` si quieres el estándar multiplicador de Hermes. **Nunca ambos.**

### Precedencia de parámetros

1. `**extra` — parámetros directos en `synthesize()` (usado por dispatcher)
2. Config — sección `edge-pitch` en `config.yaml`
3. Defaults — valores fijos del plugin

## Verificación

```sh
hermes plugins list
# edge-pitch  ✓ enabled

# Con logs detallados
HERMES_PLUGINS_DEBUG=1 hermes plugins list
```

## Tests

```sh
cd ruta/del/repo
pip install edge-tts
pytest tests/ -v
```

## Enlaces

| Recurso | URL |
|---------|-----|
| Hermes Agent | https://github.com/NousResearch/hermes-agent |
| edge-tts | https://github.com/rany2/edge-tts |
| DeepWiki (guía de plugins Hermes) | https://deepwiki.com/wiki/NousResearch/hermes-agent#10.7 |
| DeepWiki (TTS en Hermes) | https://deepwiki.com/wiki/NousResearch/hermes-agent#11 |
| DeepWiki | https://deepwiki.com |

## Estructura del proyecto

```
├── __init__.py               # re-export para install por directorio
├── plugin.yaml               # metadatos Hermes
├── pyproject.toml            # pip install + entry-point hermes_agent.plugins
├── config.example.yaml       # guía de configuración
├── .gitignore
├── .python-version
├── edge_pitch/
│   └── __init__.py           # código fuente del provider + register() + CLI
└── tests/
    └── test_provider.py      # tests pytest
```
