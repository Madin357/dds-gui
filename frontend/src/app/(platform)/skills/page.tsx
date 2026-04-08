"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

interface MarketTrend {
  id: string; occupation: string; sector: string | null;
  demand_level: string | null; growth_rate: number | null;
  avg_salary_azn: number | null; job_postings: number | null;
}
interface SkillTrend {
  id: string; skill_name: string; category: string | null;
  demand_level: string | null; growth_rate: number | null; future_outlook: string | null;
}
interface Alignment {
  name: string; code: string | null;
  relevance_score: number | null; demand_trend: string | null;
}

function DemandBadge({ level }: { level: string | null }) {
  if (!level) return <span className="text-xs text-slate-400">—</span>;
  const cls: Record<string, string> = {
    high: "bg-green-100 text-green-700", medium: "bg-amber-100 text-amber-700",
    low: "bg-slate-100 text-slate-600", declining: "bg-red-100 text-red-700",
    emerging: "bg-blue-100 text-blue-700",
  };
  return <span className={`px-2 py-0.5 rounded text-xs font-medium capitalize ${cls[level] || "bg-slate-100 text-slate-600"}`}>{level}</span>;
}

export default function SkillsPage() {
  const [trends, setTrends] = useState<MarketTrend[]>([]);
  const [skills, setSkills] = useState<SkillTrend[]>([]);
  const [alignment, setAlignment] = useState<Alignment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiFetch<MarketTrend[]>("/labour-market/trends"),
      apiFetch<SkillTrend[]>("/labour-market/skills"),
      apiFetch<Alignment[]>("/labour-market/alignment"),
    ])
      .then(([t, s, a]) => { setTrends(t); setSkills(s); setAlignment(a); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="animate-pulse text-slate-400 py-8">Loading market data...</div>;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Skills & Labour Market</h1>
        <p className="text-sm text-slate-500 mt-1">Align programs with current and future market demand</p>
      </div>

      {/* Programme Alignment */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-sm font-semibold text-slate-700 mb-4">Programme Market Alignment</h2>
        <table className="w-full text-sm">
          <thead className="border-b">
            <tr>
              <th className="text-left px-3 py-2 font-medium text-slate-600">Program</th>
              <th className="px-3 py-2 font-medium text-slate-600">Relevance Score</th>
              <th className="text-center px-3 py-2 font-medium text-slate-600">Demand Trend</th>
            </tr>
          </thead>
          <tbody>
            {alignment.map((a, i) => (
              <tr key={i} className="border-b border-slate-50">
                <td className="px-3 py-2.5 text-slate-700 font-medium">{a.name}</td>
                <td className="px-3 py-2.5">
                  <div className="flex items-center gap-2">
                    <div className="w-24 bg-slate-100 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${(a.relevance_score || 0) >= 70 ? "bg-green-500" : (a.relevance_score || 0) >= 50 ? "bg-amber-400" : "bg-red-500"}`}
                        style={{ width: `${a.relevance_score || 0}%` }}
                      />
                    </div>
                    <span className="text-xs font-medium">{a.relevance_score?.toFixed(0) || "—"}/100</span>
                  </div>
                </td>
                <td className="px-3 py-2.5 text-center"><DemandBadge level={a.demand_trend} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Labour Market Trends */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-sm font-semibold text-slate-700 mb-4">Labour Market Trends</h2>
        <table className="w-full text-sm">
          <thead className="border-b">
            <tr>
              <th className="text-left px-3 py-2 font-medium text-slate-600">Occupation</th>
              <th className="text-left px-3 py-2 font-medium text-slate-600">Sector</th>
              <th className="text-center px-3 py-2 font-medium text-slate-600">Demand</th>
              <th className="text-right px-3 py-2 font-medium text-slate-600">Growth</th>
              <th className="text-right px-3 py-2 font-medium text-slate-600">Avg Salary (AZN)</th>
              <th className="text-right px-3 py-2 font-medium text-slate-600">Postings</th>
            </tr>
          </thead>
          <tbody>
            {trends.map((t) => (
              <tr key={t.id} className="border-b border-slate-50">
                <td className="px-3 py-2.5 text-slate-700 font-medium">{t.occupation}</td>
                <td className="px-3 py-2.5 text-slate-500">{t.sector}</td>
                <td className="px-3 py-2.5 text-center"><DemandBadge level={t.demand_level} /></td>
                <td className={`px-3 py-2.5 text-right font-medium ${(t.growth_rate || 0) > 0 ? "text-green-600" : "text-red-500"}`}>
                  {(t.growth_rate || 0) > 0 ? "+" : ""}{t.growth_rate?.toFixed(1)}%
                </td>
                <td className="px-3 py-2.5 text-right text-slate-700">{t.avg_salary_azn?.toLocaleString()}</td>
                <td className="px-3 py-2.5 text-right text-slate-500">{t.job_postings}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Skills Grid */}
      <div>
        <h2 className="text-sm font-semibold text-slate-700 mb-4">In-Demand Skills</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {skills.map((s) => (
            <div key={s.id} className="bg-white rounded-lg shadow-sm p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-slate-700">{s.skill_name}</h3>
                <DemandBadge level={s.demand_level} />
              </div>
              <div className="flex items-center justify-between text-xs text-slate-500">
                <span className="capitalize">{s.category}</span>
                <span className={`font-medium ${(s.growth_rate || 0) > 0 ? "text-green-600" : "text-red-500"}`}>
                  {s.future_outlook === "growing" ? "↑" : s.future_outlook === "declining" ? "↓" : "→"} {s.growth_rate?.toFixed(0)}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
