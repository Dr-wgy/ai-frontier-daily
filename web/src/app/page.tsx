import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowRight, Sparkles } from "lucide-react";
import { BriefingCard } from "@/components/BriefingCard";
import { SectionNav, type SectionNavItem } from "@/components/SectionNav";
import {
  getLatestBriefing,
  getLatestDate,
  groupBySection,
} from "@/lib/content";
import { SECTION_LABELS, SECTION_ORDER } from "@/lib/types";
import { formatChineseDate, weekdayCN } from "@/lib/utils";

export default function HomePage() {
  const briefing = getLatestBriefing();
  const date = getLatestDate();
  if (!briefing || !date) {
    notFound();
  }

  const grouped = groupBySection(briefing.items);
  const navItems: SectionNavItem[] = [
    { key: "all", label: "全部", count: briefing.items.length },
    ...SECTION_ORDER.map((key) => ({
      key,
      label: SECTION_LABELS[key],
      count: grouped[key].length,
    })),
  ];

  const { header, footer } = briefing.blocks;

  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-200 dark:border-slate-800">
        <div className="bg-hero-glow absolute inset-0" aria-hidden="true" />
        <div className="relative mx-auto max-w-6xl px-4 pb-10 pt-12 sm:px-6 sm:pb-14 sm:pt-16 lg:px-8">
          <div className="flex items-center gap-2 text-sm font-medium text-blue-700 dark:text-blue-300">
            <Sparkles size={16} />
            <span>今日早报</span>
          </div>
          <h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-50 sm:text-4xl lg:text-5xl">
            {formatChineseDate(date)}
            <span className="ml-3 text-base font-normal text-slate-500 dark:text-slate-400 sm:text-lg">
              {weekdayCN(date)}
            </span>
          </h1>
          <p className="mt-4 max-w-3xl text-base leading-relaxed text-slate-600 dark:text-slate-300 sm:text-lg">
            {header.coverage_line}
          </p>
          <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-500 dark:text-slate-400">
            <span className="inline-flex items-center gap-1 rounded-full bg-white/70 px-2.5 py-1 ring-1 ring-slate-200 backdrop-blur dark:bg-slate-900/70 dark:ring-slate-700">
              共 {briefing.items.length} 条
            </span>
            {header.data_sources && (
              <span className="inline-flex items-center gap-1 rounded-full bg-white/70 px-2.5 py-1 ring-1 ring-slate-200 backdrop-blur dark:bg-slate-900/70 dark:ring-slate-700">
                数据源：{header.data_sources}
              </span>
            )}
            {header.tags_full && (
              <span className="inline-flex items-center gap-1 rounded-full bg-white/70 px-2.5 py-1 font-mono text-blue-700 ring-1 ring-blue-200 backdrop-blur dark:bg-slate-900/70 dark:text-blue-300 dark:ring-blue-900">
                {header.tags_full}
              </span>
            )}
          </div>
        </div>
      </section>

      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <SectionNav items={navItems} />

        <div className="space-y-12 py-8 sm:py-10">
          {SECTION_ORDER.map((key) => {
            const items = grouped[key];
            if (items.length === 0) return null;
            const footerLines = footer[key] ?? [];

            return (
              <section
                key={key}
                id={key}
                className="section-anchor scroll-mt-32"
              >
                <header className="flex items-baseline justify-between gap-2 border-b border-slate-200 pb-3 dark:border-slate-800">
                  <h2 className="text-xl font-bold text-slate-900 dark:text-slate-50 sm:text-2xl">
                    <span className="mr-2 inline-block h-2 w-2 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 align-middle" />
                    {SECTION_LABELS[key]}
                  </h2>
                  <span className="text-sm font-medium text-slate-500 dark:text-slate-400">
                    {items.length} 条
                  </span>
                </header>

                <div className="mt-5 grid gap-4">
                  {items.map((item, idx) => (
                    <BriefingCard
                      key={`${item.url}-${idx}`}
                      item={item}
                      index={idx}
                    />
                  ))}
                </div>

                {footerLines.length > 0 && (
                  <aside className="mt-5 rounded-xl border border-blue-100 bg-blue-50/60 p-4 dark:border-blue-900/60 dark:bg-blue-950/30">
                    <p className="text-xs font-semibold uppercase tracking-wider text-blue-700 dark:text-blue-300">
                      板块速览
                    </p>
                    <ul className="mt-2 space-y-1 text-sm text-slate-700 dark:text-slate-200">
                      {footerLines.map((line, i) => (
                        <li key={i} className="flex gap-2">
                          <span
                            aria-hidden="true"
                            className="mt-2 inline-block h-1 w-1 shrink-0 rounded-full bg-blue-500"
                          />
                          <span className="leading-relaxed">{line}</span>
                        </li>
                      ))}
                    </ul>
                  </aside>
                )}
              </section>
            );
          })}
        </div>

        <div className="border-t border-slate-200 py-10 text-center dark:border-slate-800">
          <Link
            href="/archive"
            className="inline-flex items-center gap-1.5 rounded-full bg-blue-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition-all hover:bg-blue-700 hover:shadow-md"
          >
            查看往期归档
            <ArrowRight size={16} />
          </Link>
        </div>
      </div>
    </div>
  );
}
