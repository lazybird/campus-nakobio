import type { APIRoute } from 'astro';
import fs from 'node:fs';
import path from 'node:path';

export const prerender = false;

const MIME_TYPES: Record<string, string> = {
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
};

export const GET: APIRoute = async ({ params }) => {
  const filePathParam = params.file;
  if (!filePathParam) {
    return new Response('Not found', { status: 404 });
  }

  // Empêcher directory traversal
  const safeFileName = path.basename(filePathParam);
  const projectRoot = process.cwd();

  // Chercher dans dist/client/uploads puis dans public/uploads
  const candidates = [
    path.join(projectRoot, 'dist', 'client', 'uploads', safeFileName),
    path.join(projectRoot, 'public', 'uploads', safeFileName),
  ];

  let foundPath: string | null = null;
  for (const c of candidates) {
    if (fs.existsSync(c)) {
      foundPath = c;
      break;
    }
  }

  if (!foundPath) {
    return new Response('Image not found', { status: 404 });
  }

  const ext = path.extname(safeFileName).toLowerCase();
  const contentType = MIME_TYPES[ext] || 'application/octet-stream';
  const fileBuffer = fs.readFileSync(foundPath);

  return new Response(fileBuffer, {
    status: 200,
    headers: {
      'Content-Type': contentType,
      'Cache-Control': 'public, max-age=31536000, immutable',
    },
  });
};
