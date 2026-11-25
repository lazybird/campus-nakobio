import type { APIRoute } from 'astro';

export const prerender = false;

export const POST: APIRoute = async ({ cookies, redirect }) => {
  cookies.delete('cms_admin_token', { path: '/' });
  return redirect('/');
};

export const GET: APIRoute = async ({ cookies, redirect }) => {
  cookies.delete('cms_admin_token', { path: '/' });
  return redirect('/');
};
