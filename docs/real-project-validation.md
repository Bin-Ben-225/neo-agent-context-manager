# Real Project Validation

This page records public-safe validation targets for NACM. The goal is to check whether generated context packs and match explanations are useful on real repositories without making those repositories test dependencies.

## Projects

| Project | Shape | Validation Focus |
| --- | --- | --- |
| `python-humanize/humanize` | Small Python library | Source/test matching, docs, localization, benchmarks |
| `pallets/click` | Medium Python CLI library | Command and option APIs, examples, tests |
| `uuidjs/uuid` | TypeScript package | Non-Python fallback indexing and prompt workflow |

## Suggested Commands

Run from a fresh clone of each project:

```powershell
py -3.11 -m nacm init --profile low-memory
py -3.11 -m nacm index build
py -3.11 -m nacm status
py -3.11 -m nacm match explain "<task>" --limit 6
py -3.11 -m nacm quick "<task>" --max-files 5 --explain
py -3.11 -m nacm plan "Investigate and improve task workflow"
py -3.11 -m nacm done
```

For Python projects, also check the workstation relation index:

```powershell
py -3.11 -m nacm index build --profile workstation
```

## Acceptance Notes

- `humanize` time task should keep `src/humanize/time.py` and `tests/test_time.py` near the top.
- `click` command option task should surface core Click command/option code and relevant tests before broad examples.
- `uuid` v4 task should surface `src/v4.ts` and v4 tests or examples without requiring Python-specific relation data.
- Benchmark, localization, generated, cache, and typing-marker files should not crowd out core source and test files.
