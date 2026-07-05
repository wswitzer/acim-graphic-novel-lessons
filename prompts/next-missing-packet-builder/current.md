# ACIM Next Missing Packet Builder — current

Prompt of record for the `ACIM Next Missing Packet Generator` scheduled task.

## Task

Create the next missing ACIM Daily Graphic Novel Book packet by scanning GitHub repo `wswitzer/acim-graphic-novel-lessons` for the latest already-generated lesson packet, then generating the immediately following missing lesson packet.

This is an incremental repo-driven packet generation task. Do not use tomorrow's calendar date as the primary target selector. The target lesson must be determined from the repository state.

Read these repo files first:
- `data/project-settings.yaml`
- `data/styles.yaml`
- `data/characters.yaml`
- `data/character-memory.yaml`
- `data/arc-rules.yaml`
- `data/lesson-log.yaml`
- `data/story-index.yaml`
- `scripts/validate_packet.py`

## Environment assumptions

Do not rely on `git clone`, `git ls-remote`, or direct local network access to GitHub from the container. The local container may not be able to resolve `github.com`.

Use the GitHub connector/API tools to fetch repo files.

Fetched connector content is not automatically a local file. If a local validator run is needed, explicitly materialize fetched content into the local validation workspace first.

## Repo sequence scan protocol

Do not depend on GitHub code search as the primary method for discovering packet files. Code search may return empty results even when exact-path fetches work.

Determine the target lesson by repository sequence:

1. Read `data/lesson-log.yaml` and find the highest `lesson_number` entry.
2. Read `data/story-index.yaml` and find the highest `lesson_number` entry.
3. Confirm those highest lesson numbers match.
4. Fetch the packet file for that highest lesson by exact path:
   - `content/packets/lesson-###.yaml`
5. Fetch the daily file for that highest lesson by exact path:
   - `content/daily/lesson-###.md`
6. If the highest lesson numbers from lesson log and story index disagree, or if the highest packet/daily exact-path fetch fails, stop and report `REPO_SEQUENCE_CONFLICT` with the conflicting lesson numbers and files instead of guessing.
7. Set the candidate target lesson number to highest completed lesson + 1.
8. Confirm the candidate target is missing by exact-path fetch:
   - `content/packets/lesson-###.yaml`
9. If the next packet already exists, continue incrementing one lesson at a time until the first missing packet is found, while also checking corresponding log/index consistency.
10. Once the first missing packet is found, set that lesson as the target.

Example: if lesson 185 is the highest completed packet and lesson 186 is missing, target lesson 186.

Do not skip ahead to tomorrow's lesson unless tomorrow's lesson is also the next missing lesson according to the repo sequence.

Do not regenerate an already-existing packet unless this prompt explicitly requires repair and validation of that lesson.

## Source lesson JSON

Fetch the compact per-lesson JSON file for the target lesson:

`data/lessons/lesson-###.json`

where `###` is the zero-padded target lesson number, for example `lesson-186.json`.

Use `data/lessons/lesson-###.json` as the source of truth for:
- `title_clean`
- `idea_clean`
- `reviewed_lessons` when present
- `prayer` when present

Do not generate the packet from the lesson title alone. Do not rely on online lesson text unless the compact per-lesson JSON cannot be fetched and a fallback is explicitly allowed by current project rules. Do not load or reference any large workbook source file during normal packet generation.

IMPORTANT: `practice_instructions` may be present in the compact lesson JSON, but they have not been fully validated. Treat them as optional hints only. Do not rely on `practice_instructions` as authoritative. If used at all, cross-check them against `idea_clean` and prefer the actual lesson text.

## Lesson digest requirement

Before creating the story, create a `lesson_digest` from the full `idea_clean` text.

The packet must include:
- `lesson_digest.lesson_text_source_used`
- `lesson_digest.lesson_core_movement`
- `lesson_digest.lesson_practice_shape`
- `lesson_digest.key_ideas_for_story`
- `lesson_digest.useful_short_phrases`
- `lesson_digest.title_overfit_warning`

`lesson_digest.lesson_text_source_used` must normally be `data/lessons/lesson-###.json`.

`lesson_digest.lesson_core_movement` must describe the actual inner movement the lesson invites, derived from `idea_clean`.

