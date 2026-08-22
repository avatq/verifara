import { EvidenceReport, Classification } from "@/types/evidence";

const VERDICT_CONFIG = {
  not_ai: { label: "NOT AI", subtitle: "يبدو أن المحتوى حقيقي.", ring: "border-status-good", bg: "bg-status-good/10", text: "text-status-good", icon: "✓" },
  ai_generated: { label: "AI GENERATED", subtitle: "يبدو أن المحتوى مولَّد بالذكاء الاصطناعي.", ring: "border-status-conflict", bg: "bg-status-conflict/10", text: "text-status-conflict", icon: "⚠" },
  inconclusive: { label: "INCONCLUSIVE", subtitle: "الأدلة غير كافية لحكم قاطع.", ring: "border-status-minor", bg: "bg-status-minor/10", text: "text-status-minor", icon: "?" },
} as const;

const CLASSIFICATION_CONFIG: Record<Classification, { label: string; color: string }> = {
  ai_generated: { label: "AI-Generated", color: "bg-status-conflict/15 text-status-conflict border-status-conflict/40" },
  ai_assisted: { label: "AI-Assisted", color: "bg-status-minor/15 text-status-minor border-status-minor/40" },
  camera_capture: { label: "Camera Capture", color: "bg-status-good/15 text-status-good border-status-good/40" },
  unknown: { label: "Unknown", color: "bg-status-na/15 text-status-na border-status-na/40" },
};

function ClassificationBadge({ report }: { report: EvidenceReport }) {
  const cfg = CLASSIFICATION_CONFIG[report.classification];
  return (
    <span className={`inline-flex items-center rounded-md border px-2.5 py-1 text-xs font-semibold ${cfg.color}`}>
      {cfg.label}
    </span>
  );
}

export function VerdictCard({ report }: { report: EvidenceReport }) {
  const aiItem = report.items.find((i) => i.key === "ai_analysis");
  const hasRealAiSignal = aiItem && aiItem.level !== "na" && aiItem.score_percent !== null;

  if (!hasRealAiSignal) {
    return (
      <div className="rounded-2xl border-2 border-base-700 bg-base-900 p-6">
        <div className="flex items-center justify-between mb-2">
          <p className="text-xs uppercase tracking-wide text-slate-500">التقييم العام</p>
          <ClassificationBadge report={report} />
        </div>
        <h2 className="font-display text-2xl font-extrabold text-slate-100">{report.overall_assessment}</h2>
        <div className="mt-4 flex items-start gap-2 rounded-lg bg-base-950/40 p-3 text-xs text-slate-400">
          <span className="mt-0.5">ⓘ</span>
          <p>تعذّر تنفيذ تحليل الذكاء الاصطناعي المتخصص لهذا الملف. التقييم مبني على الأدلة الأخرى المتاحة فقط.</p>
        </div>
      </div>
    );
  }

  const cfg = VERDICT_CONFIG[report.verdict];

  return (
    <div className={`rounded-2xl border-2 ${cfg.ring} ${cfg.bg} p-6`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className={`flex h-14 w-14 items-center justify-center rounded-full ${cfg.bg} border-2 ${cfg.ring} text-2xl ${cfg.text}`}>
            {cfg.icon}
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-500">النتيجة الأساسية</p>
            <h2 className={`font-display text-2xl font-extrabold ${cfg.text}`}>{cfg.label}</h2>
            <p className="text-sm text-slate-400 mt-0.5">{cfg.subtitle}</p>
          </div>
        </div>
        <div className="flex flex-col items-end gap-2">
          <span className={`rounded-full border ${cfg.ring} px-3 py-1 text-xs font-semibold ${cfg.text}`}>
            الثقة: {report.confidence_label}
          </span>
          <ClassificationBadge report={report} />
        </div>
      </div>

      <div className="mt-4 flex items-start gap-2 rounded-lg bg-base-950/40 p-3 text-xs text-slate-400">
        <span className="mt-0.5">ⓘ</span>
        <p>هذه النتيجة احتمال وليست حكمًا قطعيًا. راجع الأدلة للتفاصيل.</p>
      </div>
    </div>
  );
}
