"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Menu, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { ThemeToggle } from "./ThemeToggle";

const NAV = [
  { href: "/", label: "今日早报" },
  { href: "/archive", label: "往期归档" },
  {
    href: "https://github.com/forsakesoul/ai-frontier-daily",
    label: "GitHub",
    external: true,
  },
];

export function Header() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 border-b border-line-subtle bg-surface/95 backdrop-blur-xl">
      <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-4 sm:px-6">
        <Link
          href="/"
          className="group flex items-center gap-2.5 text-sm font-semibold tracking-tight text-ink"
        >
          {/* Logo dot */}
          <span
            aria-hidden="true"
            className="relative flex h-6 w-6 items-center justify-center rounded-md bg-gradient-to-br from-amber-400 to-orange-500 text-[10px] font-bold text-black transition-transform group-hover:scale-110"
          >
            AI
          </span>
          <span>
            前沿<span className="text-amber-400/80">日报</span>
          </span>
        </Link>

        <div className="flex items-center gap-1">
          <nav className="hidden items-center gap-1 md:flex">
            {NAV.map((item) => {
              const active =
                !item.external &&
                (item.href === "/"
                  ? pathname === "/"
                  : pathname.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  target={item.external ? "_blank" : undefined}
                  rel={item.external ? "noopener noreferrer" : undefined}
                  className={cn(
                    "rounded-md px-3 py-1.5 text-xs font-medium transition-all duration-150",
                    active
                      ? "bg-ink/10 text-amber-300"
                      : "text-ink-subtle hover:text-ink hover:bg-ink/[0.04]"
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <ThemeToggle />

          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            className="inline-flex h-8 w-8 items-center justify-center rounded-md text-ink-subtle transition-colors hover:bg-ink/[0.06] hover:text-ink-muted md:hidden"
            aria-label="切换导航菜单"
            aria-expanded={open}
          >
            {open ? <X size={16} /> : <Menu size={16} />}
          </button>
        </div>
      </div>

      {open && (
        <div className="border-t border-line-subtle bg-surface/95 px-4 py-3 backdrop-blur-xl md:hidden">
          <nav className="flex flex-col gap-0.5">
            {NAV.map((item) => {
              const active =
                !item.external &&
                (item.href === "/"
                  ? pathname === "/"
                  : pathname.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  target={item.external ? "_blank" : undefined}
                  rel={item.external ? "noopener noreferrer" : undefined}
                  onClick={() => setOpen(false)}
                  className={cn(
                    "rounded-md px-3 py-2 text-sm font-medium",
                    active
                      ? "text-amber-300"
                      : "text-ink-muted hover:text-ink"
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
      )}
    </header>
  );
}
