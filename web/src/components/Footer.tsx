import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t border-neutral-800/40 py-10">
      <div className="mx-auto flex max-w-5xl flex-col gap-4 px-4 sm:px-6 md:flex-row md:items-center md:justify-between">
        <div className="text-xs text-neutral-600">
          <p>
            <span className="text-neutral-400">AI 前沿日报</span> · 自动聚合中文 AI 领域要闻
          </p>
        </div>
        <div className="flex gap-x-5 text-xs text-neutral-600">
          <Link href="/" className="transition-colors hover:text-neutral-300">
            今日早报
          </Link>
          <Link href="/archive" className="transition-colors hover:text-neutral-300">
            往期归档
          </Link>
          <a
            href="https://github.com/forsakesoul/ai-frontier-daily"
            target="_blank"
            rel="noopener noreferrer"
            className="transition-colors hover:text-neutral-300"
          >
            GitHub
          </a>
        </div>
      </div>
      <div className="mx-auto mt-6 max-w-5xl px-4 text-[11px] text-neutral-700 sm:px-6">
        © {new Date().getFullYear()} AI Frontier Daily · Built with Next.js
      </div>
    </footer>
  );
}
