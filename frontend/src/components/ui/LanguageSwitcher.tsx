"use client";

import { useI18n, LOCALES } from "@/i18n";

export default function LanguageSwitcher({ variant = "default" }: { variant?: "default" | "compact" }) {
  const { locale, setLocale } = useI18n();

  if (variant === "compact") {
    return (
      <div className="flex rounded-lg overflow-hidden border border-white/20 text-xs">
        {LOCALES.map((l) => (
          <button
            key={l.code}
            onClick={() => setLocale(l.code)}
            className={`px-2 py-1 transition ${
              locale === l.code
                ? "bg-white/20 text-white font-medium"
                : "text-blue-200 hover:bg-white/10"
            }`}
          >
            {l.code.toUpperCase()}
          </button>
        ))}
      </div>
    );
  }

  return (
    <div className="flex rounded-lg overflow-hidden border border-slate-200 text-sm">
      {LOCALES.map((l) => (
        <button
          key={l.code}
          onClick={() => setLocale(l.code)}
          className={`px-3 py-1.5 transition ${
            locale === l.code
              ? "bg-[#1e3a5f] text-white font-medium"
              : "text-slate-600 hover:bg-slate-50"
          }`}
        >
          {l.code.toUpperCase()}
        </button>
      ))}
    </div>
  );
}
