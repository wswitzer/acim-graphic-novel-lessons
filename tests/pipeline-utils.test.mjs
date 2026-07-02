import { test } from 'node:test';
import assert from 'node:assert';
import { resolveCharacterReference, parseLessonPacket, generatePageImage, savePageImage, gitPushAssets } from '../scripts/pipeline-utils.mjs';
import fs from 'node:fs';
import path from 'node:path';


test('resolveCharacterReference resolves CHAR-006 to Mateo Alvarez reference path', () => {
  const result = resolveCharacterReference('CHAR-006');
  assert.ok(result.endsWith('assets/characters/mateo-alvarez/Mateo_ACIM_reference.png'), `Expected path to end with Mateo's reference image, got: ${result}`);
});

test('resolveCharacterReference resolves CHAR-011 to Lucia Bell reference path', () => {
  const result = resolveCharacterReference('CHAR-011');
  assert.ok(result.endsWith('assets/characters/lucia-bell/Lucia_ACIM_reference.png'), `Expected path to end with Lucia's reference image, got: ${result}`);
});

test('parseLessonPacket loads lesson 182 and constructs 4 complete page prompts', () => {
  const packet = parseLessonPacket(182);
  assert.strictEqual(packet.lessonNumber, 182);
  assert.strictEqual(packet.characterId, 'CHAR-006');
  assert.strictEqual(packet.styleId, 'STYLE-002');
  assert.strictEqual(packet.pages.length, 4);

  // Verify prompt merge logic
  const page1 = packet.pages.find(p => p.pageNum === 1);
  assert.ok(page1.prompt.includes('Dreamlike Watercolor graphic novel pages')); // from overall style
  assert.ok(page1.prompt.includes('Page 1, "The Errand Road"')); // from page 1 prompt
});

test('generatePageImage constructs correct payload and calls Google GenAI SDK', async () => {
  // We use Mateo's reference file since we know it exists
  const refPath = resolveCharacterReference('CHAR-006');
  
  let calledWith = null;
  const mockAiClient = {
    models: {
      async generateContent(params) {
        calledWith = params;
        return {
          candidates: [{
            content: {
              parts: [{
                inlineData: {
                  mimeType: 'image/png',
                  data: Buffer.from('mocked-image-bytes').toString('base64')
                }
              }]
            }
          }]
        };
      }
    }
  };

  const imageBuffer = await generatePageImage('Test page prompt', refPath, {
    aiClient: mockAiClient,
    model: 'gemini-3.1-flash-lite-image'
  });

  // Verify the return value is correct
  assert.strictEqual(imageBuffer.toString(), 'mocked-image-bytes');

  // Verify call parameters
  assert.ok(calledWith);
  assert.strictEqual(calledWith.model, 'gemini-3.1-flash-lite-image');
  assert.ok(Array.isArray(calledWith.contents));
  assert.ok(calledWith.contents.includes('Test page prompt'));
  
  const inlineImagePart = calledWith.contents.find(p => p.inlineData);
  assert.ok(inlineImagePart);
  assert.strictEqual(inlineImagePart.inlineData.mimeType, 'image/png');
  assert.ok(inlineImagePart.inlineData.data.length > 0); // Contains base64 data
});

test('savePageImage writes the image to the correct directory and file', () => {
  const dummyLesson = 999;
  const dummyPage = 1;
  const dummyData = Buffer.from('fake-png-content');

  const relativePath = savePageImage(dummyLesson, dummyPage, dummyData);

  // Check returned relative path
  assert.strictEqual(relativePath, 'assets/images/lesson-999/page-1.png');

  // Check actual file exists
  const absolutePath = path.join(process.cwd(), relativePath);
  assert.ok(fs.existsSync(absolutePath), `File should exist at: ${absolutePath}`);
  
  // Verify contents
  const savedData = fs.readFileSync(absolutePath);
  assert.strictEqual(savedData.toString(), 'fake-png-content');

  // Cleanup
  fs.unlinkSync(absolutePath);
  fs.rmdirSync(path.dirname(absolutePath));
});

test('gitPushAssets executes git commands in sequence when autoPush is true', () => {
  const commandsRun = [];
  const mockExec = (cmd) => {
    commandsRun.push(cmd);
    return Buffer.from('success');
  };

  gitPushAssets(182, {
    autoPush: true,
    exec: mockExec
  });

  assert.strictEqual(commandsRun.length, 3);
  assert.ok(commandsRun[0].includes('git add assets/images/lesson-182'));
  assert.ok(commandsRun[1].includes('git commit -m "Render images for Lesson 182"'));
  assert.ok(commandsRun[2].includes('git push'));
});

test('gitPushAssets does nothing when autoPush is false', () => {
  const commandsRun = [];
  const mockExec = (cmd) => {
    commandsRun.push(cmd);
    return Buffer.from('success');
  };

  gitPushAssets(182, {
    autoPush: false,
    exec: mockExec
  });

  assert.strictEqual(commandsRun.length, 0);
});




