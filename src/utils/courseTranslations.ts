import fs from 'node:fs';
import path from 'node:path';
import { SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, type LanguageConfig } from './languages';

export interface CourseData {
  id: string;
  course_code?: string;
  title: string;
  category?: string;
  summary?: string;
  total_pages?: number;
  pages: Array<{
    page_number: number;
    title: string;
    text: string;
    illustration_description?: string;
    image?: string;
  }>;
}

export interface AvailableTranslation {
  lang: string;
  config: LanguageConfig;
  url: string;
  courseCode: string;
  title: string;
  pdfFileName: string;
  pdfUrl: string;
}

/**
 * Nettoie une chaîne pour en faire un slug sûr tout en préservant le N'ko et les lettres accentuées
 */
export function slugify(text: string): string {
  return text
    .normalize('NFKD')
    .replace(/[^\p{L}\p{N}\s-]/gu, '')
    .trim()
    .replace(/[-\s]+/g, '-');
}

const LANG_SUFFIXES: Record<string, string> = {
  fr: 'FR',
  en: 'EN',
  de: 'DE',
  'bm-latn': 'Bamanankan',
  'bm-nko': 'Nko'
};

/**
 * Calcule le nom de fichier PDF clair et standardisé
 * Format : [Cursus]-[Code]-[Titre]-[Langue].pdf
 * Exemple : Semences-S2.14-Produire-ses-semences-de-Carotte-FR.pdf
 */
export function buildPdfFileName(cursusName: string, courseCode: string, title: string, lang: string): string {
  const cleanCursus = cursusName === 'maraichage' ? 'Maraichage' : 'Semences';
  const cleanCode = courseCode.replace(/[^a-zA-Z0-9.-]/g, '');
  const cleanTitle = slugify(title) || 'Cours';
  const langLabel = LANG_SUFFIXES[lang] || lang.toUpperCase();
  return `${cleanCursus}-${cleanCode}-${cleanTitle}-${langLabel}.pdf`;
}

/**
 * Charge les traductions disponibles pour un cours donné
 */
export function getAvailableTranslations(dataDir: string, courseId: string, basePath: string): AvailableTranslation[] {
  const translations: AvailableTranslation[] = [];
  const cursusName = basePath.includes('maraichage') ? 'maraichage' : 'semences';

  // Vérifier la version par défaut (ex: b14_carotte.json)
  const defaultPath = path.join(dataDir, `${courseId}.json`);
  if (fs.existsSync(defaultPath)) {
    try {
      const content: CourseData = JSON.parse(fs.readFileSync(defaultPath, 'utf-8'));
      const courseCode = content.course_code || courseId.split('_')[0].toUpperCase();
      const title = content.title || courseId;
      const pdfFileName = buildPdfFileName(cursusName, courseCode, title, DEFAULT_LANGUAGE);
      translations.push({
        lang: DEFAULT_LANGUAGE,
        config: SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE],
        url: `${basePath}/${courseId}`,
        courseCode,
        title,
        pdfFileName,
        pdfUrl: `/pdf/${cursusName}/${pdfFileName}`
      });
    } catch (e) {
      // Fallback
    }
  }

  // Vérifier les variantes linguistiques (ex: b14_carotte.en.json, b14_carotte.bm-nko.json)
  for (const [langCode, config] of Object.entries(SUPPORTED_LANGUAGES)) {
    if (langCode === DEFAULT_LANGUAGE) continue;
    const langFilePath = path.join(dataDir, `${courseId}.${langCode}.json`);
    if (fs.existsSync(langFilePath)) {
      try {
        const content: CourseData = JSON.parse(fs.readFileSync(langFilePath, 'utf-8'));
        const courseCode = content.course_code || courseId.split('_')[0].toUpperCase();
        const title = content.title || courseId;
        const pdfFileName = buildPdfFileName(cursusName, courseCode, title, langCode);
        translations.push({
          lang: langCode,
          config,
          url: `${basePath}/${courseId}/${langCode}`,
          courseCode,
          title,
          pdfFileName,
          pdfUrl: `/pdf/${cursusName}/${pdfFileName}`
        });
      } catch (e) {
        // Fallback
      }
    }
  }

  return translations;
}
