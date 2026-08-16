import { UploadPanel } from "@/components/UploadPanel";

export default function HomePage() {
  return (
    <main className="min-h-screen">
      <header className="border-b border-base-700 px-6 py-4">
        <div className="mx-auto flex max-w-4xl items-center gap-2">
          <div className="h-7 w-7 rounded-md bg-gradient-to-br from-accent-violet to-accent-blue" />
          <span className="font-display text-lg font-bold text-slate-100">Verifara</span>
        </div>
      </header>

      <section className="mx-auto max-w-4xl px-6 py-16">
        <h1 className="font-display text-4xl font-extrabold leading-tight text-slate-100">
          Verify the <span className="bg-gradient-to-l from-accent-violet to-accent-blue bg-clip-text text-transparent">evidence.</span>
          <br />
          Know the <span className="bg-gradient-to-l from-accent-violet to-accent-blue bg-clip-text text-transparent">truth.</span>
        </h1>
        <p className="mt-4 max-w-xl text-slate-400">
          ارفع صورة أو مستند، وسنحلّل البيانات الوصفية والبنية التقنية لبناء تقرير أدلة شفاف — بدون أحكام قطعية على الحقيقة.
        </p>

        <div className="mt-10">
          <UploadPanel />
        </div>
      </section>
    </main>
  );
}
