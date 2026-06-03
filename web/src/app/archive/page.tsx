import type { Metadata } from "next";
import { Archive } from "lucide-react";
import { ArchiveList } from "@/components/ArchiveList";
import { getAllBriefingSummariesAsync } from "@/lib/content";

export const metadata: Metadata = {
  title: "往期归档",
  description: "AI 前沿日报往期早报归档列表。",
};

// Ensure archive page displays latest data (avoid build-time staleness on Vercel).
export const dynamic = "force-dynamic";
export const revalidate = 0;

export default async function ArchivePage() {
  const summaries = await getAllBriefingSummariesAsync();

  return (
    <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6 sm:py-14">
      <header className="mb-8">
        <div className="flex items-center gap-2 text-[11px] font-mono text-ink-subtle">
          <Archive size={13} />
          <span>ARCHIVE</span>
        </div>
        <h1 className="mt-2 text-2xl font-bold tracking-tight text-ink sm:text-3xl">
          往期早报
        </h1>
        <p className="mt-2 text-[13px] text-ink-subtle">
          共 {summaries.length} 期，按日期倒序排列
        </p>
      </header>

      <ArchiveList summaries={summaries} />
    </div>
  );
}
