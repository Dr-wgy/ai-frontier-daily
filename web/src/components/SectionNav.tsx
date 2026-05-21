"use client";

import { useEffect, useState } from "react";
import { SECTION_LABELS, SECTION_ORDER, type SectionKey } from "@/lib/types";
import { cn } from "@/lib/utils";

export interface SectionNavItem {
  key: SectionKey | "all";
  label: string;
  count: number;
}

interface SectionNavProps {
  items: SectionNavItem[];
}

export function SectionNav({ items }: SectionNavProps) {
  const [active, setActive] = useState<string>("all");

  useEffect(() => {
    const headings = SECTION_ORDER.map((key) => document.getElementById(key))
      .filter((el): el is HTMLElement => el !== null);
    if (headings.length === 0) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
        if (visible) setActive(visible.target.id);
      },
      { rootMargin: "-30% 0px -60% 0px", threshold: 0 }
    );

    headings.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  const handleClick = (key: string) => {
    setActive(key);
    if (key === "all") {
      window.scrollTo({ top: 0, behavior: "smooth" });
      return;
    }
    const el = document.getElementById(key);
    if (el) {
      const top = el.getBoundingClientRect().top + window.scrollY - 96;
      window.scrollTo({ top, behavior: "smooth" });
    }
  };

  return (
    <div className="sticky top-14 z-30 border-b border-line-subtle bg-surface/95 backdrop-blur-xl">
      <div className="mx-auto flex max-w-5xl items-center gap-1.5 overflow-x-auto px-4 py-2.5 sm:px-6 [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
        {items.map((item) => {
          const isActive = active === item.key;
          const label =
            item.key === "all" ? "全部" : SECTION_LABELS[item.key];
          return (
            <button
              key={item.key}
              type="button"
              onClick={() => handleClick(item.key)}
              className={cn(
                "flex shrink-0 items-center gap-1.5 rounded-md px-3 py-1 text-[12px] font-medium transition-all duration-150",
                isActive
                  ? "bg-amber-500/15 text-amber-700 dark:bg-amber-400/15 dark:text-amber-300"
                  : "text-ink-subtle hover:text-ink-muted hover:bg-ink/[0.04]"
              )}
            >
              {label}
              <span
                className={cn(
                  "rounded px-1 text-[10px] font-mono tabular-nums",
                  isActive
                    ? "bg-amber-500/20 text-amber-700 dark:bg-amber-400/20 dark:text-amber-300"
                    : "bg-ink/[0.04] text-ink-subtle"
                )}
              >
                {item.count}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
