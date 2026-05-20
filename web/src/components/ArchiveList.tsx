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
      <div className="term-block p-12 text-center text-neutral-600">
        暂无往期早报。
      </div>
    );
  }

  return (
    <ol className="space-y-3">
      {summaries.map((summary) => (
        <li key={summary.date}>
          <Link
            href={`/${summary.date}`}
            className="card group block p-4 sm:p-5"
          >
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="flex items-start gap-3">
                <span
                  aria-hidden="true"
                  className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-neutral-800 bg-neutral-900/60"
                >
                  <CalendarDays size={15} className="text-neutral-600" />
                </span>
                <div>
                  <h2 className="text-[14px] font-semibold text-neutral-200 transition-colors group-hover:text-amber-300/90 sm:text-base">
                    {formatChineseDate(summary.date)}
                    <span className="ml-2 text-xs font-normal text-neutral-500 sm:text-sm">
                      {weekdayCN(summary.date)}
                    </span>
                  </h2>
                  <p className="mt-1 line-clamp-1 text-[12px] text-neutral-600">
                    {summary.coverage_line}
                  </p>
                </div>
              </div>
              <span className="inline-flex items-center gap-1.5 rounded-full border border-neutral-800 bg-white/[0.02] px-2.5 py-1 text-[11px] font-medium text-neutral-400 transition-colors group-hover:border-amber-400/20 group-hover:text-amber-300/70">
                {summary.total} 条
                <ArrowRight
                  size={12}
                  className="transition-transform group-hover:translate-x-0.5"
                />
              </span>
            </div>

            {/* Section counts */}
            <div className="mt-3.5 flex flex-wrap gap-1.5 pl-12">
              {SECTION_ORDER.map((key) => {
                const count = summary.counts[key];
                if (!count) return null;
                return (
                  <span
                    key={key}
                    className="rounded-full border border-neutral-800/80 bg-neutral-900/40 px-2 py-px text-[10px] text-neutral-600"
                  >
                    {SECTION_LABELS[key]}{" "}
                    <span className="font-mono tabular-nums">{count}</span>
                  </span>
                );
              })}
            </div>

            {summary.data_sources && (
              <p className="mt-2 pl-12 text-[10px] font-mono text-neutral-700">
                src: {summary.data_sources}
              </p>
            )}
          </Link>
        </li>
      ))}
    </ol>
  );
}
