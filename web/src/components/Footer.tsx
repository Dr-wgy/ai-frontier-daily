import Link from "next/link";

export function Footer() {
  return (
    <footer className="mt-20 border-t border-slate-200 bg-white/60 py-10 dark:border-slate-800 dark:bg-slate-950/60">
      <div className="mx-auto flex max-w-6xl flex-col gap-6 px-4 sm:px-6 lg:px-8 md:flex-row md:items-center md:justify-between">
        <div className="text-sm text-slate-600 dark:text-slate-400">
          <p className="font-medium text-slate-900 dark:text-slate-100">
            🤖 AI 前沿日报
          </p>
          <p className="mt-1">
            自动聚合中文 AI 领域每日要闻，由 LLM 重写整理，仅供学习参考。
          </p>
        </div>
        <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm">
          <Link
            href="/"
            className="text-slate-600 transition-colors hover:text-blue-600 dark:text-slate-400 dark:hover:text-blue-400"
          >
            今日早报
          </Link>
          <Link
            href="/archive"
            className="text-slate-600 transition-colors hover:text-blue-600 dark:text-slate-400 dark:hover:text-blue-400"
          >
            往期归档
          </Link>
          <a
            href="https://github.com/forsakesoul/ai-frontier-daily"
            target="_blank"
            rel="noopener noreferrer"
            className="text-slate-600 transition-colors hover:text-blue-600 dark:text-slate-400 dark:hover:text-blue-400"
          >
            GitHub
          </a>
        </div>
      </div>
      <div className="mx-auto mt-6 max-w-6xl px-4 text-xs text-slate-400 dark:text-slate-500 sm:px-6 lg:px-8">
        © {new Date().getFullYear()} AI Frontier Daily · Built with Next.js
      </div>
    </footer>
  );
}
