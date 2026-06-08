# NACM Examples

This page shows the shape of the local files NACM generates during a small Codex-first workflow.

## Example Workflow

```bash
nacm init --profile low-memory
nacm index build
nacm quick "fix src/images.py image loading failure"
```

`quick` stores the task, builds `.agent/sessions/context_pack.md`, renders `.agent/codex/codex_prompt.md`, and tries to copy the prompt to the clipboard.

After Codex finishes:

```bash
nacm done
```

## Context Pack Shape

```md
# NACM Context Pack

## Current Task

fix src/images.py image loading failure

## Relevant Files

### High Confidence
- `src/images.py` (score: 24)
  - Functions: load_image
  - Keywords: def, load_image, path, return
  - Match reasons: explicit path, filename:images, path:image

### Medium Confidence
- None

### Low Confidence
- None

## Suggested Scoped Search

- Start with High Confidence files.
- If needed, search only related directories from the relevant file list.
- Avoid full repository scans by default.
```

If no files match, NACM adds a `No Match Guidance` section that asks Codex to use scoped search before reading additional files.

## Done Report Shape

```md
# NACM Task Report

## Summary

Changed file count: 2
Large Change Risk: no
Index Dirty: yes

## Changed Files

### Modified Files
- `src/images.py`

### Added Or Untracked Files
- `tests/test_images.py`

### Deleted Files
- None

### Renamed Files
- None

## Forbidden Path Check

- No forbidden paths detected.

## Review Recommendation

- Review changed files manually before continuing.

## Next Action

- Run `nacm index build` if project structure or symbols changed.
```

If the changed file count is larger than the active profile allows, `Large Change Risk` becomes `yes` and the report recommends a review pass before continuing.
