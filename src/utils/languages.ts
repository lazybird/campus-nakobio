export interface LanguageConfig {
  code: string;
  name: string;
  nativeName: string;
  dir: 'ltr' | 'rtl';
  flag?: string;
  shortLabel: string;
}

export const SUPPORTED_LANGUAGES: Record<string, LanguageConfig> = {
  fr: {
    code: 'fr',
    name: 'Français',
    nativeName: 'Français',
    dir: 'ltr',
    shortLabel: 'FR'
  },
  en: {
    code: 'en',
    name: 'Anglais',
    nativeName: 'English',
    dir: 'ltr',
    shortLabel: 'EN'
  },
  de: {
    code: 'de',
    name: 'Allemand',
    nativeName: 'Deutsch',
    dir: 'ltr',
    shortLabel: 'DE'
  },
  'bm-latn': {
    code: 'bm-latn',
    name: 'Bamanankan (Latin)',
    nativeName: 'Bamanankan',
    dir: 'ltr',
    shortLabel: 'BM'
  },
  'bm-nko': {
    code: 'bm-nko',
    name: "N'ko",
    nativeName: 'ߒߞߏ',
    dir: 'rtl',
    shortLabel: 'ߒߞߏ'
  }
};

export const DEFAULT_LANGUAGE = 'fr';