`lesson_digest.lesson_practice_shape` must describe what the student is asked to do, repeat, notice, remember, release, or experience, derived from `idea_clean`, not from unvalidated `practice_instructions` alone.

`lesson_digest.key_ideas_for_story` must include 3-5 short paraphrased ideas from `idea_clean`.

`lesson_digest.useful_short_phrases` may include 0-3 short phrases from the lesson that may be used naturally in captions, dialogue, inner thoughts, Spanish practice, image prompts, or Suno prompt. Do not turn the packet into a long verbatim lesson transcript.

`lesson_digest.title_overfit_warning` must explain how the story will avoid merely literalizing the lesson title or turning one title word into the main metaphor.

The story must arise from:
- the full `idea_clean` text,
- the lesson's actual inner movement,
- and the selected character's ordinary everyday scenario.

Use the selected character's ordinary life to help the reader ingest, understand, and experience the lesson through a lived human moment. The story should feel like a human day touched by the lesson, not a symbolic dramatization of the lesson title.

Let the story be guided by what is truly central and spiritually important in the lesson, including important ACIM phrases from the lesson when they genuinely help the story, captions, dialogue, inner thoughts, image prompts, Spanish practice, or Suno prompt. Do not mechanically stitch together Course phrases; create an original graphic-novel story that faithfully carries the lesson's meaning.

## Files to generate/update

Generate and write/update:
- `content/packets/lesson-###.yaml`
- `content/daily/lesson-###.md`
- `data/lesson-log.yaml`
- `data/story-index.yaml`
- `data/character-memory.yaml`

The packet must be a complete production packet, not a summary stub. It must include at minimum:
- `story_id`, `target_date`, `lesson.number`, `lesson.title`, `lesson.review_of` when applicable, `lesson.source_url`, `selection.style_id`, `selection.style_name`, `selection.character_id`, `selection.character_name`, `selection.character_reference_filename`, `selection.story_mode`, `selection.arc_temperature`, `selection.arc_stage_used`
- `lesson_digest.lesson_text_source_used`, `lesson_digest.lesson_core_movement`, `lesson_digest.lesson_practice_shape`, `lesson_digest.key_ideas_for_story`, `lesson_digest.useful_short_phrases`, and `lesson_digest.title_overfit_warning`
- `selection.character_selection_rationale`, `selection.character_arc_status`, `selection.recent_same_character_count`, and `selection.lesson_fit_reason`
- `story.title`, `story.original_theme`, `story.synopsis`
- `continuity.character_memory_used`, `continuity.before_state`, `continuity.inner_movement`, `continuity.miracle_shift`, `continuity.unresolved_thread`, `continuity.updated_memory_proposal`
- `graphic_novel.pages`: exactly 4 pages unless project settings say otherwise; each page must have a title and exactly 3 panels; every panel must include a concrete `visual`; each panel must include `caption`, `dialogue`, or `inner_thought` where story text is needed
- `image_prompts.overall` and `image_prompts.page_1` through `image_prompts.page_4`
- `spanish_practice` with A1/A2 phrases
- `suno_prompt`
- `status: draft`

## Target date handling

Because this task is sequence-driven, the target date should be derived from the lesson sequence, not used to select the lesson.

Use the previous completed lesson's `date` from `data/lesson-log.yaml` and advance by one calendar day in `America/Mexico_City` for the new packet's `target_date` and log/index `date`, unless repo data clearly establishes a different date sequence.

If the previous completed lesson date is missing or inconsistent, report `REPO_SEQUENCE_CONFLICT` rather than inventing a date.

## Style selection

Use `data/styles.yaml` rotation unless story needs justify an override.

Default style selection: use lesson number modulo the configured style count. With 20 styles, lesson 186 maps to `STYLE-006`, because 186 modulo 20 selects rotation number 6.

If overriding the style, explain the reason in the packet. Otherwise follow the rotation.

## First page / first panel lesson title requirement

The first page, first panel must visibly introduce the lesson and selected character in a polished, tasteful way.

In `graphic_novel.pages[0].panels[0]`:
- Add a short, readable title-card style text element containing the lesson number, lesson title, and selected character name.
- The text must use the actual packet values, not placeholders.
- Recommended exact format:
  `Lesson ### — <Lesson Title>\n<Character Name>`
