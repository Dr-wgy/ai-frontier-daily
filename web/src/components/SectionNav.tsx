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
      const top = el.getBoundingClientRect().top + window.scrollY - 80;
      window.scrollTo({ top, behavior: "smooth" });
    }
  };

  return (
    <div className="sticky top-16 z-30 -mx-4 border-b border-slate-200 bg-white/85 px-4 py-3 backdrop-blur-md dark:border-slate-800 dark:bg-slate-950/85 sm:-mx-6 sm:px-6 lg:-mx-8 lg:px-8">
      <div className="mx-auto flex max-w-6xl gap-2 overflow-x-auto pb-1 [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
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
                "flex shrink-0 items-center gap-1.5 rounded-full px-4 py-1.5 text-sm font-medium transition-all",
                isActive
                  ? "bg-blue-600 text-white shadow-sm"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
              )}
            >
              {label}
              <span
                className={cn(
                  "rounded-full px-1.5 text-xs tabular-nums",
                  isActive
                    ? "bg-white/20 text-white"
                    : "bg-white text-slate-500 dark:bg-slate-900 dark:text-slate-400"
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
