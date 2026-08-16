import { EvidenceReport } from "@/types/evidence";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export class ApiRequestError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function postFile(endpoint: string, file: File): Promise<EvidenceReport> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: "خطأ غير متوقع من الخادم" }));
    throw new ApiRequestError(res.status, body.detail ?? "فشل التحليل");
  }

  return res.json();
}

// نحدد نوع التحليل بناءً على امتداد الملف — يطابق ALLOWED_* في backend/app/core/config.py
const IMAGE_EXT = [".jpg", ".jpeg", ".png", ".webp"];
const DOC_EXT = [".pdf", ".docx", ".txt", ".csv"];

export function inferAnalysisEndpoint(fileName: string): "/analyze/image" | "/analyze/document" | null {
  const ext = fileName.toLowerCase().slice(fileName.lastIndexOf("."));
  if (IMAGE_EXT.includes(ext)) return "/analyze/image";
  if (DOC_EXT.includes(ext)) return "/analyze/document";
  return null;
}

export async function analyzeFile(file: File): Promise<EvidenceReport> {
  const endpoint = inferAnalysisEndpoint(file.name);
  if (!endpoint) {
    throw new ApiRequestError(400, "صيغة الملف غير مدعومة حاليًا. المدعوم الآن: JPG, PNG, WebP, PDF");
  }
  return postFile(endpoint, file);
}
