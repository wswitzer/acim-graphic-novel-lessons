# ACIM Tomorrow Packet Builder — 2026-07-03 pre-validator snapshot

This is a versioned snapshot of the active `ACIM Tomorrow Packet Builder` scheduled-task prompt before adding deterministic validator/iteration requirements.

## Prompt

```text
Create the ACIM Daily Graphic Novel Book packet for tomorrow’s lesson using GitHub repo `wswitzer/acim-graphic-novel-lessons` as the source of truth.

Read these repo files first:
- `data/project-settings.yaml`
- `data/styles.yaml`
- `data/characters.yaml`
- `data/character-memory.yaml`
- `data/arc-rules.yaml`
- `data/lesson-log.yaml`
- `data/story-index.yaml`

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

Before creating the story, create a `lesson_digest` from the full `idea_clean` text. The packet must include `lesson_digest.lesson_text_source_used`, `lesson_digest.lesson_core_movement`, `lesson_digest.lesson_practice_shape`, `lesson_digest.key_ideas_for_story`, `lesson_digest.useful_short_phrases`, and `lesson_digest.title_overfit_warning`.

The story must arise from the full `idea_clean` text, the lesson’s actual inner movement, and the selected character’s ordinary everyday scenario. Use the selected character’s ordinary life to help the reader ingest, understand, and experience the lesson through a lived human moment.

Generate and write/update:
- `content/packets/lesson-###.yaml`
- `content/daily/lesson-###.md`
- `data/lesson-log.yaml`
- `data/story-index.yaml`
- `data/character-memory.yaml`

The packet must be a complete production packet, not a summary stub. It must include all required lesson, selection, lesson_digest, story, continuity, graphic_novel, image_prompts, spanish_practice, suno_prompt, and `status: draft` fields.

FIRST PAGE / FIRST PANEL LESSON TITLE REQUIREMENT

The first page, first panel must visibly introduce the lesson and selected character in a polished, tasteful way. In `graphic_novel.pages[0].panels[0]`, include a dedicated `text_items` caption entry with exact text:

`Lesson ### — <Lesson Title>\n<Character Name>`

The first panel’s `visual`, `text_items`, and `image_prompts.page_1` must clearly describe the title-card placement and ensure it does not cover faces or important objects.

CHARACTER SELECTION GATE

Do not automatically continue the most recent character. Inspect all characters, active continuity, recent usage, and recent story summaries. A character may appear for a short arc of 2–3 consecutive lessons. After 3 consecutive lessons with the same character, choose a different character unless there is a clear deliberate multi-day arc reason. Include `selection.character_selection_rationale`, `selection.character_arc_status`, `selection.recent_same_character_count`, and `selection.lesson_fit_reason`.

TEXT OWNERSHIP YAML REQUIREMENTS

Every panel that includes story text must include the simple legacy field when useful and a structured `text_items` list. Each `text_items` entry must include `text_type`, `speaker`, `text`, `render_as`, `placement`, `tail_anchor`, and optional `avoid_anchor`. Captions use `Narrator` and `tail_anchor: null`; dialogue and inner thoughts must point clearly to the speaking/thinking character.

Quality rules: preserve continuity, do not fully resolve core wounds too quickly, avoid halos/superheroes/literal religious cliches, avoid title-driven metaphor chains, prefer ordinary lived scenes, and make panels concrete enough for image generation.

Validation gate before writing: do not write if the compact lesson JSON was not fetched, `idea_clean` was not used, lesson_digest is incomplete, practice shape is based only on unvalidated practice instructions, the story could have been generated from title alone, the packet lacks required keys, the first-panel title card is missing, pages/panels are incomplete, text ownership is ambiguous, or character selection fields are omitted.

After writing the files, output a complete structured handoff with status, packet YAML, daily Markdown, updated log entry, updated story-index entry, updated character-memory entry, and compact IMAGE GENERATION HANDOFF.
```
