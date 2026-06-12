# Benchmark Results

These benchmark cases measure how much NACM narrows a task from indexed files to selected context files.

| Project | Task | Repo commit | NACM version | Max files | Indexed files | Context files | Context chars | File reduction | Index seconds | Quick seconds | Stats seconds |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| humanize | check naturaltime naturalday date and time formatting logic | 976484a | 0.1.0a4 | 5 | 86 | 5 | 4296 | 94.2% | 0.243 | 0.276 | 0.199 |
| click | check command option parsing and parameter validation logic | 8a1b1a3 | 0.1.0a4 | 5 | 150 | 5 | 3652 | 96.7% | 0.302 | 0.242 | 0.173 |
| uuid | check v4 random uuid generation logic and tests | 664cb31 | 0.1.0a4 | 5 | 134 | 5 | 2766 | 96.3% | 0.223 | 0.225 | 0.167 |

Regenerate with:

```powershell
.\scripts\benchmark-projects.ps1
.\scripts\benchmark-projects.ps1 -Project humanize -MaxFiles 5
```
