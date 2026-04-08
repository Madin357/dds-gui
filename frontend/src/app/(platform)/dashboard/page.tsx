"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import KPICard from "@/components/ui/KPICard";
import { useI18n } from "@/i18n";

interface DashboardData {
  kpis: { total_students: number; active_students: number; total_programs: number; avg_gpa: number | null; overall_attendance: number | null; overall_pass_rate: number | null; overall_dropout_rate: number | null; at_risk_students: number; high_risk_students: number; };
  enrollment_trend: { period: string; count: number }[];
  risk_distribution: { high: number; medium: number; low: number };
  top_programs: { name: string; performance_score: number | null; completion_rate: number | null }[];
  recent_recommendations: { id: string; title: string; category: string; level: string; priority_score: number | null }[];
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const { t } = useI18n();

  useEffect(() => {
    apiFetch<DashboardData>("/analytics/dashboard").then(setData).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-slate-900">{t("dashboard.title")}</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <div key={i} className="bg-white rounded-lg shadow-sm h-28 animate-pulse" />)}
        </div>
      </div>
    );
  }

  if (!data) return <p className="text-slate-500">{t("dashboard.failedLoad")}</p>;
  const { kpis, risk_distribution, top_programs, recent_recommendations, enrollment_trend } = data;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{t("dashboard.title")}</h1>
        <p className="text-sm text-slate-500 mt-1">{t("dashboard.subtitle")}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard title={t("dashboard.activeStudents")} value={kpis.active_students} subtitle={t("dashboard.ofTotal", { count: kpis.total_students })} color="border-[#0ea5e9]" />
        <KPICard title={t("dashboard.attendanceRate")} value={kpis.overall_attendance ? `${kpis.overall_attendance.toFixed(1)}%` : t("common.na")} subtitle={t("dashboard.overall")} color="border-[#22c55e]" />
        <KPICard title={t("dashboard.passRate")} value={kpis.overall_pass_rate ? `${kpis.overall_pass_rate.toFixed(1)}%` : t("common.na")} subtitle={t("dashboard.gpaAbove")} color="border-[#0ea5e9]" />
        <KPICard title={t("dashboard.atRiskStudents")} value={kpis.at_risk_students} subtitle={t("dashboard.highRiskCount", { count: kpis.high_risk_students })} color="border-[#ef4444]" trend={kpis.high_risk_students > 0 ? "up" : "neutral"} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-sm font-semibold text-slate-700 mb-4">{t("dashboard.riskDistribution")}</h2>
          <div className="space-y-3">
            <RiskBar label={t("dashboard.highRisk")} count={risk_distribution.high} total={risk_distribution.high + risk_distribution.medium + risk_distribution.low} color="bg-red-500" />
            <RiskBar label={t("dashboard.mediumRisk")} count={risk_distribution.medium} total={risk_distribution.high + risk_distribution.medium + risk_distribution.low} color="bg-amber-400" />
            <RiskBar label={t("dashboard.lowRisk")} count={risk_distribution.low} total={risk_distribution.high + risk_distribution.medium + risk_distribution.low} color="bg-green-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-sm font-semibold text-slate-700 mb-4">{t("dashboard.enrollmentByYear")}</h2>
          <div className="space-y-2">
            {enrollment_trend.map((item) => (
              <div key={item.period} className="flex items-center gap-3">
                <span className="text-xs text-slate-500 w-12">{item.period}</span>
                <div className="flex-1 bg-slate-100 rounded-full h-5 overflow-hidden">
                  <div className="bg-[#0ea5e9] h-full rounded-full flex items-center pl-2" style={{ width: `${Math.min(100, (item.count / Math.max(...enrollment_trend.map((e) => e.count))) * 100)}%` }}>
                    <span className="text-xs text-white font-medium">{item.count}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-sm font-semibold text-slate-700 mb-4">{t("dashboard.quickStats")}</h2>
          <div className="space-y-4">
            <Stat label={t("dashboard.programs")} value={kpis.total_programs} />
            <Stat label={t("dashboard.averageGpa")} value={kpis.avg_gpa?.toFixed(2) || t("common.na")} />
            <Stat label={t("dashboard.dropoutRate")} value={kpis.overall_dropout_rate ? `${kpis.overall_dropout_rate.toFixed(1)}%` : t("common.na")} />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-sm font-semibold text-slate-700 mb-4">{t("dashboard.programPerformance")}</h2>
          <table className="w-full text-sm">
            <thead><tr className="text-left text-slate-500 border-b"><th className="pb-2 font-medium">{t("dashboard.program")}</th><th className="pb-2 font-medium text-right">{t("dashboard.score")}</th><th className="pb-2 font-medium text-right">{t("dashboard.completion")}</th></tr></thead>
            <tbody>
              {top_programs.map((p, i) => (
                <tr key={i} className="border-b border-slate-50">
                  <td className="py-2.5 text-slate-700">{p.name}</td>
                  <td className="py-2.5 text-right"><span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${(p.performance_score || 0) >= 70 ? "bg-green-100 text-green-700" : (p.performance_score || 0) >= 50 ? "bg-amber-100 text-amber-700" : "bg-red-100 text-red-700"}`}>{p.performance_score?.toFixed(0) || "—"}</span></td>
                  <td className="py-2.5 text-right text-slate-600">{p.completion_rate?.toFixed(0) || "—"}%</td>
                </tr>
              ))}
              {top_programs.length === 0 && <tr><td colSpan={3} className="py-4 text-center text-slate-400">{t("common.noData")}</td></tr>}
            </tbody>
          </table>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-sm font-semibold text-slate-700 mb-4">{t("dashboard.topRecommendations")}</h2>
          <div className="space-y-3">
            {recent_recommendations.map((r) => (
              <div key={r.id} className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg">
                <span className={`shrink-0 mt-0.5 px-2 py-0.5 rounded text-xs font-medium ${r.category === "new_program" ? "bg-blue-100 text-blue-700" : r.category === "intervention" ? "bg-red-100 text-red-700" : r.category === "curriculum" ? "bg-purple-100 text-purple-700" : "bg-slate-200 text-slate-600"}`}>{r.category.replace("_", " ")}</span>
                <div className="min-w-0">
                  <p className="text-sm font-medium text-slate-700 truncate">{r.title}</p>
                  <p className="text-xs text-slate-400">{r.level} {t("dashboard.level")} • {t("dashboard.priority")}: {r.priority_score?.toFixed(0) || "—"}</p>
                </div>
              </div>
            ))}
            {recent_recommendations.length === 0 && <p className="text-sm text-slate-400 text-center py-4">{t("dashboard.noRecommendations")}</p>}
          </div>
        </div>
      </div>
    </div>
  );
}

function RiskBar({ label, count, total, color }: { label: string; count: number; total: number; color: string }) {
  const pct = total > 0 ? (count / total) * 100 : 0;
  return (<div><div className="flex justify-between text-xs mb-1"><span className="text-slate-600">{label}</span><span className="font-medium text-slate-700">{count}</span></div><div className="w-full bg-slate-100 rounded-full h-2"><div className={`${color} h-2 rounded-full`} style={{ width: `${pct}%` }} /></div></div>);
}
function Stat({ label, value }: { label: string; value: string | number }) {
  return (<div className="flex justify-between items-center"><span className="text-sm text-slate-500">{label}</span><span className="text-sm font-semibold text-slate-700">{String(value)}</span></div>);
}
