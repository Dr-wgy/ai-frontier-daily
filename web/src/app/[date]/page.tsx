import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { ArrowLeft, ArrowRight } from "lucide-react";
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
      <section className="relative overflow-hidden border-b border-line-subtle">
        <div className="ambient-glow absolute inset-0" aria-hidden="true" />
        <div className="relative mx-auto max-w-5xl px-4 pb-8 pt-8 sm:px-6 sm:pb-10 sm:pt-12">
          <Link
            href="/archive"
            className="inline-flex items-center gap-1.5 text-[12px] text-ink-subtle transition-colors hover:text-ink-muted"
          >
            <ArrowLeft size={13} />
            返回归档
          </Link>

          <div className="mt-3 flex items-center gap-2 text-[11px] font-mono text-ink-subtle">
            <span className="inline-flex h-1.5 w-1.5 rounded-full bg-cyan-500 dark:bg-cyan-400" />
            <span>DAILY</span>
            <span className="text-ink-faint">·</span>
            <time>{date}</time>
          </div>

          <h1 className="mt-2 text-2xl font-bold tracking-tight text-ink sm:text-3xl">
            {formatChineseDate(date)}
            <span className="ml-2.5 text-sm font-normal text-ink-subtle sm:text-base">
              {weekdayCN(date)}
            </span>
          </h1>

          <div className="term-block mt-5 overflow-hidden px-4 py-3.5">
            <p className="text-[13px] leading-relaxed text-ink-muted">
              {header.coverage_line}
            </p>
          </div>

          <div className="mt-4 flex flex-wrap items-center gap-2 text-[11px] font-mono text-ink-subtle">
            <span className="rounded-full border border-line bg-ink/[0.02] px-2.5 py-1">
              {briefing.items.length} articles
            </span>
            {header.data_sources && (
              <span className="rounded-full border border-line bg-ink/[0.02] px-2.5 py-1">
                {header.data_sources}
              </span>
            )}
            {header.tags_full && (
              <span className="rounded-full border border-amber-500/30 bg-amber-500/[0.08] px-2.5 py-1 text-amber-700 dark:border-amber-400/20 dark:bg-amber-400/[0.06] dark:text-amber-300/70">
                {header.tags_full}
              </span>
            )}
          </div>
        </div>
      </section>

      <SectionNav items={navItems} />

      <div className="mx-auto max-w-5xl px-4 sm:px-6">
        <div className="space-y-10 py-7 sm:py-9">
          {SECTION_ORDER.map((key) => {
            const items = grouped[key];
            if (items.length === 0) return null;
            const footerLines = footer[key] ?? [];

            return (
              <section
                key={key}
                id={key}
                className="section-anchor"
              >
                <header className="flex items-baseline justify-between gap-2 border-b border-line-faint pb-2.5 mb-5">
                  <h2 className="flex items-center gap-2.5 text-base font-semibold text-ink sm:text-lg">
                    <span
                      aria-hidden="true"
                      className="inline-block h-1.5 w-1.5 rounded-full bg-amber-500 dark:bg-amber-400/60"
                    />
                    {SECTION_LABELS[key]}
                  </h2>
                  <span className="text-xs font-mono tabular-nums text-ink-subtle">
                    {items.length.toString().padStart(2, "0")}
                  </span>
                </header>

                <div className="space-y-3">
                  {items.map((item, idx) => (
                    <BriefingCard
                      key={`${item.url}-${idx}`}
                      item={item}
                      index={idx}
                    />
                  ))}
                </div>

                {footerLines.length > 0 && (
                  <aside className="mt-4 term-block overflow-hidden px-4 py-3">
                    <p className="text-[10px] font-mono uppercase tracking-widest text-cyan-600 dark:text-cyan-400/50 mb-2">
                      {"// 板块速览"}
                    </p>
                    <ul className="space-y-1.5">
                      {footerLines.map((line, i) => (
                        <li key={i} className="flex gap-2 text-[12px] leading-relaxed text-ink-subtle">
                          <span aria-hidden="true" className="mt-1.5 shrink-0 text-amber-500/60 dark:text-amber-400/30">→</span>
                          <span>{line}</span>
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
        <nav className="grid gap-3 border-t border-line-faint py-8 sm:grid-cols-2">
          {olderDate ? (
            <Link
              href={`/${olderDate}`}
              className="card group flex items-center gap-3 p-4"
            >
              <ArrowLeft
                size={16}
                className="shrink-0 text-ink-faint transition-colors group-hover:text-amber-500 dark:group-hover:text-amber-400/60"
              />
              <div className="min-w-0">
                <p className="text-[10px] font-mono uppercase tracking-wider text-ink-faint">prev</p>
                <p className="truncate text-[13px] font-medium text-ink-muted group-hover:text-amber-700 dark:group-hover:text-amber-300/90">
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
              className="card group flex items-center justify-end gap-3 p-4 text-right"
            >
              <div className="min-w-0">
                <p className="text-[10px] font-mono uppercase tracking-wider text-ink-faint">next</p>
                <p className="truncate text-[13px] font-medium text-ink-muted group-hover:text-amber-700 dark:group-hover:text-amber-300/90">
                  {formatChineseDate(newerDate)}
                </p>
              </div>
              <ArrowRight
                size={16}
                className="shrink-0 text-ink-faint transition-colors group-hover:text-amber-500 dark:group-hover:text-amber-400/60"
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
