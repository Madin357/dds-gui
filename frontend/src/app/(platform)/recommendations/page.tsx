"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

interface Recommendation {
  id: string; level: string; category: string; title: string;
  description: string; ai_generated: boolean; priority_score: number | null;
  status: string; created_at: string;
}

const CATEGORY_COLORS: Record<string, string> = {
  new_program: "bg-blue-100 text-blue-700",
  curriculum: "bg-purple-100 text-purple-700",
  intervention: "bg-red-100 text-red-700",
  resource: "bg-amber-100 text-amber-700",
  policy: "bg-slate-200 text-slate-600",
};

export default function RecommendationsPage() {
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [levelFilter, setLevelFilter] = useState("");
  const [catFilter, setCatFilter] = useState("");

  useEffect(() => {
    let url = "/recommendations?status=active";
    if (levelFilter) url += `&level=${levelFilter}`;
    if (catFilter) url += `&category=${catFilter}`;
    apiFetch<{ items: Recommendation[]; total: number }>(url)
      .then((d) => setRecs(d.items))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [levelFilter, catFilter]);

  async function updateStatus(id: string, status: string) {
    try {
      await apiFetch(`/recommendations/${id}/status`, {
        method: "PUT",
        body: JSON.stringify({ status }),
      });
      setRecs((prev) => prev.filter((r) => r.id !== id));
    } catch (e) {
      console.error(e);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Recommendations</h1>
        <p className="text-sm text-slate-500 mt-1">AI-assisted suggestions based on analytics</p>
      </div>

      <div className="flex flex-wrap gap-3">
        <select value={levelFilter} onChange={(e) => setLevelFilter(e.target.value)}
          className="border border-slate-300 rounded-lg px-3 py-2 text-sm">
          <option value="">All Levels</option>
          <option value="institution">Institution</option>
          <option value="program">Program</option>
          <option value="student">Student</option>
        </select>
        <select value={catFilter} onChange={(e) => setCatFilter(e.target.value)}
          className="border border-slate-300 rounded-lg px-3 py-2 text-sm">
          <option value="">All Categories</option>
          <option value="new_program">New Program</option>
          <option value="curriculum">Curriculum</option>
          <option value="intervention">Intervention</option>
          <option value="resource">Resource</option>
          <option value="policy">Policy</option>
        </select>
        <span className="self-center text-sm text-slate-500">{recs.length} active recommendations</span>
      </div>

      {loading ? (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => <div key={i} className="bg-white rounded-lg shadow-sm h-32 animate-pulse" />)}
        </div>
      ) : recs.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm p-8 text-center text-slate-400">
          No active recommendations
        </div>
      ) : (
        <div className="space-y-4">
          {recs.map((r) => (
            <div key={r.id} className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2 mb-2">
                    {/* Priority badge */}
                    <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                      (r.priority_score || 0) >= 80 ? "bg-red-100 text-red-700" :
                      (r.priority_score || 0) >= 60 ? "bg-amber-100 text-amber-700" :
                      "bg-green-100 text-green-700"
                    }`}>
                      Priority: {r.priority_score?.toFixed(0) || "—"}
                    </span>
                    {/* Category */}
                    <span className={`px-2 py-0.5 rounded text-xs font-medium capitalize ${CATEGORY_COLORS[r.category] || "bg-slate-100 text-slate-600"}`}>
                      {r.category.replace("_", " ")}
                    </span>
                    {/* Level */}
                    <span className="px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-500 capitalize">
                      {r.level}
                    </span>
                    {r.ai_generated && (
                      <span className="px-2 py-0.5 rounded text-xs font-medium bg-violet-100 text-violet-700">
                        AI Generated
                      </span>
                    )}
                  </div>
                  <h3 className="text-base font-semibold text-slate-800">{r.title}</h3>
                  <p className="text-sm text-slate-600 mt-2 leading-relaxed">{r.description}</p>
                </div>

                <div className="flex flex-col gap-2 shrink-0">
                  <button
                    onClick={() => updateStatus(r.id, "accepted")}
                    className="px-4 py-1.5 text-xs font-medium bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
                  >
                    Accept
                  </button>
                  <button
                    onClick={() => updateStatus(r.id, "dismissed")}
                    className="px-4 py-1.5 text-xs font-medium bg-slate-200 text-slate-600 rounded-lg hover:bg-slate-300 transition"
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
