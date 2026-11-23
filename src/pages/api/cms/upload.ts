import type { APIRoute } from 'astro';
import fs from 'node:fs';
import path from 'node:path';
import { extractAuthToken, hashSha256 } from '@malihub/git-headless-cms-core';

export const prerender = false;

export const POST: APIRoute = async ({ request }) => {
  const token = extractAuthToken(request);
  const rawSecret = process.env.CMS_ADMIN_SECRET || '';
  const expectedHash = await hashSha256(rawSecret);

  if (!token || token !== expectedHash) {
    return new Response(
      JSON.stringify({ success: false, message: 'Unauthorized.' }),
      { status: 401, headers: { 'Content-Type': 'application/json' } }
    );
  }

  try {
    const formData = await request.formData();
    const file = formData.get('file') as File | null;

    if (!file) {
      return new Response(
        JSON.stringify({ success: false, message: 'No file provided.' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const projectRoot = process.cwd();
    const publicUploadDir = path.join(projectRoot, 'public', 'uploads');
    const distClientUploadDir = path.join(projectRoot, 'dist', 'client', 'uploads');

    if (!fs.existsSync(publicUploadDir)) {
      fs.mkdirSync(publicUploadDir, { recursive: true });
    }
    if (!fs.existsSync(distClientUploadDir)) {
      fs.mkdirSync(distClientUploadDir, { recursive: true });
    }

    const fileExt = path.extname(file.name) || '.png';
    const baseName = path.basename(file.name, fileExt).replace(/[^a-zA-Z0-9_-]/g, '-').toLowerCase();
    const fileName = `${baseName}-${Date.now()}${fileExt}`;
    const targetFilePath = path.join(publicUploadDir, fileName);
    const distTargetFilePath = path.join(distClientUploadDir, fileName);

    const arrayBuffer = await file.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    fs.writeFileSync(targetFilePath, buffer);
    try {
      fs.writeFileSync(distTargetFilePath, buffer);
    } catch {
      // Ignorer si dist/client/uploads n'existe pas en dev
    }

    const publicUrl = `/uploads/${fileName}`;

    return new Response(
      JSON.stringify({
        success: true,
        message: 'Image uploaded successfully.',
        url: publicUrl,
        filename: fileName,
      }),
      { status: 200, headers: { 'Content-Type': 'application/json' } }
    );
  } catch (err: any) {
    return new Response(
      JSON.stringify({ success: false, message: `Upload error: ${err.message}` }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
};
