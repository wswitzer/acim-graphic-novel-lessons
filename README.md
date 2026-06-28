# ACIM Graphic Novel Lessons

A source-of-truth repository for a day-by-day ACIM-inspired graphic novel/book project.

This repo intentionally uses plain text files as the “database”:

- `data/*.yaml` stores styles, characters, arc rules, continuity memory, and indexes.
- `content/packets/*.yaml` stores the machine-readable daily creative packet.
- `content/daily/*.md` stores the human-readable book/story entry.
- `book/` is where stitched manuscript drafts and weekly/monthly summaries can live.
- `prompts/` stores reusable prompts for ChatGPT Scheduled Tasks and Codex.

## Core creative rule

The visible sequence begins halfway through the Workbook lessons. Characters are not starting from zero, are not instantly healed, and are not required to suffer every day. A lesson can bring one specific healing shift, a peaceful deepening, a holy instant, joy, rest, extension, or ordinary love.

## Suggested automation flow

1. ChatGPT Scheduled Task generates the daily packet.
2. The packet is saved as a GitHub issue or directly as files under `content/`.
3. Codex stitches/validates the new content, updates `data/character-memory.yaml`, and opens a PR.
4. You review/merge.
5. GitHub Actions validates basic file structure.

## Copyright guardrail

Do not reproduce long copyrighted ACIM text. Use lesson number/title, short original summaries/reflections, and source links only.
