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

## Project structure
- `src/` core application code
- `config/` target definitions
- `docs/` product notes and roadmap
- `scripts/` helper scripts
- `tests/` automated tests

## Install / run
For local development:

```text
python -m src.main about
```

For an installable CLI:

```text
pip install -e .
ai-site-caretaker about
```

## Current commands
- `python -m src.main about`
- `python -m src.main check-site https://example.com`
- `python -m src.main check-ssl example.com`
- `python -m src.main check-server example.com --port 80`
- `python -m src.main read-logs path/to/app.log --lines 50`
- `python -m src.main daily-report example-site`
- `python -m src.main daily-report example-site --json`
- `python -m src.main daily-report example-site --json --output reports/example-site.json`
- `python -m src.main diagnose-target example-site`
- `python -m src.main diagnose-target example-site --json`
- `python -m src.main diagnose-target example-site --output reports/example-site-diagnosis.txt`
- `ai-site-caretaker about` (after `pip install -e .`)

## Config
Create `config/targets.json` using `config/targets.example.json` as a template:

```json
{
  "targets": [
    {
      "name": "example-site",
      "url": "https://example.com",
      "host": "example.com",
      "checks": ["site", "ssl", "server"],
      "server_ports": [80, 443],
      "log_paths": ["/var/log/nginx/error.log"],
      "notes": "Default starter target"
    }
  ]
}
```

### Config fields
- `checks`: choose from `site`, `ssl`, `server`, `logs`
- `server_ports`: run the server check against multiple ports
- `log_paths`: inspect one or more log files during report generation
- If `checks` is omitted, the default flow is `site + ssl + server`

## Example output
### Text report
```text
python -m src.main daily-report example-site
```

Produces output like:

```text
Overall severity: INFO

- [OK] check-site | severity=info | HTTP 200 from https://example.com
- [OK] check-ssl | severity=info | SSL valid for 89 day(s) on example.com
- [OK] check-server | severity=info | TCP connection to example.com:80 succeeded
```

### Exporting reports
Both aggregate commands can write their rendered output to disk:

```text
python -m src.main daily-report example-site --json --output reports/example-site.json
python -m src.main diagnose-target example-site --output reports/example-site-diagnosis.txt
```

Supported export formats are `.json` and `.txt`. Parent folders are created automatically.

### JSON diagnosis
```text
python -m src.main diagnose-target example-site --json
```

Produces structured output like:

```json
{
  "overall_severity": "info",
  "results": [
    {
      "name": "check-site",
      "ok": true,
      "summary": "HTTP 200 from https://example.com",
      "details": {
        "status": 200,
        "final_url": "https://example.com"
      },
      "severity": "info"
    }
  ],
  "diagnosis": {
    "healthy": true,
    "summary": "All monitored checks look healthy.",
    "failed_checks": [],
    "probable_causes": [],
    "recommended_actions": [],
    "overall_severity": "info"
  }
}
```

## Current progress
- Core CLI scaffold is working
- Health checks implemented: site, SSL, server
- Target config loading added
- Log tail reader added
- Daily report flow added
- Diagnosis flow and target validation added
- Severity tagging and report summary formatting added
- Structured JSON output added for aggregate report/diagnosis commands
- Automated `unittest` coverage currently passing for the implemented modules

## Status
- Latest pushed commit: `feat: add diagnosis flow and target validation`
- Repo: `<https://github.com/chauhan081/ai-site-caretaker>`
- Current local focus: README synced with the latest reporting/output behavior
