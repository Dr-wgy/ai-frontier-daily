import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { ArrowLeft, ArrowRight, CalendarDays } from "lucide-react";
import { BriefingCard } from "@/components/BriefingCard";
import { SectionNav, type SectionNavItem } from "@/components/SectionNav";
import {
  getAllDates,
  getBriefing,
  groupBySection,
} from "@/lib/content";
import { SECTION_LABELS, SECTION_ORDER } from "@/lib/types";
import { formatChineseDate, weekdayCN } from "@/lib/utils";

interface DatePageProps {
  params: Promise<{ date: string }>;
}

export function generateStaticParams() {
  return getAllDates().map((date) => ({ date }));
}

export async function generateMetadata({
  params,
}: DatePageProps): Promise<Metadata> {
  const { date } = await params;
  const briefing = getBriefing(date);
  if (!briefing) {
    return { title: "未找到早报" };
  }
  return {
    title: `${formatChineseDate(date)} 早报`,
    description: briefing.blocks.header.coverage_line,
  };
}

export default async function DatePage({ params }: DatePageProps) {
  const { date } = await params;
  const briefing = getBriefing(date);
  if (!briefing) {
    notFound();
  }

  const dates = getAllDates();
  const idx = dates.indexOf(date);
  const newerDate = idx > 0 ? dates[idx - 1] : null;
  const olderDate = idx >= 0 && idx < dates.length - 1 ? dates[idx + 1] : null;

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
        <div className="relative mx-auto max-w-6xl px-4 pb-10 pt-10 sm:px-6 sm:pb-12 sm:pt-14 lg:px-8">
          <Link
            href="/archive"
            className="inline-flex items-center gap-1 text-sm text-slate-600 transition-colors hover:text-blue-700 dark:text-slate-400 dark:hover:text-blue-300"
          >
            <ArrowLeft size={14} />
            返回归档
          </Link>
          <div className="mt-4 flex items-center gap-2 text-sm font-medium text-blue-700 dark:text-blue-300">
            <CalendarDays size={16} />
            <span>每日 AI 早报</span>
          </div>
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-50 sm:text-4xl">
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

        {/* Prev / Next nav */}
        <nav className="grid gap-3 border-t border-slate-200 py-10 dark:border-slate-800 sm:grid-cols-2">
          {olderDate ? (
            <Link
              href={`/${olderDate}`}
              className="group flex items-center gap-3 rounded-2xl border border-slate-200 bg-white p-4 transition-all hover:border-blue-300 hover:shadow-sm dark:border-slate-800 dark:bg-slate-900 dark:hover:border-blue-700"
            >
              <ArrowLeft
                size={18}
                className="shrink-0 text-slate-400 transition-colors group-hover:text-blue-600 dark:group-hover:text-blue-400"
              />
              <div className="min-w-0">
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  上一期
                </p>
                <p className="truncate text-sm font-medium text-slate-900 group-hover:text-blue-700 dark:text-slate-100 dark:group-hover:text-blue-300">
                  {formatChineseDate(olderDate)}
                </p>
              </div>
            </Link>
          ) : (
            <span />
          )}
          {newerDate ? (
            <Link
              href={`/${newerDate}`}
              className="group flex items-center justify-end gap-3 rounded-2xl border border-slate-200 bg-white p-4 text-right transition-all hover:border-blue-300 hover:shadow-sm dark:border-slate-800 dark:bg-slate-900 dark:hover:border-blue-700"
            >
              <div className="min-w-0">
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  下一期
                </p>
                <p className="truncate text-sm font-medium text-slate-900 group-hover:text-blue-700 dark:text-slate-100 dark:group-hover:text-blue-300">
                  {formatChineseDate(newerDate)}
                </p>
              </div>
              <ArrowRight
                size={18}
                className="shrink-0 text-slate-400 transition-colors group-hover:text-blue-600 dark:group-hover:text-blue-400"
              />
            </Link>
          ) : (
            <span />
          )}
        </nav>
      </div>
    </div>
  );
}
