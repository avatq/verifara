"use client";

import { useState, useCallback, useRef } from "react";
import { analyzeFile, ApiRequestError } from "@/lib/api";
import { EvidenceReport } from "@/types/evidence";
import { EvidenceReportView } from "./EvidenceReportView";

type Status = "idle" | "analyzing" | "done" | "error";

export function UploadPanel() {
  const [status, setStatus] = useState<Status>("idle");
  const [report, setReport] = useState<EvidenceReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const runAnalysis = useCallback(async (file: File) => {
    setStatus("analyzing");
    setError(null);
    try {
      const result = await analyzeFile(file);
      setReport(result);
      setStatus("done");
    } catch (err) {
      const message = err instanceof ApiRequestError ? err.message : "تعذّر الاتصال بخادم التحليل";
      setError(message);
      setStatus("error");
    }
  }, []);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    const file = e.dataTransfer.files?.[0];
    if (file) runAnalysis(file);
  };

  const handleSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) runAnalysis(file);
  };

  const reset = () => {
    setStatus("idle");
    setReport(null);
    setError(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  if (status === "done" && report) {
    return (
      <div className="space-y-4">
        <button
          onClick={reset}
          className="text-sm text-accent-violet hover:underline"
        >
          ← تحليل ملف آخر
        </button>
        <EvidenceReportView report={report} />
      </div>
    );
  }

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
      onDragLeave={() => setDragActive(false)}
      onDrop={handleDrop}
      className={`rounded-2xl border-2 border-dashed p-10 text-center transition-colors ${
        dragActive ? "border-accent-violet bg-accent-violet/5" : "border-base-700 bg-base-900"
      }`}
    >
      {status === "analyzing" ? (
        <div className="flex flex-col items-center gap-3 py-6">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-accent-violet border-t-transparent" />
          <p className="text-sm text-slate-400">جارٍ تحليل الملف — استخراج البيانات وبناء تقرير الأدلة…</p>
        </div>
      ) : (
        <>
          <p className="font-display text-lg font-semibold text-slate-100">
            اسحب الملف هنا أو اخترْه
          </p>
          <p className="mt-1 text-sm text-slate-500">
            المدعوم حاليًا: JPG · PNG · WebP · PDF
          </p>
          <button
            onClick={() => inputRef.current?.click()}
            className="mt-5 inline-flex items-center rounded-lg bg-gradient-to-l from-accent-violet to-accent-blue px-5 py-2.5 text-sm font-semibold text-white hover:opacity-90 transition-opacity"
          >
            اختر ملفًا
          </button>
          <input
            ref={inputRef}
            type="file"
            accept=".jpg,.jpeg,.png,.webp,.pdf"
            onChange={handleSelect}
            className="hidden"
          />
        </>
      )}

      {status === "error" && error && (
        <p className="mt-4 text-sm text-status-conflict" role="alert">{error}</p>
      )}
    </div>
  );
}
