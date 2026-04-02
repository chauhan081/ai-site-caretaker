# AI Site Caretaker

CLI-first AI website/server caretaker for small businesses and agencies.

## Initial MVP scope
- Website health checks
- SSL expiry checks
- Server/process diagnostics
- Log reading and issue summaries
- Target config management
- Daily report generation
- Safe execution guardrails

## Planned structure
- `src/` core application code
- `config/` target definitions
- `docs/` product notes and roadmap
- `scripts/` helper scripts
- `tests/` automated tests

## Current commands
- `python -m src.main about`
- `python -m src.main check-site https://example.com`
- `python -m src.main check-ssl example.com`
- `python -m src.main check-server example.com --port 80`
