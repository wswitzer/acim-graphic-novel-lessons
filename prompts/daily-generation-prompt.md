# Daily Generation Prompt

Use this prompt for the ChatGPT Scheduled Task that generates one daily ACIM-inspired graphic novel/book packet.

```text
Every day at 1:00 AM America/Mexico_City, create the next ACIM Daily Graphic Novel Book packet.

Use the current date and confirm the ACIM lesson of the day from the configured lesson source. Do not reproduce copyrighted ACIM body text. Use only the lesson number, lesson title, links, and original summaries/reflections.

Read the project memory from the GitHub repository:
- data/styles.yaml
- data/characters.yaml
- data/character-memory.yaml
- data/arc-rules.yaml
- data/lesson-log.yaml
- data/story-index.yaml

Select the graphic novel style according to the project’s rotation rules. Select the character according to character rotation/continuity rules. Use the character’s current memory block, implied first-half journey, already-healed areas, unresolved threads, story mode, and arc pacing guardrails.

Generate:
1. Daily lesson metadata
2. Story mode and arc temperature
3. Short original lesson theme
4. 4-page multi-panel graphic novel plan
5. Page-by-page image prompts
6. Character arc event
7. Updated character memory proposal
8. Spanish A1/A2 practice card
9. Optional Suno prompt
10. Book-entry Markdown

Continuity rules:
- Do not fully resolve the character’s core wound unless character memory explicitly says the arc is ready.
- One lesson may bring one specific miracle-minded shift, deepening, peaceful receiving, or extension of love.
- Not every day must involve a wound or conflict. Some days should be easy, luminous, devotional, playful, restful, relational, or quietly expansive.
- The project begins halfway through the lessons. Treat the first half as implied backstory that may be written later. Do not invent overly specific prequel events unless needed and marked as flexible.

Preferred save behavior:
- Create or update `content/packets/lesson-###.yaml` with the structured packet.
- Create or update `content/daily/lesson-###.md` with the readable story/book entry.
- Append/update `data/lesson-log.yaml`.
- Append/update `data/story-index.yaml`.
- Update the relevant entry in `data/character-memory.yaml` with a concise continuity summary.

If direct file writes are unavailable, create a GitHub issue titled:
Daily Packet - Lesson [number] - [YYYY-MM-DD]

Include the full packet in Markdown with a YAML block. Label it:
- daily-packet
- needs-codex-stitching
```
