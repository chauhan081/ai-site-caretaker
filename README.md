# AI Site Caretaker

CLI-first AI website/server caretaker for small businesses and agencies.

## Initial MVP scope
- Website health checks
- SSL expiry checks
- Server/process diagnostics
- Log reading with severity-aware summaries and recurring-pattern grouping
- Target config management
- Daily report generation
- Notification-friendly output plus practical CLI delivery integrations
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
  - surfaces error/warning counts, recurring patterns, and sample matching lines
- `python -m src.main daily-report example-site`
- `python -m src.main daily-report example-site --json`
- `python -m src.main daily-report example-site --alerts-only`
- `python -m src.main daily-report example-site --min-severity high --output reports/example-site-alerts.txt`
- `python -m src.main daily-report example-site --notify-format text --notify-target ops-email`
- `python -m src.main daily-report example-site --notify-format json --output reports/example-site-notify.json`
- `python -m src.main diagnose-target example-site`
- `python -m src.main diagnose-target example-site --json`
- `python -m src.main diagnose-target example-site --alerts-only --min-severity medium`
- `python -m src.main diagnose-target example-site --notify-format text --notify-target slack-webhook`
- `python -m src.main diagnose-target example-site --notify-format json --output reports/example-site-diagnosis-notify.json`
- `python -m src.main daily-report example-site --alerts-only --notify-format text --notify-target local-file --deliver`
- `python -m src.main diagnose-target example-site --notify-format json --notify-target slack-webhook --deliver`
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
      "checks": ["site", "ssl", "server", "logs"],
      "server_ports": [80, 443],
      "log_paths": ["/var/log/nginx/error.log"],
      "notification_targets": [
        {
          "name": "ops-email",
          "type": "email",
          "destination": "ops@example.com",
          "min_severity": "high",
          "enabled": true
        }
      ],
      "notes": "Default starter target"
    }
  ]
}
```

### Config fields
- `checks`: choose from `site`, `ssl`, `server`, `logs`
- `server_ports`: run the server check against multiple ports
- `log_paths`: inspect one or more log files during report generation
- `notification_targets`: optional named delivery definitions for email/webhook/stdout/slack-style destinations
  - `name`: lookup key for `--notify-target`
  - `type`: one of `email`, `webhook`, `stdout`, `file`, `slack`
  - `destination`: address, URL, stream name (`stdout`/`stderr`), or local file path depending on type
  - `min_severity`: optional future-facing routing hint stored in the payload
  - `enabled`: optional boolean flag for config hygiene
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
- [OK] check-server:80 | severity=info | TCP connection to example.com:80 succeeded
```

### Alert-focused output
Both aggregate commands support alert filtering before rendering or exporting:

```text
python -m src.main daily-report example-site --alerts-only
python -m src.main daily-report example-site --min-severity high
python -m src.main diagnose-target example-site --alerts-only --min-severity medium
```

- `--alerts-only` keeps only failed checks
- `--min-severity` keeps checks at or above `low`, `medium`, `high`, or `critical`
- If no checks match the filter, diagnosis output reports that the alert filter matched nothing

### Notification-friendly output
Both aggregate commands can emit compact alert text or structured JSON, and can optionally deliver that payload when you explicitly add `--deliver`:

```text
python -m src.main daily-report example-site --alerts-only --notify-format text --notify-target ops-email
python -m src.main diagnose-target example-site --min-severity high --notify-format json --output reports/example-site-notify.json
```

- `--notify-format text` emits a compact, message-ready alert body
- `--notify-format json` emits a structured payload containing source command, target, health, severity, results, optional diagnosis, and optional delivery-target metadata
- `--notify-target` looks up metadata from `notification_targets` in config
- `--deliver` is opt-in and performs the real delivery step for `webhook`, `slack`, `stdout`, or `file` targets
- `email` targets remain metadata-only for now; using `--deliver` with an email target fails fast with a clear message
- delivery respects each target's `enabled` flag and `min_severity` threshold
- `--json` and `--notify-format` are mutually exclusive to keep output shapes predictable

### Exporting reports
Both aggregate commands can write their rendered output to disk, including alert-filtered and notification-oriented output:

```text
python -m src.main daily-report example-site --json --output reports/example-site.json
python -m src.main daily-report example-site --alerts-only --output reports/example-site-alerts.txt
python -m src.main daily-report example-site --notify-format json --output-dir reports --timestamped
python -m src.main diagnose-target example-site --alerts-only --min-severity medium --output reports/example-site-diagnosis.json
```

Supported export formats are `.json` and `.txt`. Parent folders are created automatically.
Use `--output-dir` to let the CLI generate filenames like `example-site-daily-report-20260403-103045.json` for scheduled runs.
Use `--timestamped` with `--output` to preserve a chosen base name while still avoiding overwrites.

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
- Log tail reader added with recurring-pattern summaries
- Daily report flow added
- Diagnosis flow and target validation added
- Severity tagging and report summary formatting added
- Structured JSON output added for aggregate report/diagnosis commands
- Alert-focused filtering added for daily reports and diagnoses (`--alerts-only`, `--min-severity`)
- Notification-friendly text/JSON output added with named delivery-target config metadata (`--notify-format`, `--notify-target`)
- Explicit delivery adapters added for webhook/slack POSTs and local stdout/file targets (`--deliver`)
- Automated `unittest` coverage currently passing for the implemented modules

## Status
- Latest pushed commit before this change: `feat: add diagnosis flow and target validation`
- Repo: `<https://github.com/chauhan081/ai-site-caretaker>`
- Current local focus: notification-friendly delivery output for CLI/scheduler use
