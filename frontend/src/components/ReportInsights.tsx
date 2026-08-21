import { EvidenceReport, EvidenceItem } from "@/types/evidence";

function levelIcon(level: EvidenceItem["level"]) {
  if (level === "good") return "✅";
  if (level === "conflict") return "🔴";
  if (level === "minor") return "🟡";
  if (level === "na") return "⚪";
  return "🔵";
}

export function ReasonChecklist({ report }: { report: EvidenceReport }) {
  return (
    <div className="rounded-xl border border-base-700 bg-base-900 p-4">
      <h3 className="text-sm font-semibold text-slate-200 mb-3">لماذا هذه النتيجة؟</h3>
      <ul className="space-y-2">
        {report.items.map((item) => (
          <li key={item.key} className="flex items-start gap-2 text-sm text-slate-400">
            <span className="mt-0.5">{levelIcon(item.level)}</span>
            <span>
              <span className="text-slate-300">{item.label}</span> — {item.summary}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function FindingsAndLimitations({ report }: { report: EvidenceReport }) {
  const findings = report.items.filter((i) => i.level === "good" || i.level === "conflict" || i.level === "minor");
  const limitations = report.items.filter((i) => i.level === "na" || i.level === "low");

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <div className="rounded-xl border border-status-good/30 bg-status-good/5 p-4">
        <h3 className="text-sm font-semibold text-status-good mb-3">ما وجدناه</h3>
        {findings.length === 0 ? (
          <p className="text-sm text-slate-500">لا توجد نتائج حاسمة بعد.</p>
        ) : (
          <ul className="space-y-2">
            {findings.map((item) => (
              <li key={item.key} className="flex items-start gap-2 text-sm text-slate-300">
                <span className="mt-0.5">{item.level === "conflict" ? "🔴" : "✓"}</span>
                <span>{item.label}: {item.summary}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="rounded-xl border border-status-minor/30 bg-status-minor/5 p-4">
        <h3 className="text-sm font-semibold text-status-minor mb-3">ما لا يمكننا إثباته</h3>
        {limitations.length === 0 ? (
          <p className="text-sm text-slate-500">كل مصادر الأدلة أعطت نتيجة واضحة.</p>
        ) : (
          <ul className="space-y-2">
            {limitations.map((item) => (
              <li key={item.key} className="flex items-start gap-2 text-sm text-slate-300">
                <span className="mt-0.5">⚠</span>
                <span>{item.label}: {item.summary}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export function Recommendations({ report }: { report: EvidenceReport }) {
  const recs: string[] = [];

  const provenance = report.items.find((i) => i.key === "provenance");
  const aiAnalysis = report.items.find((i) => i.key === "ai_analysis");

  recs.push("النتيجة تعتمد على الأدلة المتوفرة حاليًا فقط — راجع كل عنصر أدلة للتفاصيل الكاملة.");

  if (provenance?.level === "na") {
    recs.push("للحصول على موثوقية أعلى، يُفضَّل وجود بيانات C2PA (Content Credentials) في الملف الأصلي.");
  }
  if (aiAnalysis?.level === "na") {
    recs.push("تعذّر تنفيذ تحليل الذكاء الاصطناعي هذه المرة — يمكنك إعادة المحاولة لاحقًا.");
  }
  if (report.verdict === "inconclusive") {
    recs.push("النتيجة غير حاسمة — للمحتوى الحساس (وثائق، عقود)، يُنصح بمراجعة يدوية إضافية.");
  }

  return (
    <div className="rounded-xl border border-base-700 bg-base-900 p-4">
      <h3 className="text-sm font-semibold text-slate-200 mb-3">توصيات</h3>
      <ul className="space-y-1.5">
        {recs.map((r, idx) => (
          <li key={idx} className="text-sm text-slate-400">• {r}</li>
        ))}
      </ul>
    </div>
  );
}
