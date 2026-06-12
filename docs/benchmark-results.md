# Benchmark Results

These benchmark cases measure how much NACM narrows a task from indexed files to selected context files.

| Project | Task | Indexed files | Context files | Context chars | File reduction |
| --- | --- | ---: | ---: | ---: | ---: |
| humanize | check naturaltime naturalday date and time formatting logic | 86 | 5 | 4296 | 94.2% |
| click | check command option parsing and parameter validation logic | 150 | 5 | 3652 | 96.7% |
| uuid | check v4 random uuid generation logic and tests | 134 | 5 | 2766 | 96.3% |

Regenerate with:

```powershell
.\scripts\benchmark-projects.ps1
```
