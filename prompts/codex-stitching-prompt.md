# Codex Stitching Prompt

Use this prompt for Codex when turning a generated daily packet into durable repo files.

```text
Review the newest daily packet or issue and stitch it into the repository.

Tasks:
1. Create or update `content/packets/lesson-###.yaml` with the machine-readable packet.
2. Create or update `content/daily/lesson-###.md` with the readable book/story entry.
3. Append or update the lesson entry in `data/lesson-log.yaml`.
4. Append or update the story entry in `data/story-index.yaml`.
5. Update the relevant character in `data/character-memory.yaml` with a concise continuity summary.
6. Ensure the character is not instantly healed unless the memory explicitly says that arc is ready.
7. Preserve unresolved threads and note the next natural step.
8. Run `npm run validate`.
9. Open a PR with a short summary and any continuity concerns.

Guardrails:
- Do not reproduce long copyrighted ACIM body text.
- Do not convert every lesson into conflict.
- Some days may be restful, joyful, luminous, or simply deepening love.
- Keep Markdown readable and YAML structured.
- Prefer small, reviewable diffs.
```
