import fs from 'node:fs';
import path from 'node:path';
import * as yaml from 'js-yaml';
import { GoogleGenAI } from '@google/genai';
import dotenv from 'dotenv';
import { execSync } from 'node:child_process';

dotenv.config();

// Helper to resolve characters configuration path
const workspaceRoot = process.cwd();
const charactersYamlPath = path.join(workspaceRoot, 'data/characters.yaml');

/**
 * Slugify a character's name to match directory naming conventions
 * e.g., "Mateo Alvarez" -> "mateo-alvarez"
 * @param {string} name 
 * @returns {string}
 */
export function slugify(name) {
  return name
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // remove accents
    .replace(/[^a-z0-9]+/g, '-')    // replace non-alphanumeric with hyphen
    .replace(/(^-|-$)/g, '');       // trim hyphens
}

/**
 * Resolves the character ID to their corresponding reference image file path.
 * @param {string} characterId - e.g., "CHAR-006"
 * @returns {string} Absolute path to the reference image file
 */
export function resolveCharacterReference(characterId) {
  const content = fs.readFileSync(charactersYamlPath, 'utf8');
  const db = yaml.load(content);
  const character = db.characters.find(c => c.id === characterId);
  if (!character) {
    throw new Error(`Character not found in database: ${characterId}`);
  }

  const slug = slugify(character.name);
  const charDir = path.join(workspaceRoot, 'assets/characters', slug);

  if (!fs.existsSync(charDir)) {
    throw new Error(`Character reference directory does not exist: ${charDir}`);
  }

  const files = fs.readdirSync(charDir);
  const refFile = files.find(f => f.toLowerCase().endsWith('reference.png'));
  if (!refFile) {
    throw new Error(`No reference image found in ${charDir}`);
  }

  return path.join(charDir, refFile);
}

/**
 * Loads a daily lesson packet and constructs the merged page-by-page prompts.
 * @param {number|string} lessonNumber - e.g., 182
 * @returns {Object} Structured packet with merged prompts
 */
export function parseLessonPacket(lessonNumber) {
  const padded = String(lessonNumber).padStart(3, '0');
  const filename = `lesson-${padded}.yaml`;
  const packetPath = path.join(workspaceRoot, 'content/packets', filename);

  if (!fs.existsSync(packetPath)) {
    throw new Error(`Lesson packet file not found: ${packetPath}`);
  }

  const content = fs.readFileSync(packetPath, 'utf8');
  const packet = yaml.load(content);

  const characterId = packet.selection?.character_id;
  const styleId = packet.selection?.style_id;
  const imagePrompts = packet.image_prompts || {};
  const overallStyle = imagePrompts.overall || '';

  const pages = [];
  for (let i = 1; i <= 4; i++) {
    const pageKey = `page_${i}`;
    const pagePrompt = imagePrompts[pageKey] || '';
    
    // Combine the overall style and the page specific prompt
    const combinedPrompt = `${overallStyle.trim()}\n\n${pagePrompt.trim()}`;
    
    pages.push({
      pageNum: i,
      prompt: combinedPrompt.trim()
    });
  }

  return {
    lessonNumber: parseInt(lessonNumber, 10),
    characterId,
    styleId,
    pages
  };
}

/**
 * Call the Vertex AI image generation API with the prompt and character reference image.
 * @param {string} prompt - Prompt for the page
 * @param {string} referenceImagePath - Path to the reference image on disk
 * @param {Object} [options] - Options for the generation (model, projectId, location, client injection)
 * @returns {Promise<Buffer>} - Resolved PNG image buffer
 */
export async function generatePageImage(prompt, referenceImagePath, options = {}) {
  const {
    model = process.env.IMAGE_MODEL || 'gemini-3.1-flash-lite-image',
    projectId = process.env.GCP_PROJECT_ID,
    location = process.env.GCP_LOCATION || 'us-central1',
    aiClient = null
  } = options;

  if (!fs.existsSync(referenceImagePath)) {
    throw new Error(`Reference image not found at path: ${referenceImagePath}`);
  }

  const imageBytes = fs.readFileSync(referenceImagePath);
  const mimeType = referenceImagePath.toLowerCase().endsWith('.png') ? 'image/png' : 'image/jpeg';
  const base64Data = imageBytes.toString('base64');

  // Initialize the SDK client if not injected
  const ai = aiClient || new GoogleGenAI({
    vertexai: true,
    project: projectId,
    location: location
  });

  const response = await ai.models.generateContent({
    model: model,
    contents: [
      {
        inlineData: {
          data: base64Data,
          mimeType: mimeType
        }
      },
      prompt
    ],
    config: {
      imageConfig: {
        // Flash Lite Image defaults to 1K
        imageSize: '1K'
      }
    }
  });

  const candidate = response.candidates?.[0];
  const parts = candidate?.content?.parts;
  const imagePart = parts?.find(p => p.inlineData && p.inlineData.mimeType.startsWith('image/'));

  if (!imagePart || !imagePart.inlineData?.data) {
    throw new Error(`Failed to generate image. No image data returned in parts.`);
  }

  return Buffer.from(imagePart.inlineData.data, 'base64');
}

/**
 * Saves a page image buffer to assets/images/lesson-###/page-#.png.
 * Creates directories recursively if they don't exist.
 * @param {number|string} lessonNumber - e.g., 182
 * @param {number|string} pageNum - e.g., 1
 * @param {Buffer} imageBuffer - Buffer containing image bytes
 * @returns {string} Relative path of the saved file from project root (e.g. assets/images/lesson-182/page-1.png)
 */
export function savePageImage(lessonNumber, pageNum, imageBuffer) {
  const padded = String(lessonNumber).padStart(3, '0');
  const dirName = `lesson-${padded}`;
  const relativeDir = path.join('assets/images', dirName);
  const absoluteDir = path.join(workspaceRoot, relativeDir);

  if (!fs.existsSync(absoluteDir)) {
    fs.mkdirSync(absoluteDir, { recursive: true });
  }

  const filename = `page-${pageNum}.png`;
  const relativePath = path.join(relativeDir, filename);
  const absolutePath = path.join(absoluteDir, filename);

  fs.writeFileSync(absolutePath, imageBuffer);
  return relativePath;
}

/**
 * Automates the staging, committing, and pushing of rendered lesson assets.
 * @param {number|string} lessonNumber - e.g., 182
 * @param {Object} [options] - Options (autoPush override, exec injection)
 */
export function gitPushAssets(lessonNumber, options = {}) {
  const {
    autoPush = process.env.AUTO_PUSH === 'true',
    exec = execSync
  } = options;

  if (!autoPush) {
    return;
  }

  const padded = String(lessonNumber).padStart(3, '0');
  const folderPath = path.join('assets/images', `lesson-${padded}`);

  try {
    console.log(`Staging assets for Lesson ${lessonNumber}...`);
    exec(`git add ${folderPath}`, { stdio: 'inherit' });

    console.log(`Committing assets for Lesson ${lessonNumber}...`);
    exec(`git commit -m "Render images for Lesson ${lessonNumber}"`, { stdio: 'inherit' });

    console.log(`Pushing assets to remote repository...`);
    exec(`git push`, { stdio: 'inherit' });
    
    console.log(`Successfully pushed assets for Lesson ${lessonNumber} to GitHub!`);
  } catch (error) {
    console.error(`Git automation failed for Lesson ${lessonNumber}:`, error.message);
    throw error;
  }
}




