import { EvidenceReport } from "@/types/evidence";

const VERDICT_CONFIG = {
  not_ai: {
    label: "NOT AI",
    subtitle: "يبدو أن المحتوى حقيقي.",
    ring: "border-status-good",
    bg: "bg-status-good/10",
    text: "text-status-good",
    icon: "✓",
  },
  ai_generated: {
    label: "AI GENERATED",
    subtitle: "يبدو أن المحتوى مولَّد بالذكاء الاصطناعي.",
    ring: "border-status-conflict",
    bg: "bg-status-conflict/10",
    text: "text-status-conflict",
    icon: "⚠",
  },
  inconclusive: {
    label: "INCONCLUSIVE",
    subtitle: "الأدلة غير كافية لحكم قاطع.",
    ring: "border-status-minor",
    bg: "bg-status-minor/10",
    text: "text-status-minor",
    icon: "?",
  },
} as const;

export function VerdictCard({ report }: { report: EvidenceReport }) {
  if (report.file_type !== "image") {
    return (
      <div className="rounded-2xl border-2 border-base-700 bg-base-900 p-6">
        <p className="text-xs uppercase tracking-wide text-slate-500 mb-1">التقييم العام</p>
        <h2 className="font-display text-2xl font-extrabold text-slate-100">{report.overall_assessment}</h2>
        <div className="mt-4 flex items-start gap-2 rounded-lg bg-base-950/40 p-3 text-xs text-slate-400">
          <span className="mt-0.5">ⓘ</span>
          <p>تحليل "AI Analysis" المتخصص متاح حاليًا للصور فقط. هذا التقييم مبني على بيانات المستند وبنيته وأسلوب الكتابة.</p>
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
        <span className={`rounded-full border ${cfg.ring} px-3 py-1 text-xs font-semibold ${cfg.text}`}>
          الثقة: {report.confidence_label}
        </span>
      </div>

      <div className="mt-4 flex items-start gap-2 rounded-lg bg-base-950/40 p-3 text-xs text-slate-400">
        <span className="mt-0.5">ⓘ</span>
        <p>هذه النتيجة احتمال وليست حكمًا قطعيًا. راجع الأدلة للتفاصيل.</p>
      </div>
    </div>
  );
}
