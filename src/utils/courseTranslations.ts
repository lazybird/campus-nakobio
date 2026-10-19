import fs from 'node:fs';
import path from 'node:path';
import { SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, type LanguageConfig } from './languages';

export interface CourseData {
  id: string;
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
}

/**
 * Charge les traductions disponibles pour un cours donné
 */
export function getAvailableTranslations(dataDir: string, courseId: string, basePath: string): AvailableTranslation[] {
  const translations: AvailableTranslation[] = [];

  // Vérifier la version par défaut (ex: b14_carotte.json)
  const defaultPath = path.join(dataDir, `${courseId}.json`);
  if (fs.existsSync(defaultPath)) {
    translations.push({
      lang: DEFAULT_LANGUAGE,
      config: SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE],
      url: `${basePath}/${courseId}`
    });
  }

  // Vérifier les variantes linguistiques (ex: b14_carotte.en.json, b14_carotte.bm-nko.json)
  for (const [langCode, config] of Object.entries(SUPPORTED_LANGUAGES)) {
    if (langCode === DEFAULT_LANGUAGE) continue;
    const langFilePath = path.join(dataDir, `${courseId}.${langCode}.json`);
    if (fs.existsSync(langFilePath)) {
      translations.push({
        lang: langCode,
        config,
        url: `${basePath}/${courseId}/${langCode}`
      });
    }
  }

  return translations;
}
