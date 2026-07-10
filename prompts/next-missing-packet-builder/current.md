# ACIM Next Missing Packet Builder — current

Prompt of record for the `ACIM Next Missing Packet Generator` scheduled task.

## Authority and required contracts

Use GitHub repo `wswitzer/acim-graphic-novel-lessons` as the sole source of truth.

Before doing any work, fetch and follow all of these version-controlled files:

1. `prompts/next-missing-packet-builder/current.md` — this orchestration prompt
2. `prompts/next-missing-packet-builder/artifact-lifecycle.md` — packet and page-image lifecycle contract
3. `prompts/next-missing-packet-builder/runtime-reliability.md` — local execution, workspace, retry, and validator reliability contract
4. `scripts/validate_packet.py` — packet structure validator
5. `scripts/validate_lesson_log.py` — lifecycle validator

Where the contracts are more specific than this orchestration prompt, the more specific contract wins.

Historical prompt copies in this folder are reference-only and must not override `current.md` or either active contract.

## Task

Create the next missing ACIM Daily Graphic Novel Book packet by scanning repository state, selecting the immediately following missing lesson, generating the complete packet and daily entry, updating continuity/index/lifecycle files, validating all candidate outputs locally, writing exactly five repository outputs, and verifying the remote state after writing.

## Required repository inputs

Fetch these exact files before selection or generation:

- `data/project-settings.yaml`
- `data/styles.yaml`
- `data/characters.yaml`
- `data/character-memory.yaml`
- `data/arc-rules.yaml`
- `data/lesson-log.yaml`
- `data/story-index.yaml`
- both active contracts and both validators listed above

Use GitHub connector/API tools for every repository read and write. Do not use local Git network commands as a substitute.

## Target selection

1. Find the highest `lesson_number` in `data/lesson-log.yaml`.
2. Find the highest `lesson_number` in `data/story-index.yaml`.
3. Confirm those values match.
4. Fetch the highest packet and daily entry by exact path.
5. If log, index, packet, or daily state conflicts, stop with `REPO_SEQUENCE_CONFLICT`.
6. Starting at highest completed lesson + 1, fetch exact packet paths until the first missing packet is found.
7. Use that first missing lesson as the target. Do not select by tomorrow's calendar date.
8. Derive `target_date` from the prior completed log date plus one calendar day in `America/Mexico_City` unless repository evidence establishes another consistent sequence.

## Source lesson

Fetch `data/lessons/lesson-###.json` for the target.

Use its `title_clean` and full `idea_clean` as authoritative. Use `reviewed_lessons` and `prayer` when present. Do not generate from the title alone and do not load the large workbook during normal generation.

If the compact lesson JSON is missing, stop with `TARGET_LESSON_JSON_MISSING`.

## Style, character, and continuity

Use `data/styles.yaml`, `data/characters.yaml`, `data/character-memory.yaml`, `data/arc-rules.yaml`, recent lesson-log usage, and recent story-index summaries.

- Apply configured style rotation unless a justified override is recorded.
- Do not automatically continue the newest character.
- A normal short arc is 2–3 consecutive lessons.
- After 3 consecutive lessons with one character, rotate unless a deliberate continuation is explicitly justified.
- Preserve all unrelated character memories.
- For a new arc, initialize continuity from the selected base character profile.

The packet must include:

- `selection.character_selection_rationale`
- `selection.character_arc_status`: `continuing_arc`, `new_arc_start`, or `returning_arc`
- `selection.recent_same_character_count`
- `selection.lesson_fit_reason`

## Lesson digest

Before writing the story, derive a digest from the full `idea_clean` containing:

- `lesson_text_source_used`
- `lesson_core_movement`
- `lesson_practice_shape`
- `key_ideas_for_story` with 3–5 items
- `useful_short_phrases` with 0–3 items
- `title_overfit_warning`

The story must arise from the lesson's inner movement and the character's ordinary life, not merely literalize the title or turn Course language into exposition.

## Exactly five outputs

Generate or update exactly:

1. `content/packets/lesson-###.yaml`
2. `content/daily/lesson-###.md`
3. `data/lesson-log.yaml`
4. `data/story-index.yaml`
5. `data/character-memory.yaml`

The packet must be complete production material, including:

- lesson and source metadata
- complete selection metadata
- lesson digest
- story title, original theme, and synopsis
- continuity state and updated-memory proposal
- exactly 4 pages unless project settings say otherwise
- exactly 3 concrete panels per page
- structured `text_items` for all story text
- `image_prompts.overall` and `page_1` through `page_4`
- Spanish practice
- Suno prompt
- packet-level `status: draft`

## Title card and text ownership

Page 1 panel 1 must contain the exact title-card text:

`Lesson ### — <Lesson Title>\n<Character Name>`

The panel visual must explicitly place the title card without covering a face or important object. Its `text_items` entry must use:

- `text_type: caption`
- `speaker: Narrator`
- `render_as: caption_box`
- concrete placement
- `tail_anchor: null`
- a concrete `avoid_anchor`

Every caption, dialogue line, and thought must have unambiguous structured ownership. Captions have no tails; dialogue points to the speaker; thoughts point to the thinker.

## Lifecycle requirements

Follow `artifact-lifecycle.md` exactly. For a newly generated packet, the target lesson-log entry must unambiguously record a completed, validated packet and four unstarted page images. Do not introduce or retain legacy ambiguous lifecycle fields prohibited by the contract.

The packet file's `status: draft` is editorial content status and is separate from lesson-log artifact lifecycle state.

## Local validation

Follow `runtime-reliability.md` exactly for preflight, unique workspace selection, `/tmp` fallback, retries, required local files, and the threshold for `VALIDATOR_UNAVAILABLE`.

Materialize candidate outputs, target lesson JSON, and both validators using repository-relative paths in the selected fresh workspace.

Run both commands using the actual workspace and lesson number:

```bash
python <workspace>/scripts/validate_packet.py --lesson ### --repo-root <workspace>
python <workspace>/scripts/validate_lesson_log.py --lesson ### --repo-root <workspace> --expect-page-images not_started
```

If either validator reports content errors, repair the candidates and rerun both until both pass. Do not write any GitHub output unless both pass.

## GitHub writes and verification

After both validators pass, write the five outputs sequentially in this order:

1. packet
2. daily entry
3. lesson log
4. story index
5. character memory

Then refetch all five exact paths and verify:

- packet and daily files exist and match the target
- exact first-panel title-card text is present
- log and story index each contain exactly one target entry
- selected character memory exists
- IDs and paths agree across outputs
- lifecycle fields and four deterministic page paths satisfy the active contract
- no prohibited legacy lifecycle fields remain in the target entry

Repair only obvious safe post-write inconsistencies. Otherwise report `POST_WRITE_VERIFICATION_FAILED`.

## Final handoff

Report:

- repo scan and selected target
- active prompt and contract paths
- runtime preflight and exact workspace used
- both validator commands, first-pass results, repairs, and final results
- five written paths and post-write verification
- lesson/style/character/story/digest/title-card/text-ownership summary
- complete packet YAML
- complete daily Markdown
- target updated entries from lesson log, story index, and selected character memory
- an `IMAGE GENERATION HANDOFF` containing all image prompts and noting that `graphic_novel.pages` and `text_items` are authoritative

Do not truncate the packet or omit panel scripts or `text_items`.
