import { cache } from "react";
import { MOCK_BRIEFINGS, MOCK_DATES } from "./mock-data";
import {
  SECTION_LABEL_TO_KEY,
  SECTION_ORDER,
  type Briefing,
  type BriefingSummary,
  type NewsItem,
  type SectionKey,
} from "./types";

export const getAllDates = cache((): string[] => {
  return [...MOCK_DATES];
});

export const getLatestDate = cache((): string | null => {
  const dates = getAllDates();
  return dates[0] ?? null;
});

export const getBriefing = cache((date: string): Briefing | null => {
  return MOCK_BRIEFINGS[date] ?? null;
});

export const getLatestBriefing = cache((): Briefing | null => {
  const date = getLatestDate();
  return date ? getBriefing(date) : null;
});

export function groupBySection(
  items: NewsItem[]
): Record<SectionKey, NewsItem[]> {
  const out: Record<SectionKey, NewsItem[]> = {
    foundation: [],
    core_tech: [],
    agent: [],
    vertical: [],
    industry: [],
  };
  for (const item of items) {
    const key = SECTION_LABEL_TO_KEY[item.main_section];
    if (key) out[key].push(item);
  }
  for (const key of SECTION_ORDER) {
    out[key].sort((a, b) => a.rank - b.rank);
  }
  return out;
}

export const getBriefingSummary = cache(
  (date: string): BriefingSummary | null => {
    const briefing = getBriefing(date);
    if (!briefing) return null;
    const grouped = groupBySection(briefing.items);
    const counts = SECTION_ORDER.reduce((acc, key) => {
      acc[key] = grouped[key].length;
      return acc;
    }, {} as Record<SectionKey, number>);
    return {
      date,
      coverage_line: briefing.blocks.header.coverage_line,
      data_sources: briefing.blocks.header.data_sources,
      total: briefing.items.length,
      counts,
    };
  }
);

export function getAllBriefingSummaries(): BriefingSummary[] {
  return getAllDates()
    .map(getBriefingSummary)
    .filter((s): s is BriefingSummary => s !== null);
}
