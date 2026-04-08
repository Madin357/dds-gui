"use client";

import { useI18n } from "@/i18n";
import LanguageSwitcher from "@/components/ui/LanguageSwitcher";

export default function LandingPage() {
  const { t } = useI18n();

  return (
    <div className="min-h-screen bg-white">
      {/* Nav */}
      <nav className="border-b border-slate-100">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <img src="/logo.svg" alt="EduScope" className="w-9 h-9" />
            <span className="text-lg font-bold text-[#1e3a5f]">EduScope</span>
          </div>
          <div className="flex items-center gap-4">
            <LanguageSwitcher />
            <a href="/login" className="text-sm text-slate-600 hover:text-slate-900 transition">{t("common.signIn")}</a>
            <a href="/login" className="px-4 py-2 text-sm font-medium bg-[#1e3a5f] text-white rounded-lg hover:bg-[#2d5a8e] transition">
              {t("common.getStarted")}
            </a>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-block px-3 py-1 bg-blue-50 text-[#0ea5e9] text-xs font-medium rounded-full mb-6">
            {t("landing.tagline")}
          </div>
          <h1 className="text-5xl font-bold text-slate-900 leading-tight">
            {t("landing.heroTitle1")}<br />
            <span className="text-[#0ea5e9]">{t("landing.heroTitle2")}</span>
          </h1>
          <p className="mt-6 text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed">
            {t("landing.heroDesc")}
          </p>
          <div className="mt-10 flex items-center justify-center gap-4">
            <a href="/login" className="px-8 py-3 text-base font-medium bg-[#1e3a5f] text-white rounded-lg hover:bg-[#2d5a8e] transition shadow-lg shadow-blue-900/20">
              {t("landing.startDemo")}
            </a>
            <a href="#features" className="px-8 py-3 text-base font-medium text-slate-700 border border-slate-300 rounded-lg hover:bg-slate-50 transition">
              {t("landing.learnMore")}
            </a>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 bg-slate-50 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-slate-900 mb-4">{t("landing.featuresTitle")}</h2>
          <p className="text-center text-slate-500 mb-14 max-w-2xl mx-auto">{t("landing.featuresDesc")}</p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Feature icon="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" title={t("landing.featureRealtime")} desc={t("landing.featureRealtimeDesc")} />
            <Feature icon="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" title={t("landing.featureDropout")} desc={t("landing.featureDropoutDesc")} />
            <Feature icon="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" title={t("landing.featurePrograms")} desc={t("landing.featureProgramsDesc")} />
            <Feature icon="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" title={t("landing.featureMarket")} desc={t("landing.featureMarketDesc")} />
            <Feature icon="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" title={t("landing.featureAI")} desc={t("landing.featureAIDesc")} />
            <Feature icon="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" title={t("landing.featureSync")} desc={t("landing.featureSyncDesc")} />
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-slate-900 mb-14">{t("landing.howTitle")}</h2>
          <div className="space-y-8">
            <Step num={1} title={t("landing.step1Title")} desc={t("landing.step1Desc")} />
            <Step num={2} title={t("landing.step2Title")} desc={t("landing.step2Desc")} />
            <Step num={3} title={t("landing.step3Title")} desc={t("landing.step3Desc")} />
            <Step num={4} title={t("landing.step4Title")} desc={t("landing.step4Desc")} />
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-[#1e3a5f] px-6">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-white mb-4">{t("landing.ctaTitle")}</h2>
          <p className="text-blue-200 mb-8">{t("landing.ctaDesc")}</p>
          <a href="/login" className="inline-block px-8 py-3 text-base font-medium bg-white text-[#1e3a5f] rounded-lg hover:bg-slate-100 transition shadow-lg">
            {t("landing.requestDemo")}
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-slate-100">
        <div className="max-w-6xl mx-auto flex items-center justify-between text-sm text-slate-400">
          <span>{t("landing.footerLeft")}</span>
          <span>{t("landing.footerRight")}</span>
        </div>
      </footer>
    </div>
  );
}

function Feature({ icon, title, desc }: { icon: string; title: string; desc: string }) {
  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100">
      <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center mb-4">
        <svg className="w-5 h-5 text-[#0ea5e9]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d={icon} />
        </svg>
      </div>
      <h3 className="text-base font-semibold text-slate-800 mb-2">{title}</h3>
      <p className="text-sm text-slate-500 leading-relaxed">{desc}</p>
    </div>
  );
}

function Step({ num, title, desc }: { num: number; title: string; desc: string }) {
  return (
    <div className="flex gap-5">
      <div className="shrink-0 w-10 h-10 bg-[#1e3a5f] text-white rounded-full flex items-center justify-center text-sm font-bold">{num}</div>
      <div>
        <h3 className="text-lg font-semibold text-slate-800">{title}</h3>
        <p className="text-sm text-slate-500 mt-1">{desc}</p>
      </div>
    </div>
  );
}
