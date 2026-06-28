import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const requiredFiles = [
  'README.md',
  'AGENTS.md',
  'data/styles.yaml',
  'data/characters.yaml',
  'data/character-memory.yaml',
  'data/arc-rules.yaml',
  'data/lesson-log.yaml',
  'data/story-index.yaml',
  'prompts/daily-generation-prompt.md',
  'prompts/codex-stitching-prompt.md',
  'book/manuscript.md',
  'book/toc.md'
];

const errors = [];

for (const file of requiredFiles) {
  if (!existsSync(file)) {
    errors.push(`Missing required file: ${file}`);
  }
}

function read(file) {
  return readFileSync(file, 'utf8');
}

if (existsSync('data/styles.yaml')) {
  const styles = read('data/styles.yaml');
  const count = (styles.match(/id: STYLE-/g) || []).length;
  if (count < 20) errors.push(`Expected at least 20 styles, found ${count}`);
}

if (existsSync('data/characters.yaml')) {
  const characters = read('data/characters.yaml');
  const count = (characters.match(/id: CHAR-/g) || []).length;
  if (count < 10) errors.push(`Expected at least 10 characters, found ${count}`);
}

if (existsSync('content/daily')) {
  const dailyFiles = readdirSync('content/daily').filter((name) => name.endsWith('.md'));
  for (const name of dailyFiles) {
    if (!/^lesson-\d{3}\.md$/.test(name)) {
      errors.push(`Daily file should use lesson-###.md naming: ${join('content/daily', name)}`);
    }
  }
}

if (existsSync('content/packets')) {
  const packetFiles = readdirSync('content/packets').filter((name) => name.endsWith('.yaml'));
  for (const name of packetFiles) {
    if (!/^lesson-\d{3}\.yaml$/.test(name)) {
      errors.push(`Packet file should use lesson-###.yaml naming: ${join('content/packets', name)}`);
    }
  }
}

if (errors.length) {
  console.error('Validation failed:');
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}

console.log('Continuity validation passed.');
