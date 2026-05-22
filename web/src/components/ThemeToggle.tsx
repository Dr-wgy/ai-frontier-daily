"use client";

import { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";

export function ThemeToggle() {
  const [mounted, setMounted] = useState(false);
  const { resolvedTheme, setTheme } = useTheme();

  // eslint-disable-next-line react-hooks/set-state-in-effect -- one-shot mount detection; the trailing render is intentional and bounded
  useEffect(() => setMounted(true), []);

  if (!mounted) {
    return (
      <span
        aria-hidden="true"
        className="inline-flex h-8 w-8 shrink-0"
      />
    );
  }

  const isDark = resolvedTheme === "dark";
  const next = isDark ? "light" : "dark";
  const Icon = isDark ? Moon : Sun;
  const currentLabel = isDark ? "深色" : "浅色";
  const nextLabel = isDark ? "浅色" : "深色";

  return (
    <button
      type="button"
      onClick={() => setTheme(next)}
      aria-label={`切换主题，当前：${currentLabel}`}
      title={`主题：${currentLabel}（点击切换至${nextLabel}）`}
      className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-line-subtle bg-surface-subtle text-ink-muted transition-colors hover:border-line hover:bg-surface-elevated hover:text-ink"
    >
      <Icon size={15} aria-hidden="true" />
    </button>
  );
}
