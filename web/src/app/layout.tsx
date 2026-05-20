import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { ThemeProvider } from "next-themes";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "AI 前沿日报 · AI Frontier Daily",
    template: "%s · AI 前沿日报",
  },
  description:
    "每日聚合中文 AI 领域要闻：大模型、智能体、算力、垂直应用、产业观察，由 LLM 自动整理。",
  keywords: [
    "AI 早报",
    "AI 日报",
    "大模型",
    "智能体",
    "AI 算力",
    "AI 产业",
    "AI Frontier Daily",
  ],
  authors: [{ name: "AI Frontier Daily" }],
  openGraph: {
    title: "AI 前沿日报",
    description: "每日聚合中文 AI 领域要闻，由 LLM 自动整理。",
    type: "website",
    locale: "zh_CN",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="zh-CN"
      className={`${geistSans.variable} ${geistMono.variable} h-full`}
      suppressHydrationWarning
    >
      <body className="flex min-h-full flex-col">
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          <Header />
          <main className="flex-1">{children}</main>
          <Footer />
        </ThemeProvider>
      </body>
    </html>
  );
}
