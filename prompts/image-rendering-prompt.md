# Image Rendering Prompt

Use this prompt in a clean ChatGPT image-generation thread or scheduled image task after the daily packet has been generated.

```text
Render the actual graphic novel page images for the latest generated lesson in GitHub repo `wswitzer/acim-graphic-novel-lessons`.

Read the latest entry from `data/lesson-log.yaml`. Then read that lesson's packet from `content/packets/lesson-###.yaml` and daily story from `content/daily/lesson-###.md`.

Use the packet's:
- selected style
- character description and visual continuity
- overall image prompt
- page_1, page_2, page_3, and page_4 image prompts
- graphic_novel.pages panel descriptions

Generate four separate images, one per page:
- page 1
- page 2
- page 3
- page 4

Critical rendering requirements:
- Do not generate a dashboard, UI mockup, metadata screen, file tree, or status report image.
- Do not visualize GitHub or the workflow itself.
- Generate only the four graphic novel pages described by the lesson packet.
- Keep the character visually consistent across all pages.
- Use the selected graphic novel style.
- Avoid halos and literal religious cliches.
- Avoid reproducing long copyrighted ACIM text in the image. Short original captions from the packet are allowed.
- Each generated image should be a finished comic/graphic-novel page, not a prompt sheet.

For Lesson 179 specifically, render Lucia Bell in Premium Animated Feature Style using the page prompts from `content/packets/lesson-179.yaml`. She is a mid-20s Caribbean-British musician with colorful headwrap, headphones, gold necklace, and lyric notebook. The story is called “The Song That Stayed.” The visual motif is a faint golden melody connecting ordinary city life.

After generating images, report whether the images can be stored automatically. If binary upload to GitHub is unavailable, return the generated images in ChatGPT and note that GitHub should store prompt metadata and external image links instead.
```

## Single-page fallback prompt

Use this if the image model struggles with four separate pages at once:

```text
Create one finished graphic novel page for Lesson 179, Page 1: “Rooftop Afterglow.”

Premium animated feature graphic novel style, appealing character design, painterly backgrounds, warm night city lighting, clear emotional storytelling, no halos, no literal religious imagery. Show Lucia Bell, a mid-20s Caribbean-British musician with colorful headwrap, headphones around her neck, gold necklace, and lyric notebook.

Page layout: three panels.

Panel 1: Wide evening rooftop in a warm city. String lights glow above Lucia and her bandmates as they pack up instruments. Caption: “The last note faded, but Lucia kept listening.”

Panel 2: Close-up of Lucia’s hand resting on her lyric notebook. Her gold necklace catches soft light. Dialogue: “It always feels like I have to catch it before it leaves.”

Panel 3: Painterly sky over the rooftop. The last trace of the rehearsal appears as subtle music-note-shaped light dissolving into the clouds. Caption: “Tonight, she did not reach for it.”

Make this a finished comic page, not a dashboard, not a UI, not a prompt sheet.
```
