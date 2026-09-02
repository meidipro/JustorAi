import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const PRIVATE_GUIDES = path.join(ROOT, 'content/private/generated/guides');
const PUBLIC_ROOT = path.join(ROOT, 'src/content/generated/public');
const PUBLIC_GUIDES = path.join(PUBLIC_ROOT, 'guides');
const DIST = path.join(ROOT, 'dist');

const listFiles = async (root: string): Promise<string[]> => {
  const entries = await readdir(root, { withFileTypes: true });
  const files: string[] = [];
  for (const entry of entries) {
    const full = path.join(root, entry.name);
    if (entry.isDirectory()) files.push(...await listFiles(full));
    else files.push(full);
  }
  return files;
};

const privateFiles = (await readdir(PRIVATE_GUIDES)).filter((file) => file.endsWith('.json'));
if (privateFiles.length !== 60) {
  throw new Error(`Boundary verification expected 60 private guides; found ${privateFiles.length}`);
}

const publicIndex = JSON.parse(
  await readFile(path.join(PUBLIC_ROOT, 'guide-index.json'), 'utf8'),
) as Array<{ id: number; publishedLocales: string[] }>;
const publicGuideFiles = (await readdir(PUBLIC_GUIDES)).filter((file) => file.endsWith('.json'));
const expectedPublicBodies = publicIndex.reduce(
  (total, guide) => total + guide.publishedLocales.length,
  0,
);
if (publicGuideFiles.length !== expectedPublicBodies) {
  throw new Error(
    `Public index expects ${expectedPublicBodies} locale bodies; found ${publicGuideFiles.length}`,
  );
}

const reviewGuideIds: string[] = [];
const forbiddenReviewText: string[] = [];
for (const id of reviewGuideIds) {
  const guide = JSON.parse(
    await readFile(path.join(PRIVATE_GUIDES, `${id}.json`), 'utf8'),
  ) as { content: { en: { title: string; directAnswer: string } } };
  forbiddenReviewText.push(guide.content.en.title, guide.content.en.directAnswer.slice(0, 96));
}

const forbiddenPublicText = [
  ...forbiddenReviewText,
  'content/private/generated',
  'Verified information is unavailable right now.',
  'No canonical record was returned by the connected source.',
  "Bangladesh's first bilingual Legal Intelligence Ecosystem",
  'Zero Hallucination Guarantee',
  'Guarantees absolute precision',
  "40% of lawyers' billable hours wasted",
  'AI securely locked into our verified database',
  'TAM: 77.7M active mobile internet users',
  'SOM: 10,000 Active Users',
];

const inspectable = (await listFiles(DIST)).filter((file) => /\.(?:html|js|css|json|map|txt)$/i.test(file));
for (const file of inspectable) {
  const body = await readFile(file, 'utf8');
  for (const forbidden of forbiddenPublicText) {
    if (body.includes(forbidden)) {
      throw new Error(`Production artifact leaked forbidden text in ${path.relative(DIST, file)}: ${forbidden}`);
    }
  }
}

process.stdout.write(
  `Public guide boundary verified: 60 private guides; ${publicIndex.length} public index records; `
  + `${publicGuideFiles.length} public locale bodies; 3 review-guide fingerprints absent from dist.\n`,
);
