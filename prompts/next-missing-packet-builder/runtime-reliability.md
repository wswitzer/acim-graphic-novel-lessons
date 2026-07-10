# Packet builder runtime reliability contract

This file supplements `prompts/next-missing-packet-builder/current.md` for local materialization and deterministic validation.

Where this file is more specific about execution tools, workspace selection, retries, or `VALIDATOR_UNAVAILABLE`, this file wins.

## Purpose

Keep transient execution-environment failures from being mistaken for packet or validator defects, while preserving the rule that no GitHub output may be written before deterministic validation passes.

## Primary execution method

- Use GitHub connector/API tools for every repository read and write.
- Use `container.exec` as the primary private local-execution method when it is available.
- Do not use user-visible Python for internal validation.
- A connector error, `ClientError`, tool-state reset, empty response, or one failed shell call is transient unless a fresh retry reproduces it.

## Early preflight

Run this before spending substantial effort drafting the packet:

1. `python --version`
2. `python -c "import yaml; print(yaml.__version__)"`
3. Create and delete a small test file under `/mnt/data`.
4. Confirm a shell command can create directories and execute Python scripts.

Do not claim that `/mnt/data` is read-only unless an actual shell command reports the write failure and a fresh `container.exec` retry reproduces it. Include the literal shell error when reporting failure.

## Fresh validation workspace

Create a new unique workspace for every run. Preferred form:

`/mnt/data/acim-packet-validation-<lesson>-<timestamp>`

Never rely on a workspace from a prior run.

If `/mnt/data` genuinely fails the write test twice in fresh shell calls, use:

`/tmp/acim-packet-validation-<lesson>-<timestamp>`

Pass the exact selected workspace path to both validators.

Recreate all required repo-relative directories and materialize fetched connector content as real local files.

## Required local files

At minimum, materialize:

- `scripts/validate_packet.py`
- `scripts/validate_lesson_log.py`
- `data/lessons/lesson-###.json`
- `content/packets/lesson-###.yaml`
- `content/daily/lesson-###.md`
- `data/lesson-log.yaml`
- `data/story-index.yaml`
- `data/character-memory.yaml`

Confirm every required file exists before validation.

## Validator commands

Replace `###` and `<workspace>` with actual values:

```bash
python <workspace>/scripts/validate_packet.py --lesson ### --repo-root <workspace>
python <workspace>/scripts/validate_lesson_log.py --lesson ### --repo-root <workspace> --expect-page-images not_started
```

Both commands must pass before any GitHub output file is written.

## Retry and repair rules

- If a validator runs and reports content errors, revise only the candidate outputs, rematerialize them, and rerun both validators.
- If execution itself fails transiently, retry once in a fresh `container.exec` call.
- Preserve already-materialized candidate files when the workspace still exists.
- Recreate the workspace only when it was lost, corrupted, or located on a genuinely unwritable path.
- Do not disable or alter the recurring scheduled task because one run encounters infrastructure failure.

## `VALIDATOR_UNAVAILABLE` threshold

Report `VALIDATOR_UNAVAILABLE` only after:

1. two fresh `container.exec` attempts fail; and
2. `/mnt/data` has been tested twice; and
3. `/tmp` has also been tested when `/mnt/data` genuinely failed; and
4. no other private local-execution method available to the run can execute the validators.

Never write partially validated files.

## Final reporting

Include:

- Python and PyYAML versions;
- literal workspace write-test result;
- exact workspace used;
- both validator commands;
- first-pass results;
- repairs made;
- final validator results.
