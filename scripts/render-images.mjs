#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';
import { 
  parseLessonPacket, 
  resolveCharacterReference, 
  generatePageImage, 
  savePageImage, 
  gitPushAssets 
} from './pipeline-utils.mjs';

// Load config or default values
const workspaceRoot = process.cwd();
const autoPush = process.env.AUTO_PUSH === 'true';
const defaultModel = process.env.IMAGE_MODEL || 'gemini-3.1-flash-lite-image';

/**
 * Renders the 4 graphic novel pages for a specific lesson.
 * @param {number} lessonNumber 
 */
async function renderLesson(lessonNumber) {
  const padded = String(lessonNumber).padStart(3, '0');
  console.log(`==================================================`);
  console.log(`Starting rendering for Lesson ${lessonNumber}...`);
  console.log(`==================================================`);

  // 1. Parse lesson packet
  const packet = parseLessonPacket(lessonNumber);
  console.log(`Parsed packet for Lesson ${lessonNumber}.`);
  console.log(`Character ID: ${packet.characterId}`);
  console.log(`Style ID: ${packet.styleId}`);

  // 2. Resolve character reference
  let refImagePath;
  try {
    refImagePath = resolveCharacterReference(packet.characterId);
    console.log(`Resolved character reference: ${refImagePath}`);
  } catch (error) {
    console.error(`Warning: Could not resolve reference image for character ${packet.characterId}. Image generation will proceed without a visual seed.`, error.message);
  }

  const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  // 3. Generate each of the 4 pages
  for (const page of packet.pages) {
    console.log(`Generating Page ${page.pageNum}/4...`);
    console.log(`Prompt: "${page.prompt.slice(0, 100)}..."`);
    
    let attempts = 0;
    const maxAttempts = 3;
    let imageBuffer;
    
    while (attempts < maxAttempts) {
      try {
        attempts++;
        imageBuffer = await generatePageImage(page.prompt, refImagePath, {
          model: defaultModel
        });
        break; // Success
      } catch (error) {
        if (attempts >= maxAttempts) {
          console.error(`Error generating Page ${page.pageNum} after ${maxAttempts} attempts:`, error.message);
          throw error;
        }
        
        console.warn(`Attempt ${attempts} failed: ${error.message}. Retrying in 15 seconds...`);
        await sleep(15000);
      }
    }

    const savedPath = savePageImage(lessonNumber, page.pageNum, imageBuffer);
    console.log(`Successfully saved: ${savedPath}`);
    
    // Add a small delay between pages to prevent immediate rate limit triggers
    await sleep(2000);
  }

  // 4. Git Push if enabled
  if (autoPush) {
    gitPushAssets(lessonNumber);
  }

  console.log(`Finished rendering Lesson ${lessonNumber}!\n`);
}

/**
 * Finds all lessons currently present in the content/packets/ directory.
 * @returns {number[]} Array of sorted lesson numbers
 */
function getAvailableLessons() {
  const dirPath = path.join(workspaceRoot, 'content/packets');
  if (!fs.existsSync(dirPath)) return [];

  const files = fs.readdirSync(dirPath);
  return files
    .map(file => {
      const match = file.match(/^lesson-(\d{3})\.yaml$/);
      return match ? parseInt(match[1], 10) : null;
    })
    .filter(num => num !== null)
    .sort((a, b) => a - b);
}

/**
 * Checks if images for a given lesson already exist.
 * @param {number} lessonNumber 
 * @returns {boolean}
 */
function imagesExistForLesson(lessonNumber) {
  const padded = String(lessonNumber).padStart(3, '0');
  const dirPath = path.join(workspaceRoot, 'assets/images', `lesson-${padded}`);
  if (!fs.existsSync(dirPath)) return false;

  // Check if all 4 pages exist
  for (let i = 1; i <= 4; i++) {
    if (!fs.existsSync(path.join(dirPath, `page-${i}.png`))) {
      return false;
    }
  }
  return true;
}

async function main() {
  const args = process.argv.slice(2);
  const isLoop = args.includes('--loop') || args.includes('-l');
  
  // Try to find a specific lesson number in the arguments
  let specifiedLesson = null;
  for (const arg of args) {
    const match = arg.match(/^(?:--lesson=)?(\d+)$/);
    if (match) {
      specifiedLesson = parseInt(match[1], 10);
      break;
    }
  }

  // Pull latest changes before proceeding to make sure we are synced
  try {
    console.log("Syncing with GitHub repository (git pull)...");
    execSync('git pull', { stdio: 'inherit' });
  } catch (error) {
    console.warn("Warning: git pull failed, proceeding with local files.", error.message);
  }

  const available = getAvailableLessons();
  if (available.length === 0) {
    console.error("No lesson packets found in content/packets/. Please generate packets first.");
    process.exit(1);
  }

  if (isLoop) {
    console.log("Running in Loop Mode to render all missing lesson images...");
    for (const num of available) {
      if (!imagesExistForLesson(num)) {
        try {
          await renderLesson(num);
        } catch (error) {
          console.error(`Failed to render Lesson ${num}, continuing with next lessons.`, error.message);
        }
      } else {
        console.log(`Skipping Lesson ${num}: images already exist.`);
      }
    }
  } else {
    // Single lesson mode
    const targetLesson = specifiedLesson || available[available.length - 1];
    if (!available.includes(targetLesson)) {
      console.error(`Error: Lesson packet for ${targetLesson} does not exist in content/packets/`);
      process.exit(1);
    }
    
    try {
      await renderLesson(targetLesson);
    } catch (error) {
      console.error(`Failed to render Lesson ${targetLesson}:`, error.message);
      process.exit(1);
    }
  }
}

main().catch(error => {
  console.error("Fatal error running pipeline:", error.message);
  process.exit(1);
});
