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
  const time = formatPubTime(item.pub_time);
  const tags = [...(item.vertical_tags ?? []), ...(item.general_tags ?? [])];

  return (
    <article className="card group p-5 sm:p-6">
      <div className="flex items-start gap-3.5">
        {/* Index badge — terminal style */}
        <span
          aria-hidden="true"
          className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-md border border-neutral-700 bg-neutral-800/80 text-[11px] font-mono font-medium text-neutral-500"
        >
          {String(index + 1).padStart(2, "0")}
        </span>

        <div className="min-w-0 flex-1 space-y-3">
          {/* Meta row */}
          <div className="flex flex-wrap items-center gap-x-1.5 gap-y-1 text-[11px] font-mono text-neutral-600">
            <span className="text-neutral-400">{item.source}</span>
            {time && (
              <>
                <span className="text-neutral-700">·</span>
                <time>{time}</time>
              </>
            )}
            {item.sub_section && (
              <>
                <span className="text-neutral-700">·</span>
                <span className="rounded px-1.5 py-px text-[10px] text-cyan-400/70 border border-cyan-400/15">
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
          <h3 className="text-[15px] font-semibold leading-snug text-neutral-100 transition-colors group-hover:text-amber-300/90 sm:text-base">
            <a
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-baseline gap-1.5"
            >
              {item.headline || item.title}
              <ExternalLink
                size={13}
                className="relative top-0 inline-block shrink-0 text-neutral-700 transition-colors group-hover:text-amber-400/50"
                aria-hidden="true"
              />
            </a>
          </h3>

          {/* Plain explain — highlighted block */}
          {item.plain_explain && (
            <div className="term-block overflow-hidden px-3.5 py-2.5">
              <p className="flex gap-2 text-[13px] leading-relaxed text-neutral-400">
                <span className="shrink-0 text-amber-400/60 text-[11px] mt-0.5">→</span>
                <span>{item.plain_explain}</span>
              </p>
            </div>
          )}

          {/* Digest */}
          {item.digest_for_outline && (
            <p className="text-[13px] leading-relaxed text-neutral-500">
              {item.digest_for_outline}
            </p>
          )}

          {/* Impacts */}
          {item.impacts && item.impacts.length > 0 && (
            <div className="space-y-1.5">
              <p className="text-[10px] font-mono uppercase tracking-widest text-neutral-600">
                Impact
              </p>
              <ul className="space-y-1">
                {item.impacts.map((impact, i) => (
                  <li key={i} className="flex gap-2 text-[13px] text-neutral-400">
                    <span
                      aria-hidden="true"
                      className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-amber-400/40"
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
                  className="rounded-full border border-neutral-800 bg-neutral-900/60 px-2 py-px text-[11px] text-neutral-500"
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
