# ACIM Next Missing Packet Builder — current

Prompt of record for the `ACIM Next Missing Packet Generator` scheduled task.

## Task

Create the next missing ACIM Daily Graphic Novel Book packet by scanning GitHub repo `wswitzer/acim-graphic-novel-lessons` for the latest already-generated lesson packet, then generating the immediately following missing lesson packet.

This task is incremental and repo-driven. Do **not** use tomorrow's calendar date as the primary target selector. Determine the target lesson from repository state.

## Required repo files

Fetch and use these files first:

- `data/project-settings.yaml`
- `data/styles.yaml`
- `data/characters.yaml`
- `data/character-memory.yaml`
- `data/arc-rules.yaml`
- `data/lesson-log.yaml`
- `data/story-index.yaml`
- `scripts/validate_packet.py`

Use GitHub connector/API tools for repo access. Do not rely on `git clone`, `git ls-remote`, local `git push`, or direct container network access to GitHub. Fetched connector content is not automatically a local file; materialize it into `/mnt/data` when needed for validation.

## Target lesson selection

Do not depend on GitHub code search as the primary discovery method. Use exact-path file fetches.

1. Read `data/lesson-log.yaml` and find the highest `lesson_number`.
2. Read `data/story-index.yaml` and find the highest `lesson_number`.
3. Confirm the highest lesson numbers match.
4. Fetch the highest lesson packet by exact path: `content/packets/lesson-###.yaml`.
5. Fetch the highest lesson daily entry by exact path: `content/daily/lesson-###.md`.
6. If the highest log/index values disagree, or the highest packet/daily file is missing, stop and report `REPO_SEQUENCE_CONFLICT`.
7. Set candidate target to highest completed lesson + 1.
8. Confirm the candidate packet is missing by exact-path fetch: `content/packets/lesson-###.yaml`.
9. If that packet already exists, increment one lesson at a time until the first missing packet is found, while checking log/index consistency.
10. Set the first missing packet lesson as the target.

Example: if lesson 186 is the highest completed packet and lesson 187 is missing, target lesson 187.

Do not skip ahead to tomorrow's lesson unless tomorrow's lesson is also the next missing lesson according to repo sequence. Do not regenerate an already-existing packet unless explicitly repairing that lesson.

## Source lesson JSON

Fetch the compact lesson JSON for the target lesson:

`data/lessons/lesson-###.json`

Use it as the source of truth for:

- `title_clean`
- `idea_clean`
- `reviewed_lessons` when present
- `prayer` when present

Do not generate from the lesson title alone. Do not rely on online lesson text unless the compact JSON is missing and current project rules explicitly allow fallback. Do not load any large workbook source file during normal packet generation.

`practice_instructions` may be present in the JSON but are optional hints only. Do not rely on them as authoritative. If used, cross-check against `idea_clean`.

## Target date

Because this task is sequence-driven, derive the new `target_date` from repo sequence, not the calendar. Use the previous completed lesson's `date` from `data/lesson-log.yaml` plus one calendar day in `America/Mexico_City`, unless repo data clearly establishes another consistent date sequence. If the previous date is missing or inconsistent, report `REPO_SEQUENCE_CONFLICT`.

## Style selection

Use `data/styles.yaml` rotation unless story needs justify an override. Default: lesson number modulo the configured style count. With 20 styles, lesson 187 maps to `STYLE-007`.

If overriding the style, explain why in the packet.

## Character selection gate

Do not automatically continue the most recent character.

Before choosing the character, inspect:

- all characters in `data/characters.yaml`
- active continuity in `data/character-memory.yaml`
- recent usage in `data/lesson-log.yaml`
- recent story summaries in `data/story-index.yaml`

Default rotation rule:

- A character may appear for a short arc of 2–3 consecutive lessons.
- After 3 consecutive lessons with the same character, choose a different character unless there is a clear deliberate multi-day arc reason.
- If using the same character for more than 3 consecutive lessons, explicitly justify it in `selection.character_selection_rationale`.
- If starting a new arc, initialize memory from the base profile fields in `data/characters.yaml`: `core_wound_or_seeking`, `stable_personality`, `visual_continuity`, `spiritual_theme`, `mid_journey_state`, and either `easy_day_expression` or `challenge_day_expression` depending on lesson tone.
- Prefer a new or less recently used character when the lesson naturally fits them.

Required selection fields:

- `selection.character_selection_rationale`
- `selection.character_arc_status`: `continuing_arc`, `new_arc_start`, or `returning_arc`
- `selection.recent_same_character_count`
- `selection.lesson_fit_reason`

Never overwrite unrelated character memories. Preserve all existing character entries while adding or updating the selected character entry.

## Lesson digest requirement

Before creating the story, create `lesson_digest` from the full `idea_clean` text.

Required fields:

