import type { APIRoute } from 'astro';
import fs from 'node:fs';
import path from 'node:path';
import { extractAuthToken, hashSha256, getGitProvider, type GitFileChange } from '@malihub/git-headless-cms-core';

export const prerender = false;

const EXCLUDED_DIRS = new Set([
  'node_modules',
  '.git',
  '.astro',
  'dist',
  '.dev',
  '.gemini',
  '.vscode',
  'public',
  'assets',
  'scripts',
  'tests',
  'coverage',
]);

function findContentFiles(dir: string, baseDir: string = dir): GitFileChange[] {
  const changes: GitFileChange[] = [];
  if (!fs.existsSync(dir)) return changes;

  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (!EXCLUDED_DIRS.has(entry.name)) {
        changes.push(...findContentFiles(fullPath, baseDir));
      }
    } else if (entry.isFile()) {
      const isTextContent = (entry.name.endsWith('.json') || entry.name.endsWith('.md') || entry.name.endsWith('.mdx')) && entry.name !== 'package.json' && entry.name !== 'package-lock.json';
      if (isTextContent) {
        const relPath = path.relative(baseDir, fullPath).replace(/\\/g, '/');
        const content = fs.readFileSync(fullPath, 'utf-8');
        changes.push({ path: relPath, content });
      }
    }
  }
  return changes;
}

export const POST: APIRoute = async ({ request }) => {
  const token = extractAuthToken(request);
  const rawSecret = process.env.CMS_ADMIN_SECRET || '';
  const expectedHash = await hashSha256(rawSecret);

  if (!token || token !== expectedHash) {
    return new Response(
      JSON.stringify({ success: false, message: 'Unauthorized: Invalid or missing authentication token.' }),
      { status: 401, headers: { 'Content-Type': 'application/json' } }
    );
  }

  const envGitEnabled = process.env.CMS_GIT_ENABLED;
  const isGitEnabled = String(envGitEnabled).toLowerCase() === 'true' || String(envGitEnabled) === '1';

  if (!isGitEnabled) {
    return new Response(
      JSON.stringify({ success: false, message: 'Git publishing is not enabled (CMS_GIT_ENABLED=false).' }),
      { status: 400, headers: { 'Content-Type': 'application/json' } }
    );
  }

  const targetBranch = process.env.CMS_GIT_BRANCH || process.env.GIT_DEPLOY_BRANCH || 'content';
  const gitToken = process.env.GIT_TOKEN;
  if (!gitToken) {
    return new Response(
      JSON.stringify({
        success: false,
        message: 'Missing Git publication token (GIT_TOKEN undefined).',
        errors: ['Missing Git API token (GIT_TOKEN). Cannot publish.'],
      }),
      { status: 400, headers: { 'Content-Type': 'application/json' } }
    );
  }

  const gitOwner = process.env.GIT_OWNER || 'lazybird';
  const gitRepo = process.env.GIT_REPO || 'campus-nakobio';
  const providerType = process.env.GIT_PROVIDER || 'github';

  try {
    const projectRoot = process.cwd();
    const candidateDirs = [
      path.join(projectRoot, 'src', 'data'),
      path.join(projectRoot, 'data'),
      path.join(projectRoot, 'src', 'content'),
      path.join(projectRoot, 'content'),
    ];

    const contentDirs = candidateDirs.filter((d) => fs.existsSync(d));
    const modifiedFilesMap = new Map<string, GitFileChange>();

    for (const cDir of contentDirs) {
      const filesInDir = findContentFiles(cDir, projectRoot);
      for (const f of filesInDir) {
        modifiedFilesMap.set(f.path, f);
      }
    }

    const modifiedFiles = Array.from(modifiedFilesMap.values());

    if (modifiedFiles.length === 0) {
      return new Response(
        JSON.stringify({
          success: true,
          message: 'No content files (.json/.md) found to publish.',
          gitPushed: false,
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const baseBranch = process.env.CMS_GIT_BASE_BRANCH || 'main';
    const createPrEnv = process.env.CMS_CREATE_PR;
    const shouldCreatePr = createPrEnv !== undefined
      ? (String(createPrEnv).toLowerCase() === 'true' || String(createPrEnv) === '1')
      : (targetBranch !== baseBranch && targetBranch !== 'prod');

    const provider = getGitProvider(providerType);
    const result = await provider.publish({
      owner: gitOwner,
      repo: gitRepo,
      branch: targetBranch,
      baseBranch,
      createPullRequest: shouldCreatePr,
      commitMessage: 'cms(publish): update course content via editor',
      files: modifiedFiles,
      token: gitToken,
    });

    return new Response(
      JSON.stringify({
        success: true,
        message: result.message,
        gitPushed: true,
        commitSha: result.commitSha,
        pullRequestUrl: result.pullRequestUrl,
        pullRequestNumber: result.pullRequestNumber,
      }),
      { status: 200, headers: { 'Content-Type': 'application/json' } }
    );
  } catch (gitErr: any) {
    return new Response(
      JSON.stringify({
        success: false,
        message: `Error publishing via API on ${providerType}: ${gitErr.message}`,
        errors: [gitErr.message],
      }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
};
