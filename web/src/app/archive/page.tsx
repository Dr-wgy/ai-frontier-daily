import type { Metadata } from "next";
import { Archive } from "lucide-react";
import { ArchiveList } from "@/components/ArchiveList";
import { getAllBriefingSummaries } from "@/lib/content";

export const metadata: Metadata = {
  title: "往期归档",
  description: "AI 前沿日报往期早报归档列表。",
};

export default function ArchivePage() {
  const summaries = getAllBriefingSummaries();

  return (
    <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6 sm:py-14 lg:px-8">
      <header className="mb-8">
        <div className="flex items-center gap-2 text-sm font-medium text-blue-700 dark:text-blue-300">
          <Archive size={16} />
          <span>往期归档</span>
        </div>
        <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-50 sm:text-4xl">
          所有早报
        </h1>
        <p className="mt-3 text-base text-slate-600 dark:text-slate-300">
          共 {summaries.length} 期，按日期倒序排列。
        </p>
      </header>

      <ArchiveList summaries={summaries} />
    </div>
  );
}
