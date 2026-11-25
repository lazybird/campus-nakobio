/**
 * Formate le texte pédagogique d'une slide (Markdown léger -> HTML).
 * Si le texte contient déjà des balises HTML bloc (cas d'un contenu édité
 * via l'éditeur WYSIWYG du CMS), il est renvoyé tel quel sans ré-enveloppage.
 */
const BLOCK_HTML_RE = /<(p|ul|ol|h[1-6]|div|blockquote|table)(\s|>)/i;

export function formatPedagogicalText(rawText?: string | null): string {
  if (!rawText || !rawText.trim()) {
    return '<p><em>Contenu technique en cours de finalisation</em></p>';
  }

  const trimmed = rawText.trim();
  if (BLOCK_HTML_RE.test(trimmed)) {
    return trimmed;
  }

  const html = rawText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  const lines = html.split('\n');
  let inList = false;
  let listType: 'ul' | 'ol' = 'ul';
  const formattedLines: string[] = [];

  for (let line of lines) {
    line = line.trim();
    if (!line) continue;

    if (line.startsWith('⚠️') || line.toLowerCase().startsWith('attention')) {
      if (inList) {
        formattedLines.push(`</${listType}>`);
        inList = false;
      }
      formattedLines.push(`<div class="slide-alert">${line}</div>`);
      continue;
    }

    const numMatch = line.match(/^(\d+)\.\s+(.*)/);
    if (numMatch) {
      if (!inList || listType !== 'ol') {
        if (inList) formattedLines.push(`</${listType}>`);
        formattedLines.push('<ol>');
        inList = true;
        listType = 'ol';
      }
      formattedLines.push(`<li>${numMatch[2]}</li>`);
      continue;
    }

    const bulletMatch = line.match(/^[-•]\s+(.*)/);
    if (bulletMatch) {
      if (!inList || listType !== 'ul') {
        if (inList) formattedLines.push(`</${listType}>`);
        formattedLines.push('<ul>');
        inList = true;
        listType = 'ul';
      }
      formattedLines.push(`<li>${bulletMatch[1]}</li>`);
      continue;
    }

    if (inList) {
      formattedLines.push(`</${listType}>`);
      inList = false;
    }
    formattedLines.push(`<p>${line}</p>`);
  }

  if (inList) {
    formattedLines.push(`</${listType}>`);
  }

  return formattedLines.join('');
}
