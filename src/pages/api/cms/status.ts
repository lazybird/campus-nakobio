import type { APIRoute } from 'astro';
import { extractAuthToken, hashSha256 } from '@malihub/git-headless-cms-core';

export const prerender = false;

async function handleStatus(request: Request) {
  const token = extractAuthToken(request);
  const rawSecret = process.env.CMS_ADMIN_SECRET || '';
  const expectedHash = await hashSha256(rawSecret);
  const authenticated = Boolean(token && token === expectedHash);

  const envGitEnabled = process.env.CMS_GIT_ENABLED;
  const isGitEnabled = String(envGitEnabled).toLowerCase() === 'true' || String(envGitEnabled) === '1';

  return new Response(
    JSON.stringify({
      status: 'ok',
      version: '0.1.3',
      authenticated,
      git: {
        enabled: isGitEnabled,
        branch: process.env.CMS_GIT_BRANCH || 'content',
        provider: process.env.GIT_PROVIDER || 'github',
        repo: process.env.GIT_REPO || 'campus-nakobio',
      },
    }),
    { status: 200, headers: { 'Content-Type': 'application/json' } }
  );
}

export const GET: APIRoute = async ({ request }) => {
  return handleStatus(request);
};

export const POST: APIRoute = async ({ request }) => {
  return handleStatus(request);
};