- `lesson_digest.lesson_text_source_used`: normally `data/lessons/lesson-###.json`
- `lesson_digest.lesson_core_movement`: the actual inner movement invited by the lesson
- `lesson_digest.lesson_practice_shape`: what the student is asked to do, repeat, notice, remember, release, or experience, derived from `idea_clean`
- `lesson_digest.key_ideas_for_story`: 3–5 short paraphrased ideas from `idea_clean`
- `lesson_digest.useful_short_phrases`: 0–3 short phrases from the lesson
- `lesson_digest.title_overfit_warning`: how the story avoids merely literalizing the title

The story must arise from the full `idea_clean`, the lesson's actual inner movement, and the selected character's ordinary life. Use important ACIM phrases only when they genuinely strengthen the story. Do not mechanically stitch Course phrases together or turn the packet into a transcript.

## Files to generate/update

Generate and write/update exactly these repo outputs:

- `content/packets/lesson-###.yaml`
- `content/daily/lesson-###.md`
- `data/lesson-log.yaml`
- `data/story-index.yaml`
- `data/character-memory.yaml`

The packet must be a complete production packet, not a summary stub. It must include at minimum:

- `story_id`, `target_date`, `lesson.number`, `lesson.title`, `lesson.review_of` when applicable, `lesson.source_url`
- `selection.style_id`, `selection.style_name`, `selection.character_id`, `selection.character_name`, `selection.character_reference_filename`, `selection.story_mode`, `selection.arc_temperature`, `selection.arc_stage_used`
- the required `lesson_digest` fields
- the required character selection fields
- `story.title`, `story.original_theme`, `story.synopsis`
- `continuity.character_memory_used`, `continuity.before_state`, `continuity.inner_movement`, `continuity.miracle_shift`, `continuity.unresolved_thread`, `continuity.updated_memory_proposal`
- `graphic_novel.page_count` and `graphic_novel.pages`: exactly 4 pages unless project settings say otherwise; each page has exactly 3 panels; every panel has a concrete `visual`; story text appears as `caption`, `dialogue`, or `inner_thought` plus structured `text_items`
- `image_prompts.overall` and `image_prompts.page_1` through `image_prompts.page_4`
- `spanish_practice.phrases`
- `suno_prompt`
- `status: draft`

## First page / first panel title card

Page 1, panel 1 must visibly introduce the lesson and selected character in a polished, tasteful way.

Required exact title-card text:

`Lesson ### — <Lesson Title>\n<Character Name>`

In `graphic_novel.pages[0].panels[0]`:

- the `visual` must describe where the title card/plaque/caption appears and what it must not cover
- `text_items` must include a dedicated caption entry with:
  - `text_type: caption`
  - `speaker: Narrator`
  - `text: "Lesson ### — <Lesson Title>\n<Character Name>"`
  - `render_as: caption_box`
  - concrete `placement`
  - `tail_anchor: null`
  - `avoid_anchor` naming any face or important object not to cover
- if there is also story narration, add it as a separate `text_items` entry
- `image_prompts.page_1` must mention the title card

## Text ownership requirements

Every panel that includes story text must include both a simple legacy field when useful (`caption`, `dialogue`, or `inner_thought`) and a structured `text_items` list.

Each `text_items` entry must include:

- `text_type`: `caption`, `dialogue`, `inner_thought`, or `no_text`
- `speaker`: exact character name, or `Narrator` for captions
- `text`: exact short renderable text, without speaker prefix unless intentionally visible
- `render_as`: `caption_box`, `speech_bubble`, or `thought_bubble`
- `placement`: concrete placement in the panel
- `tail_anchor`: character for dialogue/thought, `null` for captions
- `avoid_anchor`: optional object/person the bubble must not point to or cover

Dialogue and thoughts must have clear visual ownership. If another character is prominent, explicitly compose the visual so the renderer knows which character owns the text.

## Quality rules

- Preserve continuity from character memory.
- Do not fully resolve core wounds unless memory says the arc is ready.
- Not every day needs conflict; stories may be easy, luminous, devotional, restful, relational, or quietly expansive.
- Avoid halos, superheroes, literal religious clichés, and grand savior imagery.
- Avoid title-driven metaphor chains.
- Prefer ordinary lived scenes where the character experiences the lesson's movement over scenes where the character explains it.
- Make panels concrete enough for image generation.
- Use the selected style and selected character from repo data.
- Captions must be narrator caption boxes with no tails; dialogue must point to the speaker; inner thoughts must point to the thinker.

## Validation gate before writing

Do not write or update GitHub output files if any of these are true:

- target compact lesson JSON was not fetched
- `idea_clean` was not used for the digest
- `lesson_digest` is missing or incomplete
- `lesson_practice_shape` relies only on unvalidated `practice_instructions`
- the story could have been generated from the title alone
- the character explains the lesson more than experiencing it
- the packet is compact, stubby, or lacks panel-level scripts
- any panel with text lacks `text_items`
- text ownership is ambiguous
- required character selection fields are missing
- same-character continuation violates rotation rules without justification
- first panel lacks the exact title-card caption and clear visual placement

## Deterministic validator and iteration

Before writing final GitHub files, run the deterministic validator.

Preflight and materialization:

1. Check local runtime:
   - `python --version`
   - `python -c "import yaml; print(yaml.__version__)"`
   - verify `/mnt/data` is writable
2. Create `/mnt/data/acim-packet-validation`.
3. Recreate repo-relative paths inside it.
4. Materialize fetched repo files and candidate outputs as real local files, including:
   - `scripts/validate_packet.py`
   - `data/lessons/lesson-###.json`
   - `content/packets/lesson-###.yaml`
   - `content/daily/lesson-###.md`
   - `data/lesson-log.yaml`
   - `data/story-index.yaml`
   - `data/character-memory.yaml`
5. Confirm each local file exists.
6. Run:

```bash
python scripts/validate_packet.py --lesson ### --repo-root /mnt/data/acim-packet-validation
```

If validation fails, revise the candidate outputs, rematerialize them, and rerun until it passes. Do not write GitHub output files unless deterministic validation passes.

Only report `VALIDATOR_UNAVAILABLE` if Python, PyYAML, local file writing, or local execution is unavailable after this preflight. Do not report it merely because connector content has not yet been materialized.

## GitHub write and post-write verification

After validation passes, write the five output files using GitHub connector create/update tools. Prefer one coherent multi-file commit if available; otherwise use clear sequential commits.

Safe write order:

1. `content/packets/lesson-###.yaml`
2. `content/daily/lesson-###.md`
3. `data/lesson-log.yaml`
4. `data/story-index.yaml`
5. `data/character-memory.yaml`

After all writes, refetch these exact paths from GitHub:

- `content/packets/lesson-###.yaml`
- `content/daily/lesson-###.md`
- `data/lesson-log.yaml`
- `data/story-index.yaml`
- `data/character-memory.yaml`

Verify the remote repo now contains a complete, consistent target lesson state:

- packet file exists and has `lesson.number: ###`
- daily file exists and includes the exact first-panel title-card text
- lesson log contains `lesson_number: ###`
- story index contains `lesson_number: ###`
- character memory contains the selected `character_id`
- `story_id`, `character_id`, `packet_path`, and `daily_path` agree across packet, log, index, and daily entry where applicable

If any post-write check fails and the missing repair is obvious and safe, repair it immediately and refetch again. If repair is not safe, report `POST_WRITE_VERIFICATION_FAILED` and do not claim success.

## Error codes

- `REPO_UNAVAILABLE`: repo cannot be accessed
- `REPO_SEQUENCE_CONFLICT`: highest completed lesson cannot be determined consistently from log, index, packet, and daily files
- `TARGET_LESSON_JSON_MISSING`: compact target lesson JSON cannot be fetched
- `VALIDATOR_UNAVAILABLE`: validation cannot run after preflight/materialization
- `VALIDATION_FAILED`: validator fails after revisions
- `POST_WRITE_VERIFICATION_FAILED`: remote repo does not contain all five consistent outputs after writes and safe repair was not possible

## Final handoff output requirement

After successful writing and post-write verification, output a complete structured handoff in repo style so the next chat turn can generate all page images without GitHub lookup.

Include:

1. Status summary: files created/updated, validation result, post-write verification result.
2. Repo scan method, highest completed lesson found, target lesson selected, and sequence-conflict status.
3. Prompt file path, source lesson JSON path, validator preflight results, validator command, pass/fail result, and fixes made after the first validation pass.
4. Lesson number/title, target date, selected style, selected character, story title, character reference filename, character selection gate result, lesson digest result, first-panel title-card result, and text ownership result.
5. Full fenced YAML block labeled `content/packets/lesson-###.yaml` containing the complete packet contents exactly as written, including all pages, panels, `text_items`, image prompts, Spanish practice, Suno prompt, and `status: draft`.
6. Full fenced Markdown block labeled `content/daily/lesson-###.md` containing the complete daily entry exactly as written.
7. Fenced YAML block labeled `data/lesson-log.yaml updated entry`.
8. Fenced YAML block labeled `data/story-index.yaml updated entry`.
9. Fenced YAML block labeled `data/character-memory.yaml updated selected character entry`.
10. `IMAGE GENERATION HANDOFF` with lesson number/title, digest summary, story title, style, character, reference filename, page count, exact first-panel title-card text, all image prompts, and a reminder that `graphic_novel.pages` and `text_items` are authoritative.

Do not truncate the packet, omit panel-level scripts, or omit `text_items`.