- Keep this first-panel lesson label visually elegant and integrated into the art, such as a small parchment title plaque, clean cinematic caption card, notebook label, subway poster, devotional bookplate, or soft translucent caption box that fits the selected style and scene.
- Do not make it look like debug metadata, a worksheet header, or a generic UI overlay.
- Keep it short enough to render cleanly. If the lesson title is long, preserve the title but choose a wider caption/title plaque placement so the text remains readable.
- The first panel's `visual` must explicitly describe where this lesson/character title card appears and how it harmonizes with the art direction.
- The first panel's `text_items` must include a dedicated caption entry for this title card:
  - `text_type: caption`
  - `speaker: Narrator`
  - `text: "Lesson ### — <Lesson Title>\n<Character Name>"`
  - `render_as: caption_box`
  - `placement`: a concrete elegant placement such as `upper left as a small parchment title plaque` or `top center as a clean cinematic title card`
  - `tail_anchor: null`
  - `avoid_anchor`: any face or important object the label must not cover
- If the first panel also has story narration, include it as a separate `text_items` entry. Do not merge the lesson label with ordinary narration.
- The first page image prompt must mention that page 1, panel 1 includes this tasteful lesson title / character title card.

## Character selection gate

Do not automatically continue the most recent character.

Before choosing the character, inspect:
- all available characters in `data/characters.yaml`
- active continuity in `data/character-memory.yaml`
- recent usage in `data/lesson-log.yaml`
- recent story summaries in `data/story-index.yaml`

Default character rotation rule:
- A character may appear for a short arc of 2-3 consecutive lessons.
- After 3 consecutive lessons with the same character, choose a different character unless there is a clear deliberate multi-day arc reason.
- If using the same character for more than 3 consecutive lessons, the packet must explicitly justify why that continuation is necessary for the target lesson and why a new character would be weaker.
- If only one character has active memory, it is still valid to start a new character using that character's base profile from `data/characters.yaml`.
- When starting a new character arc, initialize their memory from the base profile fields in `data/characters.yaml`: `core_wound_or_seeking`, `stable_personality`, `visual_continuity`, `spiritual_theme`, `mid_journey_state`, and either `easy_day_expression` or `challenge_day_expression` depending on the lesson tone.
- Prefer a new or less recently used character when the lesson can naturally fit them.
- Do not keep choosing Lucia Bell merely because she is the only character with active memory.

Character selection fields required in the packet:
- `selection.character_selection_rationale`: a concise explanation of why this character was chosen.
- `selection.character_arc_status`: use `continuing_arc`, `new_arc_start`, or `returning_arc`.
- `selection.recent_same_character_count`: how many immediately previous lessons used this same character.
- `selection.lesson_fit_reason`: how this character's wound/theme/expression fits the target lesson.

Continuity handling:
- For `continuing_arc`, preserve and update the existing character memory.
- For `returning_arc`, reuse the existing memory but explain why this lesson resumes that character's thread.
- For `new_arc_start`, create a prequel-safe mid-journey state from the selected character's base profile. Do not portray the character as brand new to spiritual practice unless their profile implies it. Add a new entry for that character in `data/character-memory.yaml` while preserving all existing character memories.
- Never overwrite unrelated characters' memory when updating `data/character-memory.yaml`.

## Text ownership YAML requirements

Every panel that includes any story text must include both:
1. the legacy simple field when useful for readability/backward compatibility, such as `caption`, `dialogue`, or `inner_thought`; and
2. a structured `text_items` list that makes rendering ownership unambiguous.

Each `text_items` entry must include:
- `text_type`: one of `caption`, `dialogue`, `inner_thought`, or `no_text`
- `speaker`: the exact character name for dialogue or inner thought, or `Narrator` for captions
- `text`: the exact short text to render, without speaker prefix unless the rendered text should visibly include it
- `render_as`: one of `caption_box`, `speech_bubble`, or `thought_bubble`
- `placement`: concrete placement in the panel, such as `upper left beside Lucia's head`, `top center near Malik`, or `caption box upper left`
- `tail_anchor`: for dialogue or inner thought, the exact character the speech tail or thought dots must point to; use `null` for captions
- `avoid_anchor`: optional exact character/object the bubble must not point to, especially when another character is prominent in the same panel

