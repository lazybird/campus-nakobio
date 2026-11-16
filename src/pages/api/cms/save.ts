import type { APIRoute } from 'astro';
import fs from 'node:fs';
import path from 'node:path';
import { extractAuthToken, hashSha256 } from '@malihub/git-headless-cms-core';

export const prerender = false;

function setDeepProperty(obj: any, propPath: string, value: any) {
  const normalizedPath = propPath.replace(/\[(\d+)\]/g, '.$1');
  const parts = normalizedPath.split('.').filter(Boolean);
  let current = obj;
  for (let i = 0; i < parts.length - 1; i++) {
    const part = parts[i];
    if (!(part in current) || typeof current[part] !== 'object' || current[part] === null) {
      current[part] = {};
    }
    current = current[part];
  }
  current[parts[parts.length - 1]] = value;
}

export const POST: APIRoute = async ({ request }) => {
  const token = extractAuthToken(request);
  const rawSecret = process.env.CMS_ADMIN_SECRET || '';
  const expectedHash = await hashSha256(rawSecret);

  if (!token || token !== expectedHash) {
    return new Response(
      JSON.stringify({ success: false, message: 'Unauthorized: Invalid or missing token.' }),
      { status: 401, headers: { 'Content-Type': 'application/json' } }
    );
  }

  let body: any;
  try {
    body = await request.json();
  } catch {
    return new Response(
      JSON.stringify({ success: false, message: 'Invalid JSON payload.' }),
      { status: 400, headers: { 'Content-Type': 'application/json' } }
    );
  }

  const { drafts = {} } = body;
  const projectRoot = process.cwd();
  const updatedFilesSet = new Set<string>();
  const errors: string[] = [];

  const jsonDraftsByFile: Record<string, Record<string, any>> = {};

  for (const [key, value] of Object.entries(drafts)) {
    if (key.includes('::')) {
      const [relPath, fieldKey] = key.split('::');
      if (relPath.endsWith('.json')) {
        if (!jsonDraftsByFile[relPath]) {
          jsonDraftsByFile[relPath] = {};
        }
        let parsedVal: any = value;
        if (typeof value === 'string' && (value.startsWith('{') || value.startsWith('['))) {
          try {
            parsedVal = JSON.parse(value);
          } catch {
            parsedVal = value;
          }
        }
        jsonDraftsByFile[relPath][fieldKey] = parsedVal;
      }
    }
  }

  for (const [relPath, fields] of Object.entries(jsonDraftsByFile)) {
    const fullPath = path.join(projectRoot, relPath);
    try {
      if (fs.existsSync(fullPath)) {
        const fileContent = fs.readFileSync(fullPath, 'utf-8');
        const jsonObj = JSON.parse(fileContent);

        for (const [fieldKey, value] of Object.entries(fields)) {
          setDeepProperty(jsonObj, fieldKey, value);
        }

        fs.writeFileSync(fullPath, JSON.stringify(jsonObj, null, 2), 'utf-8');
        updatedFilesSet.add(relPath);
      } else {
        errors.push(`JSON file not found: ${relPath}`);
      }
    } catch (err: any) {
      errors.push(`Error updating JSON file ${relPath}: ${err.message}`);
    }
  }

  const updatedFiles = Array.from(updatedFilesSet);
  if (errors.length > 0) {
    return new Response(
      JSON.stringify({
        success: false,
        message: `Save completed with ${errors.length} error(s).`,
        updatedFiles,
        errors,
      }),
      { status: 207, headers: { 'Content-Type': 'application/json' } }
    );
  }

  return new Response(
    JSON.stringify({
      success: true,
      message: `${updatedFiles.length} file(s) updated locally on disk.`,
      updatedFiles,
    }),
    { status: 200, headers: { 'Content-Type': 'application/json' } }
  );
};
