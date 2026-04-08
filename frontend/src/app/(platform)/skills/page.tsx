"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useI18n } from "@/i18n";

interface MarketTrend { id: string; occupation: string; sector: string | null; demand_level: string | null; growth_rate: number | null; avg_salary_azn: number | null; job_postings: number | null; }
interface SkillTrend { id: string; skill_name: string; category: string | null; demand_level: string | null; growth_rate: number | null; future_outlook: string | null; }
interface Alignment { name: string; code: string | null; relevance_score: number | null; demand_trend: string | null; }

export default function SkillsPage() {
  const [trends, setTrends] = useState<MarketTrend[]>([]);
  const [skills, setSkills] = useState<SkillTrend[]>([]);
  const [alignment, setAlignment] = useState<Alignment[]>([]);
  const [loading, setLoading] = useState(true);
  const { t } = useI18n();

  useEffect(() => {
    Promise.all([
      apiFetch<MarketTrend[]>("/labour-market/trends"),
      apiFetch<SkillTrend[]>("/labour-market/skills"),
      apiFetch<Alignment[]>("/labour-market/alignment"),
    ]).then(([tr, sk, al]) => { setTrends(tr); setSkills(sk); setAlignment(al); }).catch(console.error).finally(() => setLoading(false));
  }, []);

  function DemandBadge({ level }: { level: string | null }) {
    if (!level) return <span className="text-xs text-slate-400">—</span>;
    const cls: Record<string, string> = { high: "bg-green-100 text-green-700", medium: "bg-amber-100 text-amber-700", low: "bg-slate-100 text-slate-600", declining: "bg-red-100 text-red-700", emerging: "bg-blue-100 text-blue-700" };
    const label = t(`skills.${level}` as any) || level;
    return <span className={`px-2 py-0.5 rounded text-xs font-medium capitalize ${cls[level] || "bg-slate-100 text-slate-600"}`}>{label}</span>;
  }

  if (loading) return <div className="animate-pulse text-slate-400 py-8">{t("skills.loading")}</div>;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{t("skills.title")}</h1>
        <p className="text-sm text-slate-500 mt-1">{t("skills.subtitle")}</p>
      </div>

      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-sm font-semibold text-slate-700 mb-4">{t("skills.programmeAlignment")}</h2>
        <table className="w-full text-sm">
          <thead className="border-b"><tr><th className="text-left px-3 py-2 font-medium text-slate-600">{t("skills.program")}</th><th className="px-3 py-2 font-medium text-slate-600">{t("skills.relevanceScore")}</th><th className="text-center px-3 py-2 font-medium text-slate-600">{t("skills.demandTrend")}</th></tr></thead>
          <tbody>
            {alignment.map((a, i) => (
              <tr key={i} className="border-b border-slate-50">
                <td className="px-3 py-2.5 text-slate-700 font-medium">{t(`programNames.${a.name}` as any) || a.name}</td>
                <td className="px-3 py-2.5"><div className="flex items-center gap-2"><div className="w-24 bg-slate-100 rounded-full h-2"><div className={`h-2 rounded-full ${(a.relevance_score || 0) >= 70 ? "bg-green-500" : (a.relevance_score || 0) >= 50 ? "bg-amber-400" : "bg-red-500"}`} style={{ width: `${a.relevance_score || 0}%` }} /></div><span className="text-xs font-medium">{a.relevance_score?.toFixed(0) || "—"}/100</span></div></td>
                <td className="px-3 py-2.5 text-center"><DemandBadge level={a.demand_trend} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-sm font-semibold text-slate-700 mb-4">{t("skills.labourTrends")}</h2>
        <table className="w-full text-sm">
          <thead className="border-b"><tr><th className="text-left px-3 py-2 font-medium text-slate-600">{t("skills.occupation")}</th><th className="text-left px-3 py-2 font-medium text-slate-600">{t("skills.sector")}</th><th className="text-center px-3 py-2 font-medium text-slate-600">{t("skills.demand")}</th><th className="text-right px-3 py-2 font-medium text-slate-600">{t("skills.growth")}</th><th className="text-right px-3 py-2 font-medium text-slate-600">{t("skills.avgSalary")}</th><th className="text-right px-3 py-2 font-medium text-slate-600">{t("skills.postings")}</th></tr></thead>
          <tbody>
            {trends.map((tr) => (
              <tr key={tr.id} className="border-b border-slate-50">
                <td className="px-3 py-2.5 text-slate-700 font-medium">{t(`occupations.${tr.occupation}` as any) || tr.occupation}</td>
                <td className="px-3 py-2.5 text-slate-500">{tr.sector ? (t(`sectors.${tr.sector}` as any) || tr.sector) : ""}</td>
                <td className="px-3 py-2.5 text-center"><DemandBadge level={tr.demand_level} /></td>
                <td className={`px-3 py-2.5 text-right font-medium ${(tr.growth_rate || 0) > 0 ? "text-green-600" : "text-red-500"}`}>{(tr.growth_rate || 0) > 0 ? "+" : ""}{tr.growth_rate?.toFixed(1)}%</td>
                <td className="px-3 py-2.5 text-right text-slate-700">{tr.avg_salary_azn?.toLocaleString()}</td>
                <td className="px-3 py-2.5 text-right text-slate-500">{tr.job_postings}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div>
        <h2 className="text-sm font-semibold text-slate-700 mb-4">{t("skills.inDemandSkills")}</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {skills.map((s) => (
            <div key={s.id} className="bg-white rounded-lg shadow-sm p-4">
              <div className="flex items-center justify-between mb-2"><h3 className="text-sm font-medium text-slate-700">{t(`skillNames.${s.skill_name}` as any) || s.skill_name}</h3><DemandBadge level={s.demand_level} /></div>
              <div className="flex items-center justify-between text-xs text-slate-500">
                <span className="capitalize">{s.category ? (t(`skills.${s.category}` as any) || s.category) : ""}</span>
                <span className={`font-medium ${(s.growth_rate || 0) > 0 ? "text-green-600" : "text-red-500"}`}>{s.future_outlook === "growing" ? "↑" : s.future_outlook === "declining" ? "↓" : "→"} {s.growth_rate?.toFixed(0)}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
