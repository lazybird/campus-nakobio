export async function hashSha256(message: string): Promise<string> {
  const text = (message || '').trim();
  if (!text) return '';
  const cryptoObj = typeof window !== 'undefined' ? window.crypto : globalThis.crypto;
  if (cryptoObj?.subtle) {
    const msgBuffer = new TextEncoder().encode(text);
    const hashBuffer = await cryptoObj.subtle.digest('SHA-256', msgBuffer);
    return Array.from(new Uint8Array(hashBuffer))
      .map((b) => b.toString(16).padStart(2, '0'))
      .join('');
  }
  // Node.js fallback
  try {
    const nodeCrypto = await import('crypto');
    return nodeCrypto.createHash('sha256').update(text).digest('hex');
  } catch {
    return '';
  }
}

export function getAdminCookieToken(): string | null {
  if (typeof document === 'undefined') return null;
  const match = document.cookie.match(/(?:^|; )cms_admin_token=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : null;
}

export function setAdminCookieToken(token: string) {
  if (typeof document === 'undefined') return;
  const expires = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toUTCString();
  document.cookie = `cms_admin_token=${encodeURIComponent(token)}; path=/; expires=${expires}; SameSite=Lax`;
}

export function clearAdminCookieToken() {
  if (typeof document === 'undefined') return;
  document.cookie = 'cms_admin_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax';
}
