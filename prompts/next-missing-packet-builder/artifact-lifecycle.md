# Packet and page-image artifact lifecycle contract

This file supplements `prompts/next-missing-packet-builder/current.md` for the `ACIM Next Missing Packet Generator` scheduled task. Follow both files. Where this file is more specific about `data/lesson-log.yaml`, this file wins.

## Purpose

`data/lesson-log.yaml` must distinguish packet creation from rendered page-image creation. The packet file's own `status: draft` is an editorial/content status and must not be used as the artifact-generation status.

## Required lesson-log entry

Every newly generated packet must add exactly one lesson entry with the existing lesson metadata plus these artifact fields:

```yaml
- lesson_number: 189
  date: '2026-07-08'
  style_id: STYLE-009
  character_id: CHAR-001
  story_mode: integration
  arc_temperature: 2
  packet_path: content/packets/lesson-189.yaml
  daily_path: content/daily/lesson-189.md
  packet_status: complete
  packet_generated_at_local: '2026-07-09T22:05:00-06:00'
  packet_validation_status: passed
  packet_validation_notes: Deterministic packet validation passed.
  page_images:
    status: not_started
    expected_count: 4
    generated_count: 0
    completed_at_local: null
    pages:
      - page_number: 1
        status: not_started
        path: assets/images/lesson-189/page-1.png
        generated_at_local: null
      - page_number: 2
        status: not_started
        path: assets/images/lesson-189/page-2.png
        generated_at_local: null
      - page_number: 3
        status: not_started
        path: assets/images/lesson-189/page-3.png
        generated_at_local: null
      - page_number: 4
        status: not_started
        path: assets/images/lesson-189/page-4.png
        generated_at_local: null
```

## Packet-generation rules

- Set `packet_status: complete` only after the packet and daily files are complete candidate outputs and both deterministic validators pass.
- Set `packet_validation_status: passed` only when validation actually passes.
- Record a concrete `packet_generated_at_local` timestamp in `America/Mexico_City`.
- Initialize `page_images.status` to `not_started`, `generated_count` to `0`, and all four page statuses to `not_started`.
- Use exactly four deterministic page paths: `assets/images/lesson-###/page-1.png` through `page-4.png`.
- Do not use the legacy ambiguous lesson-log fields `status`, `generated_at_local`, `validation_passed`, or `validation_notes`.

## Page-image lifecycle rules

Allowed overall `page_images.status` values:

- `not_started`: no page files have been generated.
- `in_progress`: rendering is actively underway.
- `partial`: one to three page files exist, but generation is not currently running.
- `complete`: all four page files exist and have been verified.
- `failed`: generation stopped with no completed page files; include `last_error`.

Allowed individual page statuses are `not_started`, `in_progress`, `complete`, and `failed`.

A page may be marked `complete` only after its exact repository file exists. `generated_count` must equal the number of pages whose status is `complete`. `completed_at_local` must be non-null only when all four pages are complete.

## Historical backfill rule

Historical state may be backfilled only from deterministic repository evidence:

- Mark the packet `complete` when both the packet and daily files exist.
- Mark image generation `complete` only when all four exact page files exist in `assets/images/lesson-###/`.
- Mark image generation `partial` when one to three exact page files exist.
- Mark image generation `not_started` when none of the exact page files exist.
- Do not infer that an image exists merely because it was displayed in a prior chat or generated outside the repository.

## Validation commands

Materialize both validators and run both before writing the five packet outputs:

```bash
python scripts/validate_packet.py --lesson ### --repo-root /mnt/data/acim-packet-validation
python scripts/validate_lesson_log.py --lesson ### --repo-root /mnt/data/acim-packet-validation --expect-page-images not_started
```

Do not write GitHub output files unless both commands pass.

## Post-write verification

After writing, refetch `data/lesson-log.yaml` and verify that the target lesson has:

- `packet_status: complete`
- `packet_validation_status: passed`
- the exact packet and daily paths
- a four-page `page_images` structure initialized to `not_started`
- no legacy ambiguous status fields
