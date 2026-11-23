import type { APIRoute } from 'astro';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { extractAuthToken, hashSha256 } from '@malihub/git-headless-cms-core';

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

interface LocalFileChange {
  path: string;
  isBinary: boolean;
  content?: string;
  buffer?: Buffer;
}

function findContentFiles(dir: string, baseDir: string = dir): LocalFileChange[] {
  const changes: LocalFileChange[] = [];
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
        changes.push({ path: relPath, isBinary: false, content });
      }
    }
  }
  return changes;
}

function findUploadFiles(projectRoot: string): LocalFileChange[] {
  const uploadsDir = path.join(projectRoot, 'public', 'uploads');
  const changes: LocalFileChange[] = [];
  if (!fs.existsSync(uploadsDir)) return changes;

  const entries = fs.readdirSync(uploadsDir, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.isFile() && !entry.name.startsWith('.')) {
      const fullPath = path.join(uploadsDir, entry.name);
      const relPath = `public/uploads/${entry.name}`;
      const buffer = fs.readFileSync(fullPath);
      changes.push({ path: relPath, isBinary: true, buffer });
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
  const baseUrl = 'https://api.github.com';
  const headers = {
    'Authorization': `token ${gitToken}`,
    'Accept': 'application/vnd.github.v3+json',
    'Content-Type': 'application/json',
    'User-Agent': 'git-headless-cms-campus',
  };

  try {
    const projectRoot = process.cwd();
    const candidateDirs = [
      path.join(projectRoot, 'src', 'data'),
      path.join(projectRoot, 'data'),
      path.join(projectRoot, 'src', 'content'),
      path.join(projectRoot, 'content'),
    ];

    const contentDirs = candidateDirs.filter((d) => fs.existsSync(d));
    const allLocalFilesMap = new Map<string, LocalFileChange>();

    for (const cDir of contentDirs) {
      const filesInDir = findContentFiles(cDir, projectRoot);
      for (const f of filesInDir) {
        allLocalFilesMap.set(f.path, f);
      }
    }

    // Inclure les fichiers médias uploadés dans public/uploads
    const uploadFiles = findUploadFiles(projectRoot);
    for (const uf of uploadFiles) {
      allLocalFilesMap.set(uf.path, uf);
    }

    const allLocalFiles = Array.from(allLocalFilesMap.values());

    if (allLocalFiles.length === 0) {
      return new Response(
        JSON.stringify({
          success: true,
          message: 'No files to publish.',
          gitPushed: false,
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } }
      );
    }

    // Récupérer la référence de la branche cible
    const baseBranch = process.env.CMS_GIT_BASE_BRANCH || 'main';
    let refRes = await fetch(`${baseUrl}/repos/${gitOwner}/${gitRepo}/git/ref/heads/${targetBranch}`, { headers });
    let latestCommitSha: string;

    if (!refRes.ok) {
      if (refRes.status === 404 && baseBranch && baseBranch !== targetBranch) {
        const baseRefRes = await fetch(`${baseUrl}/repos/${gitOwner}/${gitRepo}/git/ref/heads/${baseBranch}`, { headers });
        if (!baseRefRes.ok) {
          throw new Error(`Failed to retrieve base branch '${baseBranch}': ${baseRefRes.status}`);
        }
        const baseRefData = await baseRefRes.json();
        latestCommitSha = baseRefData.object.sha;

        const createRefRes = await fetch(`${baseUrl}/repos/${gitOwner}/${gitRepo}/git/refs`, {
          method: 'POST',
          headers,
          body: JSON.stringify({ ref: `refs/heads/${targetBranch}`, sha: latestCommitSha }),
        });
        if (!createRefRes.ok) {
          throw new Error(`Failed to create branch '${targetBranch}': ${createRefRes.status}`);
        }
      } else {
        throw new Error(`Failed to retrieve branch '${targetBranch}': ${refRes.status}`);
      }
    } else {
      const refData = await refRes.json();
      latestCommitSha = refData.object.sha;
    }

    // Récupérer le commit parent et son arbre complet
    const commitRes = await fetch(`${baseUrl}/repos/${gitOwner}/${gitRepo}/git/commits/${latestCommitSha}`, { headers });
    if (!commitRes.ok) {
      throw new Error(`Failed to retrieve parent commit (${latestCommitSha})`);
    }
    const commitData = await commitRes.json();
    const baseTreeSha = commitData.tree.sha;

    const treeFullRes = await fetch(`${baseUrl}/repos/${gitOwner}/${gitRepo}/git/trees/${baseTreeSha}?recursive=1`, { headers });
    const remoteTreeMap = new Map<string, string>();
    if (treeFullRes.ok) {
      const treeFullData = await treeFullRes.json();
      if (treeFullData.tree) {
        for (const item of treeFullData.tree) {
          if (item.type === 'blob') {
            remoteTreeMap.set(item.path, item.sha);
          }
        }
      }
    }

    // Déterminer les fichiers modifiés ou nouveaux
    const treeItems: any[] = [];
    for (const f of allLocalFiles) {
      const buf = f.isBinary ? f.buffer! : Buffer.from(f.content!, 'utf-8');
      const header = `blob ${buf.length}\0`;
      const localSha = crypto.createHash('sha1').update(Buffer.concat([Buffer.from(header), buf])).digest('hex');
      const remoteSha = remoteTreeMap.get(f.path);

      if (remoteSha !== localSha) {
        if (f.isBinary) {
          // Créer un blob base64 pour les binaires / images
          const blobRes = await fetch(`${baseUrl}/repos/${gitOwner}/${gitRepo}/git/blobs`, {
            method: 'POST',
            headers,
            body: JSON.stringify({
              content: buf.toString('base64'),
              encoding: 'base64',
            }),
          });
          if (!blobRes.ok) {
            const errTxt = await blobRes.text();
            throw new Error(`Failed to create Git blob for ${f.path}: ${errTxt}`);
          }
          const blobData = await blobRes.json();
          treeItems.push({
            path: f.path,
            mode: '100644',
            type: 'blob',
            sha: blobData.sha,
          });
        } else {
          // Fichier texte direct
          treeItems.push({
            path: f.path,
            mode: '100644',
            type: 'blob',
            content: f.content!,
          });
        }
      }
    }

    if (treeItems.length === 0) {
      return new Response(
        JSON.stringify({
          success: true,
          message: 'All content files and uploads are identical to remote repository. Nothing to commit.',
          gitPushed: false,
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } }
      );
    }

    // Créer le nouvel arbre Git
    const createTreeRes = await fetch(`${baseUrl}/repos/${gitOwner}/${gitRepo}/git/trees`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        base_tree: baseTreeSha,
        tree: treeItems,
      }),
    });
    if (!createTreeRes.ok) {
      const errTxt = await createTreeRes.text();
      throw new Error(`Failed to create Git tree: ${errTxt}`);
    }
    const treeData = await createTreeRes.json();
    const newTreeSha = treeData.sha;

    // Créer le commit
    const createCommitRes = await fetch(`${baseUrl}/repos/${gitOwner}/${gitRepo}/git/commits`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        message: 'cms(publish): update course content and uploads via editor',
        tree: newTreeSha,
        parents: [latestCommitSha],
      }),
    });
    if (!createCommitRes.ok) {
      const errTxt = await createCommitRes.text();
      throw new Error(`Failed to create Git commit: ${errTxt}`);
    }
    const newCommitData = await createCommitRes.json();
    const newCommitSha = newCommitData.sha;

    // Mettre à jour la branche
    const updateRefRes = await fetch(`${baseUrl}/repos/${gitOwner}/${gitRepo}/git/refs/heads/${targetBranch}`, {
      method: 'PATCH',
      headers,
      body: JSON.stringify({ sha: newCommitSha, force: false }),
    });
    if (!updateRefRes.ok) {
      const errTxt = await updateRefRes.text();
      throw new Error(`Failed to update branch reference: ${errTxt}`);
    }

    // Gérer la Pull Request si nécessaire
    let prUrl: string | undefined;
    let prNumber: number | undefined;
    const createPrEnv = process.env.CMS_CREATE_PR;
    const shouldCreatePr = createPrEnv !== undefined
      ? (String(createPrEnv).toLowerCase() === 'true' || String(createPrEnv) === '1')
      : (targetBranch !== baseBranch && targetBranch !== 'prod');

    if (shouldCreatePr && baseBranch && baseBranch !== targetBranch) {
      try {
        const prRes = await fetch(`${baseUrl}/repos/${gitOwner}/${gitRepo}/pulls`, {
          method: 'POST',
          headers,
          body: JSON.stringify({
            title: `cms(content): updates from web editor`,
            head: targetBranch,
            base: baseBranch,
            body: `### CMS Publication\n\nAutomated publication from CMS Web Editor.\nCommit: ${newCommitSha}\nFiles modified: ${treeItems.length}`,
          }),
        });
        if (prRes.ok) {
          const prData = await prRes.json();
          prUrl = prData.html_url;
          prNumber = prData.number;
        } else if (prRes.status === 422) {
          const existingPrRes = await fetch(`${baseUrl}/repos/${gitOwner}/${gitRepo}/pulls?head=${gitOwner}:${targetBranch}&base=${baseBranch}&state=open`, { headers });
          if (existingPrRes.ok) {
            const existingPrs = await existingPrRes.json();
            if (existingPrs.length > 0) {
              prUrl = existingPrs[0].html_url;
              prNumber = existingPrs[0].number;
            }
          }
        }
      } catch {
        // Ignorer les erreurs d'ouverture de PR si le commit est déjà poussé
      }
    }

    return new Response(
      JSON.stringify({
        success: true,
        message: `Successfully published changes and uploads to GitHub (Commit: ${newCommitSha.substring(0, 7)}).`,
        gitPushed: true,
        commitSha: newCommitSha,
        pullRequestUrl: prUrl,
        pullRequestNumber: prNumber,
      }),
      { status: 200, headers: { 'Content-Type': 'application/json' } }
    );
  } catch (gitErr: any) {
    return new Response(
      JSON.stringify({
        success: false,
        message: `Error publishing via API on GitHub: ${gitErr.message}`,
        errors: [gitErr.message],
      }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
};
