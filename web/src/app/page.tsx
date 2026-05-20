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
      {/* Hero — terminal-style */}
      <section className="relative overflow-hidden border-b border-neutral-800/40">
        <div className="ambient-glow absolute inset-0" aria-hidden="true" />
        <div className="relative mx-auto max-w-5xl px-4 pb-8 pt-10 sm:px-6 sm:pb-10 sm:pt-14">
          {/* Status line */}
          <div className="mb-3 flex items-center gap-2 text-[11px] font-mono text-neutral-600">
            <span className="inline-flex h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>LATEST</span>
            <span className="text-neutral-700">·</span>
            <time>{date}</time>
          </div>

          {/* Title */}
          <h1 className="text-2xl font-bold tracking-tight text-neutral-100 sm:text-3xl lg:text-4xl">
            {formatChineseDate(date)}
            <span className="ml-2.5 text-sm font-normal text-neutral-500 sm:text-base">
              {weekdayCN(date)}
            </span>
          </h1>

          {/* Coverage — terminal block style */}
          <div className="term-block mt-5 overflow-hidden px-4 py-3.5">
            <p className="text-[13px] leading-relaxed text-neutral-400">
              {header.coverage_line}
            </p>
          </div>

          {/* Meta tags row */}
          <div className="mt-4 flex flex-wrap items-center gap-2 text-[11px] font-mono text-neutral-600">
            <span className="rounded-full border border-neutral-800 bg-white/[0.02] px-2.5 py-1">
              {briefing.items.length} articles
            </span>
            {header.data_sources && (
              <span className="rounded-full border border-neutral-800 bg-white/[0.02] px-2.5 py-1">
                {header.data_sources}
              </span>
            )}
            {header.tags_full && (
              <span className="rounded-full border border-amber-400/20 bg-amber-400/[0.06] px-2.5 py-1 text-amber-300/70">
                {header.tags_full}
              </span>
            )}
          </div>
        </div>
      </section>

      <div className="mx-auto max-w-5xl px-4 sm:px-6">
        <SectionNav items={navItems} />

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
                {/* Section header */}
                <header className="flex items-baseline justify-between gap-2 border-b border-neutral-800/30 pb-2.5 mb-5">
                  <h2 className="flex items-center gap-2.5 text-base font-semibold text-neutral-200 sm:text-lg">
                    <span
                      aria-hidden="true"
                      className="inline-block h-1.5 w-1.5 rounded-full bg-amber-400/60"
                    />
                    {SECTION_LABELS[key]}
                  </h2>
                  <span className="text-xs font-mono tabular-nums text-neutral-600">
                    {items.length.toString().padStart(2, "0")}
                  </span>
                </header>

                {/* Cards */}
                <div className="space-y-3">
                  {items.map((item, idx) => (
                    <BriefingCard
                      key={`${item.url}-${idx}`}
                      item={item}
                      index={idx}
                    />
                  ))}
                </div>

                {/* Footer summary */}
                {footerLines.length > 0 && (
                  <aside className="mt-4 term-block overflow-hidden px-4 py-3">
                    <p className="text-[10px] font-mono uppercase tracking-widest text-cyan-400/50 mb-2">
                      // 板块速览
                    </p>
                    <ul className="space-y-1.5">
                      {footerLines.map((line, i) => (
                        <li key={i} className="flex gap-2 text-[12px] leading-relaxed text-neutral-500">
                          <span aria-hidden="true" className="mt-1.5 shrink-0 text-amber-400/30">→</span>
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

        {/* Archive CTA */}
        <div className="border-t border-neutral-800/30 py-10 text-center">
          <Link
            href="/archive"
            className="inline-flex items-center gap-2 rounded-lg border border-neutral-800 bg-white/[0.03] px-5 py-2.5 text-[13px] font-medium text-neutral-300 transition-all hover:border-amber-400/25 hover:bg-amber-4/5 hover:text-amber-300"
          >
            查看往期归档
            <ArrowRight size={14} />
          </Link>
        </div>
      </div>
    </div>
  );
}
