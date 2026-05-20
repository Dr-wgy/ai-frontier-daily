import Link from "next/link";
import { ArrowRight, CalendarDays } from "lucide-react";
import { SECTION_LABELS, SECTION_ORDER, type BriefingSummary } from "@/lib/types";
import { formatChineseDate, weekdayCN } from "@/lib/utils";

interface ArchiveListProps {
  summaries: BriefingSummary[];
}

export function ArchiveList({ summaries }: ArchiveListProps) {
  if (summaries.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-12 text-center text-slate-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400">
        暂无往期早报。
      </div>
    );
  }

  return (
    <ol className="space-y-4">
      {summaries.map((summary) => (
        <li key={summary.date}>
          <Link
            href={`/${summary.date}`}
            className="group block rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:border-blue-300 hover:shadow-md dark:border-slate-800 dark:bg-slate-900 dark:hover:border-blue-700 sm:p-6"
          >
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="flex items-start gap-3">
                <span
                  aria-hidden="true"
                  className="mt-0.5 inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 text-white shadow-sm"
                >
                  <CalendarDays size={18} />
                </span>
                <div>
                  <h2 className="text-base font-semibold text-slate-900 transition-colors group-hover:text-blue-700 dark:text-slate-50 dark:group-hover:text-blue-300 sm:text-lg">
                    {formatChineseDate(summary.date)}
                    <span className="ml-2 text-sm font-normal text-slate-500 dark:text-slate-400">
                      {weekdayCN(summary.date)}
                    </span>
                  </h2>
                  <p className="mt-1 line-clamp-2 text-sm text-slate-600 dark:text-slate-300">
                    {summary.coverage_line}
                  </p>
                </div>
              </div>
              <span className="inline-flex items-center gap-1 rounded-full bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700 transition-colors group-hover:bg-blue-100 dark:bg-blue-950/60 dark:text-blue-300 dark:group-hover:bg-blue-900/60">
                共 {summary.total} 条
                <ArrowRight
                  size={14}
                  className="transition-transform group-hover:translate-x-0.5"
                />
              </span>
            </div>

            <div className="mt-4 flex flex-wrap gap-1.5">
              {SECTION_ORDER.map((key) => {
                const count = summary.counts[key];
                if (!count) return null;
                return (
                  <span
                    key={key}
                    className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2.5 py-0.5 text-xs text-slate-600 dark:bg-slate-800 dark:text-slate-300"
                  >
                    {SECTION_LABELS[key]}
                    <span className="tabular-nums text-slate-500 dark:text-slate-400">
                      {count}
                    </span>
                  </span>
                );
              })}
            </div>

            {summary.data_sources && (
              <p className="mt-3 text-xs text-slate-500 dark:text-slate-400">
                数据源：{summary.data_sources}
              </p>
            )}
          </Link>
        </li>
      ))}
    </ol>
  );
}
