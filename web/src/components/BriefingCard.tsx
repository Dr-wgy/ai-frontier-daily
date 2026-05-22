import { ExternalLink } from "lucide-react";
import type { NewsItem } from "@/lib/types";
import { HotTag } from "./HotTag";

interface BriefingCardProps {
  item: NewsItem;
  index: number;
}

function formatPubTime(pubTime: string): string {
  const match = pubTime.match(/(\d{2}:\d{2})/);
  return match ? match[1] : "";
}

export function BriefingCard({ item, index }: BriefingCardProps) {
  const time = formatPubTime(item.daily_report_time);
  const tags = [...(item.vertical_tags ?? []), ...(item.general_tags ?? [])];

  return (
    <article className="card group p-5 sm:p-6">
      <div className="flex items-start gap-3.5">
        {/* Index badge — terminal style */}
        <span
          aria-hidden="true"
          className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-md border border-line bg-surface-subtle text-[11px] font-mono font-medium text-ink-subtle"
        >
          {String(index + 1).padStart(2, "0")}
        </span>

        <div className="min-w-0 flex-1 space-y-3">
          {/* Meta row */}
          <div className="flex flex-wrap items-center gap-x-1.5 gap-y-1 text-[11px] font-mono text-ink-subtle">
            <span className="text-ink-muted">{item.source}</span>
            {time && (
              <>
                <span className="text-ink-faint">·</span>
                <time>{time}</time>
              </>
            )}
            {item.sub_section && (
              <>
                <span className="text-ink-faint">·</span>
                <span className="rounded px-1.5 py-px text-[10px] text-cyan-500/80 border border-cyan-500/20 dark:text-cyan-400/70 dark:border-cyan-400/15">
                  {item.sub_section}
                </span>
              </>
            )}
            {item.hot && (
              <span className="ml-auto">
                <HotTag hot={item.hot} level={item.hot_level} />
              </span>
            )}
          </div>

          {/* Headline */}
          <h3 className="text-[15px] font-semibold leading-snug text-ink transition-colors group-hover:text-amber-600 dark:group-hover:text-amber-300/90 sm:text-base">
            <a
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-baseline gap-1.5"
            >
              {item.headline || item.title}
              <ExternalLink
                size={13}
                className="relative top-0 inline-block shrink-0 text-ink-faint transition-colors group-hover:text-amber-500/60 dark:group-hover:text-amber-400/50"
                aria-hidden="true"
              />
            </a>
          </h3>

          {/* Plain explain — highlighted block */}
          {item.plain_explain && (
            <div className="term-block overflow-hidden px-3.5 py-2.5">
              <p className="flex gap-2 text-[13px] leading-relaxed text-ink-muted">
                <span className="shrink-0 text-amber-500/70 dark:text-amber-400/60 text-[11px] mt-0.5">→</span>
                <span>{item.plain_explain}</span>
              </p>
            </div>
          )}

          {/* Digest */}
          {item.digest_for_outline && (
            <p className="text-[13px] leading-relaxed text-ink-subtle">
              {item.digest_for_outline}
            </p>
          )}

          {/* Impacts */}
          {item.impacts && item.impacts.length > 0 && (
            <div className="space-y-1.5">
              <p className="text-[10px] font-mono uppercase tracking-widest text-ink-subtle">
                Impact
              </p>
              <ul className="space-y-1">
                {item.impacts.map((impact, i) => (
                  <li key={i} className="flex gap-2 text-[13px] text-ink-muted">
                    <span
                      aria-hidden="true"
                      className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-amber-500/60 dark:bg-amber-400/40"
                    />
                    <span className="leading-relaxed">{impact}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Tags */}
          {tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5 pt-1">
              {tags.map((tag, i) => (
                <span
                  key={`${tag}-${i}`}
                  className="rounded-full border border-line bg-surface-subtle px-2 py-px text-[11px] text-ink-subtle"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </article>
  );
}
