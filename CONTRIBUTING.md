# Contributing

Create a focused branch, add tests with each behavioral change, and run `make check` and `make test`
before opening a change. Security findings must follow `SECURITY.md` rather than a public issue.

Developer setup:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
npm install
make check test
```

PowerShell activation is `.\.venv\Scripts\Activate.ps1`. Commits must not contain credentials,
generated secrets, production data, or changes to third-party vendored code without attribution.
