"use client";

import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from "react";
import en from "./locales/en.json";
import az from "./locales/az.json";

export type Locale = "en" | "az";

const translations: Record<Locale, Record<string, Record<string, string>>> = { en, az };

export const LOCALES: { code: Locale; label: string }[] = [
  { code: "en", label: "English" },
  { code: "az", label: "Azərbaycan" },
];

const STORAGE_KEY = "eduscope_lang";

interface I18nContextValue {
  locale: Locale;
  setLocale: (l: Locale) => void;
  t: (key: string, params?: Record<string, string | number>) => string;
}

const I18nContext = createContext<I18nContextValue | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("en");

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY) as Locale | null;
    if (stored && translations[stored]) {
      setLocaleState(stored);
    }
  }, []);

  const setLocale = useCallback((l: Locale) => {
    setLocaleState(l);
    localStorage.setItem(STORAGE_KEY, l);
  }, []);

  const t = useCallback(
    (key: string, params?: Record<string, string | number>): string => {
      // key format: "namespace.key" e.g. "dashboard.title"
      const [ns, ...rest] = key.split(".");
      const k = rest.join(".");
      const dict = translations[locale]?.[ns];
      let value = dict?.[k] ?? translations["en"]?.[ns]?.[k] ?? key;

      if (params) {
        for (const [p, v] of Object.entries(params)) {
          value = value.replace(`{${p}}`, String(v));
        }
      }
      return value;
    },
    [locale],
  );

  return (
    <I18nContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within I18nProvider");
  return ctx;
}