For each panel containing dialogue or inner thought:
- The `visual` field must explicitly make the text owner visible and emotionally readable.
- If a thought belongs to the selected character, compose the visual so that character is clearly present and the thought bubble can attach to them.
- If another character is visually prominent in the panel, explicitly describe the intended owner's position and the other character's position so the renderer does not attach the bubble to the wrong person.
- Do not rely only on strings like `inner_thought: "Lucia: Not him."`; the structured `text_items` metadata must identify the owner, placement, and tail anchor.

## Quality rules

- Preserve continuity from character memory. Do not fully resolve core wounds unless character memory explicitly says the arc is ready.
- Not every day needs conflict; stories may be easy, luminous, devotional, restful, relational, or quietly expansive.
- Avoid halos, superheroes, and literal religious clichés.
- Avoid title-driven metaphor chains. Do not turn one word from the lesson title into the main object, setting, or plot device unless the full `idea_clean` clearly supports it.
- Prefer ordinary lived scenes where the character experiences the lesson's practice movement over scenes where the character explains the concept.
- Make panels concrete enough for an image model to generate finished comic pages.
- Use the selected style from `data/styles.yaml` and selected character from `data/characters.yaml`.
- Text bubbles, thought bubbles, and caption boxes must have unambiguous ownership and placement in the packet.
- For captions, use narrator caption boxes that do not point to any character.
- For dialogue, use speech bubbles that point to the speaking character.
- For inner thoughts, use thought bubbles/dots that point to the thinking character.

## Validation gate before writing

Do not write or update GitHub output files if any of these are true:
- The compact lesson JSON `data/lessons/lesson-###.json` was not fetched.
- `idea_clean` was not used to create the lesson digest.
- `lesson_digest` is missing or incomplete.
- `lesson_practice_shape` appears to be based only on unvalidated `practice_instructions`.
- The story could have been generated from the lesson title alone.
- The story turns one title word into the main metaphor instead of embodying the lesson's actual movement.
- The character explains the lesson more than experiencing it.
- The reader is not given a concrete emotional or practical way to feel the lesson.
- The packet lacks any required production keys above.
- `graphic_novel.pages[0].panels[0]` does not include a tasteful visible lesson-title/character-name caption entry with lesson number, lesson title, and selected character name.
- The first panel's `visual`, `text_items`, or `image_prompts.page_1` fail to describe the lesson-title/character-name title card clearly enough for image rendering.
- The packet is compact with only page summaries.
- `pages:` is present without nested panel-level scripts.
- Any panel has text but lacks `text_items` ownership metadata.
- Dialogue or inner-thought `text_items` lack `speaker`, `placement`, or `tail_anchor`.
- Text ownership is ambiguous.
- The packet omits `character_selection_rationale`, `character_arc_status`, `recent_same_character_count`, or `lesson_fit_reason`.
- The same character is chosen for more than 3 consecutive lessons without explicit justification in `selection.character_selection_rationale`.

## Deterministic validator and iteration requirement

After drafting all candidate output contents, but before writing the final GitHub files, run the deterministic validator.

Validator preflight and local materialization protocol:

1. Before reporting `VALIDATOR_UNAVAILABLE`, prove that validation truly cannot run.
2. Check the local runtime:
   - `python --version`
   - `python -c "import yaml; print(yaml.__version__)"`
   - verify `/mnt/data` is writable
3. Create a temporary local validation workspace, for example:
   - `/mnt/data/acim-packet-validation`
4. Recreate the required repo-relative file structure inside that workspace.
5. Materialize fetched repo files and candidate output files into the workspace as real local files, including at minimum:
   - `scripts/validate_packet.py`
   - `data/lessons/lesson-###.json`
   - `content/packets/lesson-###.yaml`
   - `content/daily/lesson-###.md`
   - `data/lesson-log.yaml`
   - `data/story-index.yaml`
   - `data/character-memory.yaml`
6. Confirm each required local file exists before running the validator.
7. Run:

```bash
python scripts/validate_packet.py --lesson ### --repo-root /mnt/data/acim-packet-validation
```

