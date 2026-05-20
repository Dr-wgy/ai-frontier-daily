import { ExternalLink } from "lucide-react";
import type { NewsItem } from "@/lib/types";
import { HotTag } from "./HotTag";

interface BriefingCardProps {
  item: NewsItem;
  index: number;
}

function formatPubTime(pubTime: string): string {
  // pub_time looks like "2026-05-21 08:30:00" — keep just the HH:MM
  const match = pubTime.match(/(\d{2}:\d{2})/);
  return match ? match[1] : "";
}

export function BriefingCard({ item, index }: BriefingCardProps) {
  const time = formatPubTime(item.pub_time);
  const tags = [...(item.vertical_tags ?? []), ...(item.general_tags ?? [])];

  return (
    <article className="group relative overflow-hidden rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:border-blue-300 hover:shadow-md dark:border-slate-800 dark:bg-slate-900 dark:hover:border-blue-700 sm:p-6">
      <div className="flex items-start gap-3">
        <span
          aria-hidden="true"
          className="mt-0.5 inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 text-xs font-bold text-white shadow-sm"
        >
          {index + 1}
        </span>
        <div className="min-w-0 flex-1">
          <header className="flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-slate-500 dark:text-slate-400">
            <span className="font-medium text-slate-700 dark:text-slate-300">
              {item.source}
            </span>
            {time && (
              <>
                <span aria-hidden="true">·</span>
                <time className="tabular-nums">{time}</time>
              </>
            )}
            {item.sub_section && (
              <>
                <span aria-hidden="true">·</span>
                <span className="rounded bg-blue-50 px-1.5 py-0.5 text-blue-700 dark:bg-blue-950/60 dark:text-blue-300">
                  {item.sub_section}
                </span>
              </>
            )}
            {item.hot && (
              <span className="ml-auto">
                <HotTag hot={item.hot} level={item.hot_level} />
              </span>
            )}
          </header>

          <h3 className="mt-2 text-base font-semibold leading-snug text-slate-900 transition-colors group-hover:text-blue-700 dark:text-slate-50 dark:group-hover:text-blue-300 sm:text-lg">
            <a
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-baseline gap-1"
            >
              {item.headline || item.title}
              <ExternalLink
                size={14}
                className="relative top-0.5 inline-block shrink-0 text-slate-400 transition-colors group-hover:text-blue-500"
                aria-hidden="true"
              />
            </a>
          </h3>

          {item.plain_explain && (
            <p className="mt-3 rounded-lg border-l-2 border-blue-400 bg-blue-50/60 px-3 py-2 text-sm leading-relaxed text-slate-700 dark:border-blue-500 dark:bg-blue-950/30 dark:text-slate-200">
              <span className="mr-1 font-semibold text-blue-700 dark:text-blue-300">
                解读 ·
              </span>
              {item.plain_explain}
            </p>
          )}

          {item.digest_for_outline && (
            <p className="mt-3 text-sm leading-relaxed text-slate-600 dark:text-slate-300">
              {item.digest_for_outline}
            </p>
          )}

          {item.impacts && item.impacts.length > 0 && (
            <div className="mt-3">
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                影响 / Impacts
              </p>
              <ul className="mt-1.5 space-y-1 text-sm text-slate-700 dark:text-slate-200">
                {item.impacts.map((impact, i) => (
                  <li key={i} className="flex gap-2">
                    <span
                      aria-hidden="true"
                      className="mt-2 inline-block h-1 w-1 shrink-0 rounded-full bg-blue-500"
                    />
                    <span className="leading-relaxed">{impact}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {tags.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-1.5">
              {tags.map((tag, i) => (
                <span
                  key={`${tag}-${i}`}
                  className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600 dark:bg-slate-800 dark:text-slate-300"
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
