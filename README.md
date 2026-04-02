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
- `python -m src.main read-logs path/to/app.log --lines 50`
- `python -m src.main daily-report example-site`
- `python -m src.main diagnose-target example-site`

## Current progress
- Core CLI scaffold is working
- Health checks implemented: site, SSL, server
- Target config loading added
- Log tail reader added
- Daily report flow added
- Diagnosis flow and target validation added
- Severity tagging and report summary formatting added
- Automated `unittest` coverage currently passing for the implemented modules

## Current status
- Latest pushed commit: `feat: add diagnosis flow and target validation`
- Repo: `<https://github.com/chauhan081/ai-site-caretaker>`
- Current local block: severity tagging, better reporting output, and README sync