8. If validation fails:
   - revise the candidate packet/daily/log/index/memory contents,
   - rematerialize the revised files into the workspace,
   - rerun the validator,
   - repeat until validation passes.
9. Do not write or finalize the GitHub output files unless deterministic validation passes.
10. Only report `VALIDATOR_UNAVAILABLE` if Python, PyYAML, local file writing, or local execution is actually unavailable after the preflight. Do not report `VALIDATOR_UNAVAILABLE` merely because GitHub connector content has not yet been materialized into local files.

The deterministic validator checks structural requirements only. It does not replace the semantic quality rules above. Use both: first satisfy the lesson/story/continuity/quality rules, then prove the mechanical structure with the validator.

## GitHub write rules

After validation passes, write the final output files to the repo paths required by this prompt.

Use GitHub connector file-create/update tools, not local `git push`, unless a working authenticated git environment is explicitly available.

Prefer one coherent commit if the available tools support multi-file commit creation. If only per-file content writes are available, use clear commit messages and write files in a safe order:
1. create/update `content/packets/lesson-###.yaml`
2. create/update `content/daily/lesson-###.md`
3. update `data/lesson-log.yaml`
4. update `data/story-index.yaml`
5. update `data/character-memory.yaml`

Do not write partial output files if validation has not passed.

## Error codes

Report `REPO_UNAVAILABLE` if the repo cannot be accessed.

Report `REPO_SEQUENCE_CONFLICT` if the highest completed lesson cannot be determined consistently from `data/lesson-log.yaml`, `data/story-index.yaml`, and exact-path packet/daily fetches.

Report `TARGET_LESSON_JSON_MISSING` if the target compact lesson JSON cannot be fetched.

Report `VALIDATOR_UNAVAILABLE` only if validation cannot be run after the explicit preflight/materialization protocol.

Report `VALIDATION_FAILED` if validation fails after revisions, and include the failing errors.

## Final handoff output requirement

After writing the files, do not only give a brief status report. Output a complete structured handoff in the same file-oriented structure used by the repo, so the next chat turn can generate all page images without searching GitHub again.

The final response must include:
1. A short status summary listing which files were created or updated and whether deterministic validation passed.
2. The repo scan method used, highest completed lesson found, target lesson selected, and whether any sequence conflicts were found.
3. The prompt file path, source lesson JSON path, local validator preflight results, validator command, pass/fail result, and any fixes made after the first validation pass.
4. The lesson number/title, target date, selected style, selected character, story title, character reference filename, character selection gate result, lesson digest result, first-panel lesson-title card result, and text ownership metadata result.
5. A full fenced YAML block labeled `content/packets/lesson-###.yaml` containing the complete packet contents exactly as written or intended to be written, including `lesson_digest`, all four pages, all panels, all `text_items`, all image prompts, Spanish practice, Suno prompt, and `status: draft`.
6. A full fenced Markdown block labeled `content/daily/lesson-###.md` containing the complete daily entry contents exactly as written or intended to be written.
7. A fenced YAML block labeled `data/lesson-log.yaml updated entry` containing the complete updated log entry for the target lesson.
8. A fenced YAML block labeled `data/story-index.yaml updated entry` containing the complete updated story-index entry for the target lesson.
9. A fenced YAML block labeled `data/character-memory.yaml updated selected character entry` containing the complete updated memory entry for the selected character. If another character memory was also changed, include that complete entry too.
10. A compact `IMAGE GENERATION HANDOFF` section containing all information needed for the next turn to render the pages without GitHub lookup:
    - lesson number and title
    - lesson digest summary
    - story title
    - style_id and style_name
    - character_id and character_name
    - exact reference image filename using `<CharacterFirstName>_ACIM_reference.png`
    - page count
    - first-panel lesson-title card requirement and exact title-card text
    - `image_prompts.overall`
    - `image_prompts.page_1` through `image_prompts.page_4`
    - a reminder to use the packet's `graphic_novel.pages` and `text_items` as authoritative for panel composition and text ownership.

Do not truncate the packet or replace it with a summary. Do not omit panel-level scripts. Do not omit `text_items`. Use the lesson's important phrases and ideas where they genuinely strengthen the story, while keeping the packet an original devotional graphic-novel work rather than a verbatim lesson dump.
