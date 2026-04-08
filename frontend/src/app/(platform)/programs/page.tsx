"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useI18n } from "@/i18n";

interface Program { id: string; name: string; code: string | null; level: string | null; department: string | null; performance_score: number | null; completion_rate: number | null; pass_rate: number | null; avg_gpa: number | null; dropout_rate: number | null; enrollment_trend: string | null; relevance_score: number | null; demand_trend: string | null; student_count: number | null; }

function ScoreBar({ value }: { value: number | null }) {
  if (value === null) return <span className="text-xs text-slate-400">—</span>;
  const pct = Math.min(100, value);
  const color = value >= 70 ? "bg-green-500" : value >= 50 ? "bg-amber-400" : "bg-red-500";
  return (<div className="flex items-center gap-2"><div className="w-20 bg-slate-100 rounded-full h-2"><div className={`${color} h-2 rounded-full`} style={{ width: `${pct}%` }} /></div><span className="text-xs font-medium text-slate-600">{value.toFixed(0)}</span></div>);
}

export default function ProgramsPage() {
  const [programs, setPrograms] = useState<Program[]>([]);
  const [loading, setLoading] = useState(true);
  const { t } = useI18n();

  useEffect(() => {
    apiFetch<{ items: Program[]; total: number }>("/programs").then((d) => setPrograms(d.items)).catch(console.error).finally(() => setLoading(false));
  }, []);

  function TrendBadge({ trend }: { trend: string | null }) {
    if (!trend) return <span className="text-xs text-slate-400">—</span>;
    const cls = trend === "growing" ? "bg-green-100 text-green-700" : trend === "declining" ? "bg-red-100 text-red-700" : "bg-slate-100 text-slate-600";
    const label = t(`programs.${trend}` as any) || trend;
    return <span className={`px-2 py-0.5 rounded text-xs font-medium capitalize ${cls}`}>{label}</span>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{t("programs.title")}</h1>
        <p className="text-sm text-slate-500 mt-1">{t("programs.subtitle")}</p>
      </div>
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-slate-600">{t("programs.program")}</th>
              <th className="text-right px-4 py-3 font-medium text-slate-600">{t("programs.students")}</th>
              <th className="text-right px-4 py-3 font-medium text-slate-600">{t("programs.completion")}</th>
              <th className="text-right px-4 py-3 font-medium text-slate-600">{t("programs.passRate")}</th>
              <th className="text-right px-4 py-3 font-medium text-slate-600">{t("programs.avgGpa")}</th>
              <th className="text-right px-4 py-3 font-medium text-slate-600">{t("programs.dropout")}</th>
              <th className="px-4 py-3 font-medium text-slate-600">{t("programs.performance")}</th>
              <th className="px-4 py-3 font-medium text-slate-600">{t("programs.relevance")}</th>
              <th className="text-center px-4 py-3 font-medium text-slate-600">{t("programs.trend")}</th>
            </tr>
          </thead>
          <tbody>
            {loading ? [...Array(5)].map((_, i) => (<tr key={i}><td colSpan={9} className="px-4 py-3"><div className="h-4 bg-slate-100 rounded animate-pulse" /></td></tr>))
            : programs.map((p) => (
              <tr key={p.id} className="border-b border-slate-50 hover:bg-slate-50">
                <td className="px-4 py-3"><div><p className="font-medium text-slate-700">{p.name}</p><p className="text-xs text-slate-400">{p.code} • {p.department || p.level}</p></div></td>
                <td className="px-4 py-3 text-right text-slate-700">{p.student_count ?? "—"}</td>
                <td className="px-4 py-3 text-right text-slate-700">{p.completion_rate?.toFixed(1) ?? "—"}%</td>
                <td className="px-4 py-3 text-right text-slate-700">{p.pass_rate?.toFixed(1) ?? "—"}%</td>
                <td className="px-4 py-3 text-right text-slate-700">{p.avg_gpa?.toFixed(2) ?? "—"}</td>
                <td className="px-4 py-3 text-right text-slate-700">{p.dropout_rate?.toFixed(1) ?? "—"}%</td>
                <td className="px-4 py-3"><ScoreBar value={p.performance_score} /></td>
                <td className="px-4 py-3"><ScoreBar value={p.relevance_score} /></td>
                <td className="px-4 py-3 text-center"><TrendBadge trend={p.enrollment_trend} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
