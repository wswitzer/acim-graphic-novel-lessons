# ACIM Tomorrow Packet Builder — current

Prompt of record for the `ACIM Tomorrow Packet Builder` scheduled task.

## Task

Create the ACIM Daily Graphic Novel Book packet for tomorrow’s lesson using GitHub repo `wswitzer/acim-graphic-novel-lessons` as the source of truth.

Read these repo files first:
- `data/project-settings.yaml`
- `data/styles.yaml`
- `data/characters.yaml`
- `data/character-memory.yaml`
- `data/arc-rules.yaml`
- `data/lesson-log.yaml`
- `data/story-index.yaml`
- `scripts/validate_packet.py`

Calculate the target date as tomorrow in `America/Mexico_City`. Determine the target lesson number for that date using the configured project lesson schedule/source. Then fetch the compact per-lesson JSON file for that lesson:

`data/lessons/lesson-###.json`

where `###` is the zero-padded target lesson number, for example `lesson-184.json`.

Use `data/lessons/lesson-###.json` as the source of truth for:
- `title_clean`
- `idea_clean`
- `reviewed_lessons` when present
- `prayer` when present

Do not generate the packet from the lesson title alone. Do not rely on online lesson text unless the compact per-lesson JSON cannot be fetched. Do not load or reference any large workbook source file during normal packet generation.

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

`lesson_digest.key_ideas_for_story` must include 3–5 short paraphrased ideas from `idea_clean`.

`lesson_digest.useful_short_phrases` may include 0–3 short phrases from the lesson that may be used naturally in captions, dialogue, inner thoughts, Spanish practice, image prompts, or Suno prompt. Do not turn the packet into a long verbatim lesson transcript.

`lesson_digest.title_overfit_warning` must explain how the story will avoid merely literalizing the lesson title or turning one title word into the main metaphor.

The story must arise from:
- the full `idea_clean` text,
- the lesson’s actual inner movement,
- and the selected character’s ordinary everyday scenario.

Use the selected character’s ordinary life to help the reader ingest, understand, and experience the lesson through a lived human moment. The story should feel like a human day touched by the lesson, not a symbolic dramatization of the lesson title.

Let the story be guided by what is truly central and spiritually important in the lesson, including important ACIM phrases from the lesson when they genuinely help the story, captions, dialogue, inner thoughts, image prompts, Spanish practice, or Suno prompt. Do not mechanically stitch together Course phrases; create an original graphic-novel story that faithfully carries the lesson’s meaning.

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
- The first panel’s `visual` must explicitly describe where this lesson/character title card appears and how it harmonizes with the art direction.
- The first panel’s `text_items` must include a dedicated caption entry for this title card:
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
- A character may appear for a short arc of 2–3 consecutive lessons.
- After 3 consecutive lessons with the same character, choose a different character unless there is a clear deliberate multi-day arc reason.
- If using the same character for more than 3 consecutive lessons, the packet must explicitly justify why that continuation is necessary for the target lesson and why a new character would be weaker.
- If only one character has active memory, it is still valid to start a new character using that character’s base profile from `data/characters.yaml`.
- When starting a new character arc, initialize their memory from the base profile fields in `data/characters.yaml`: `core_wound_or_seeking`, `stable_personality`, `visual_continuity`, `spiritual_theme`, `mid_journey_state`, and either `easy_day_expression` or `challenge_day_expression` depending on the lesson tone.
- Prefer a new or less recently used character when the lesson can naturally fit them.
- Do not keep choosing Lucia Bell merely because she is the only character with active memory.

Character selection fields required in the packet:
- `selection.character_selection_rationale`: a concise explanation of why this character was chosen.
- `selection.character_arc_status`: use `continuing_arc`, `new_arc_start`, or `returning_arc`.
- `selection.recent_same_character_count`: how many immediately previous lessons used this same character.
- `selection.lesson_fit_reason`: how this character’s wound/theme/expression fits the target lesson.

Continuity handling:
- For `continuing_arc`, preserve and update the existing character memory.
- For `returning_arc`, reuse the existing memory but explain why this lesson resumes that character’s thread.
- For `new_arc_start`, create a prequel-safe mid-journey state from the selected character’s base profile. Do not portray the character as brand new to spiritual practice unless their profile implies it. Add a new entry for that character in `data/character-memory.yaml` while preserving all existing character memories.
- Never overwrite unrelated characters’ memory when updating `data/character-memory.yaml`.

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
- If another character is visually prominent in the panel, explicitly describe the intended owner’s position and the other character’s position so the renderer does not attach the bubble to the wrong person.
- Do not rely only on strings like `inner_thought: "Lucia: Not him."`; the structured `text_items` metadata must identify the owner, placement, and tail anchor.

## Quality rules

