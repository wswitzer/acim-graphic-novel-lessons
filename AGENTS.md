# AGENTS.md

Guidance for Codex/ChatGPT agents working in this repo.

## Project purpose

This repository is the source of truth for an ACIM-inspired daily graphic novel/book workflow. It stores structured YAML memory and human-readable Markdown entries so the project can be generated, reviewed, stitched, and eventually built into a book or website.

## Source-of-truth rules

- Treat GitHub files as the canonical database.
- `data/*.yaml` contains persistent project state, style definitions, character definitions, continuity memory, arc rules, lesson logs, and story indexes.
- `content/packets/*.yaml` contains generated daily packets.
- `content/daily/*.md` contains readable daily story/book entries.
- `book/` contains stitched manuscript drafts.
- `prompts/` contains reusable prompts for scheduled ChatGPT tasks and Codex tasks.

## Copyright guardrail

Do not reproduce long copyrighted ACIM body text. Use lesson number, lesson title, short original summaries/reflections, and source links. Any lesson commentary must be original.

## Continuity guardrails

- The visible story sequence begins partway through the Workbook lessons.
- Characters are not beginners, not fully healed, and not required to suffer every day.
- Do not fully resolve a character’s core wound unless `data/character-memory.yaml` explicitly says the arc is ready.
- One lesson should usually bring one specific perception shift, peaceful deepening, extension of love, or integration step.
- Some days should be easy, luminous, joyful, devotional, playful, restful, or quietly expansive.
- Preserve unresolved threads in `data/character-memory.yaml`.
- When a new daily packet is created, also update `data/lesson-log.yaml`, `data/story-index.yaml`, and the relevant character memory proposal.

## File naming

Use zero-padded lesson numbers:

- `content/packets/lesson-170.yaml`
- `content/daily/lesson-170.md`

## Daily packet minimum fields

Each packet should include:

- lesson metadata
- style id/name
- character id/name
- story mode
- arc temperature
- original theme summary
- graphic novel pages/panels
- page image prompts
- character arc event
- updated character memory proposal
- Spanish A1/A2 practice card
- optional Suno prompt
- book-entry markdown draft

## Validation

Run `npm run validate` before opening PRs when scripts are available.
