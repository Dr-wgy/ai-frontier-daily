"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Menu, X } from "lucide-react";
import { cn } from "@/lib/utils";

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
    <header className="sticky top-0 z-40 border-b border-neutral-800/60 bg-[#0a0a0a]/90 backdrop-blur-xl">
      <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-4 sm:px-6">
        <Link
          href="/"
          className="group flex items-center gap-2.5 text-sm font-semibold tracking-tight text-neutral-200"
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
                    ? "bg-white/10 text-amber-300"
                    : "text-neutral-500 hover:text-neutral-200 hover:bg-white/[0.04]"
                )}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          className="inline-flex h-8 w-8 items-center justify-center rounded-md text-neutral-500 transition-colors hover:bg-white/[0.06] hover:text-neutral-300 md:hidden"
          aria-label="切换导航菜单"
          aria-expanded={open}
        >
          {open ? <X size={16} /> : <Menu size={16} />}
        </button>
      </div>

      {open && (
        <div className="border-t border-neutral-800/40 bg-[#0a0a0a]/95 px-4 py-3 backdrop-blur-xl md:hidden">
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
                      : "text-neutral-400 hover:text-neutral-200"
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
