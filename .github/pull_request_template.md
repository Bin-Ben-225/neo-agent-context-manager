## Summary

- 

## Scope

- [ ] Local-only
- [ ] Prompt-only
- [ ] Does not read credentials or upload user code
- [ ] Does not commit `.agent/`

## Validation

```powershell
py -3.11 -m pytest tests -q
py -3.11 -m ruff check .
py -3.11 -m nacm validate smoke
```

## Notes

Mention any skipped checks or follow-up work.