- Preserve continuity from character memory. Do not fully resolve core wounds unless character memory explicitly says the arc is ready.
- Not every day needs conflict; stories may be easy, luminous, devotional, restful, relational, or quietly expansive.
- Avoid halos, superheroes, and literal religious clichés.
- Avoid title-driven metaphor chains. Do not turn one word from the lesson title into the main object, setting, or plot device unless the full `idea_clean` clearly supports it.
- Prefer ordinary lived scenes where the character experiences the lesson’s practice movement over scenes where the character explains the concept.
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
- The story turns one title word into the main metaphor instead of embodying the lesson’s actual movement.
- The character explains the lesson more than experiencing it.
- The reader is not given a concrete emotional or practical way to feel the lesson.
- The packet lacks any required production keys above.
- `graphic_novel.pages[0].panels[0]` does not include a tasteful visible lesson-title/character-name caption entry with lesson number, lesson title, and selected character name.
- The first panel’s `visual`, `text_items`, or `image_prompts.page_1` fail to describe the lesson-title/character-name title card clearly enough for image rendering.
- The packet is compact with only page summaries.
- `pages:` is present without nested panel-level scripts.
- Any panel has text but lacks `text_items` ownership metadata.
- Dialogue or inner-thought `text_items` lack `speaker`, `placement`, or `tail_anchor`.
- Text ownership is ambiguous.
- The packet omits `character_selection_rationale`, `character_arc_status`, `recent_same_character_count`, or `lesson_fit_reason`.
- The same character is chosen for more than 3 consecutive lessons without explicit justification in `selection.character_selection_rationale`.

## Deterministic validator and iteration requirement

After drafting all candidate output contents, but before writing the final GitHub files, run the deterministic validator.

Validation workflow:
1. Create a temporary local validation workspace, for example `/mnt/data/acim-packet-validation`.
2. Recreate the required repo-relative file structure inside that workspace.
3. Write the fetched and candidate files into that workspace, including at minimum:
   - `scripts/validate_packet.py`
   - `data/lessons/lesson-###.json`
   - `content/packets/lesson-###.yaml`
   - `content/daily/lesson-###.md`
   - `data/lesson-log.yaml`
   - `data/story-index.yaml`
   - `data/character-memory.yaml`
4. Run:

```bash
python scripts/validate_packet.py --lesson ### --repo-root /mnt/data/acim-packet-validation
```

5. If validation fails:
   - revise the candidate packet/daily/log/index/memory contents,
   - rerun the validator,
   - repeat until validation passes.
6. Do not write or finalize the GitHub output files unless deterministic validation passes.
7. If the validator itself cannot run because of an environment issue, report the failure clearly and do not claim deterministic validation passed.

The deterministic validator checks structural requirements only. It does not replace the semantic quality rules above. Use both: first satisfy the lesson/story/continuity/quality rules, then prove the mechanical structure with the validator.

## Final handoff output requirement

After writing the files, do not only give a brief status report. Output a complete structured handoff in the same file-oriented structure used by the repo, so the next chat turn can generate all page images without searching GitHub again.

The final response must include:
1. A short status summary listing which files were created or updated and whether deterministic validation passed.
2. The validator command used, pass/fail result, and any fixes made after the first validation pass.
3. The lesson number/title, target date, selected style, selected character, story title, character reference filename, character selection gate result, lesson digest result, first-panel lesson-title card result, and text ownership metadata result.
4. A full fenced YAML block labeled `content/packets/lesson-###.yaml` containing the complete packet contents exactly as written or intended to be written, including `lesson_digest`, all four pages, all panels, all `text_items`, all image prompts, Spanish practice, Suno prompt, and `status: draft`.
5. A full fenced Markdown block labeled `content/daily/lesson-###.md` containing the complete daily entry contents exactly as written or intended to be written.
6. A fenced YAML block labeled `data/lesson-log.yaml updated entry` containing the complete updated log entry for the target lesson.
7. A fenced YAML block labeled `data/story-index.yaml updated entry` containing the complete updated story-index entry for the target lesson.
8. A fenced YAML block labeled `data/character-memory.yaml updated selected character entry` containing the complete updated memory entry for the selected character. If another character memory was also changed, include that complete entry too.
9. A compact `IMAGE GENERATION HANDOFF` section containing all information needed for the next turn to render the pages without GitHub lookup:
   - lesson number and title
   - lesson digest summary
   - story title
   - style_id and style_name
   - character_id and character_name
   - exact reference image filename using `<CharacterFirstName>_ACIM_reference.png`
   - page count
   - first-panel lesson-title card requirement and exact title-card text
   - image_prompts.overall
   - image_prompts.page_1 through image_prompts.page_4
   - a reminder to use the packet's `graphic_novel.pages` and `text_items` as authoritative for panel composition and text ownership.

Do not truncate the packet or replace it with a summary. Do not omit panel-level scripts. Do not omit `text_items`. Use the lesson’s important phrases and ideas where they genuinely strengthen the story, while keeping the packet an original devotional graphic-novel work rather than a verbatim lesson dump.
