import type { Metadata } from "next";
import "./globals.css";

// ملاحظة: نستخدم Inter و Sora عبر next/font/google في بيئة الإنتاج (VPS بإنترنت طبيعي).
// السطرين التاليين (بدون شبكة خارجية) نشطان مؤقتًا فقط لأن بيئة التطوير الحالية
// هنا مقيّدة الشبكة ولا تصل Google Fonts. عند النشر: استبدلهما بالسطرين المعلّقين تحتهما.
const bodyFont = { variable: "--font-body" };
const displayFont = { variable: "--font-display" };
// import { Inter, Sora } from "next/font/google";
// const bodyFont = Inter({ subsets: ["latin"], variable: "--font-body" });
// const displayFont = Sora({ subsets: ["latin"], weight: ["600", "700", "800"], variable: "--font-display" });

export const metadata: Metadata = {
  title: "Verifara — Digital Media Verification",
  description: "Evidence-based authenticity verification for images, video, audio, and documents.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${bodyFont.variable} ${displayFont.variable}`}>
      <body className="bg-base-950 text-slate-200 antialiased">{children}</body>
    </html>
  );
}
