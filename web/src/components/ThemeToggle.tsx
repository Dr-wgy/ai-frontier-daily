"use client";

import { useEffect, useRef, useState } from "react";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";

export function ThemeToggle() {
  const [mounted, setMounted] = useState(false);
  const { resolvedTheme, setTheme } = useTheme();
  const buttonRef = useRef<HTMLButtonElement>(null);

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

  const handleClick = () => {
    const root = document.documentElement;
    const btn = buttonRef.current;
    type DocWithVT = Document & {
      startViewTransition?: (cb: () => void) => { ready: Promise<void> };
    };
    const doc = document as DocWithVT;
    const supportsVT =
      typeof doc.startViewTransition === "function" &&
      !window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    if (!supportsVT || !btn) {
      setTheme(next);
      return;
    }

    // Anchor the circular reveal at the button's center, expanding to cover
    // the farthest screen corner.
    const rect = btn.getBoundingClientRect();
    const x = rect.left + rect.width / 2;
    const y = rect.top + rect.height / 2;
    const r = Math.hypot(
      Math.max(x, window.innerWidth - x),
      Math.max(y, window.innerHeight - y),
    );
    root.style.setProperty("--theme-x", `${x}px`);
    root.style.setProperty("--theme-y", `${y}px`);
    root.style.setProperty("--theme-r", `${r}px`);

    doc.startViewTransition!(() => {
      setTheme(next);
    });
  };

  return (
    <button
      ref={buttonRef}
      type="button"
      onClick={handleClick}
      aria-label={`切换主题，当前：${currentLabel}`}
      title={`主题：${currentLabel}（点击切换至${nextLabel}）`}
      className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-line-subtle bg-surface-subtle text-ink-muted transition-colors hover:border-line hover:bg-surface-elevated hover:text-ink"
    >
      <Icon size={15} aria-hidden="true" />
    </button>
  );
}
