export type SectionKey =
  | "foundation"
  | "core_tech"
  | "agent"
  | "vertical"
  | "industry";

export const SECTION_ORDER: SectionKey[] = [
  "foundation",
  "core_tech",
  "agent",
  "vertical",
  "industry",
];

export const SECTION_LABELS: Record<SectionKey, string> = {
  foundation: "AI 基石与算力",
  core_tech: "大模型与核心技术",
  agent: "AI 智能体与交互",
  vertical: "AI+ 垂直应用",
  industry: "AI 产业与观察",
};

export const SECTION_LABEL_TO_KEY: Record<string, SectionKey> = Object.entries(
  SECTION_LABELS
).reduce((acc, [key, label]) => {
  acc[label] = key as SectionKey;
  return acc;
}, {} as Record<string, SectionKey>);

export interface NewsItem {
  title: string;
  url: string;
  source: string;
  summary: string;
  pub_time: string;
  _feed_url?: string;
  main_section: string;
  sub_section: string;
  relevance: number;
  hot_level: number;
  rank: number;
  headline: string;
  plain_explain: string;
  impacts: string[];
  digest_for_outline: string;
  vertical_tags: string[];
  general_tags: string[];
  hot: string;
}

export interface BriefingHeader {
  date_str: string;
  coverage_line: string;
  data_sources: string;
  tags_full: string;
}

export type FooterBlocks = Partial<Record<SectionKey, string[]>>;

export interface BriefingBlocks {
  header: BriefingHeader;
  footer: FooterBlocks;
}

export interface Briefing {
  items: NewsItem[];
  blocks: BriefingBlocks;
}

export interface BriefingSummary {
  date: string;
  coverage_line: string;
  data_sources: string;
  total: number;
  counts: Record<SectionKey, number>;
}
