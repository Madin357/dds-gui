export default function KPICard({
  title,
  value,
  subtitle,
  trend,
  color = "border-[#0ea5e9]",
}: {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: "up" | "down" | "neutral";
  color?: string;
}) {
  const arrow =
    trend === "up" ? "↑" : trend === "down" ? "↓" : "";
  const trendColor =
    trend === "up"
      ? "text-green-600"
      : trend === "down"
        ? "text-red-500"
        : "text-slate-400";

  return (
    <div className={`bg-white rounded-lg shadow-sm border-l-4 ${color} p-5`}>
      <p className="text-sm font-medium text-slate-500">{title}</p>
      <div className="mt-1 flex items-baseline gap-2">
        <p className="text-2xl font-bold text-slate-900">{value}</p>
        {arrow && <span className={`text-sm font-medium ${trendColor}`}>{arrow} {subtitle}</span>}
      </div>
      {!arrow && subtitle && (
        <p className="mt-1 text-xs text-slate-400">{subtitle}</p>
      )}
    </div>
  );
}
