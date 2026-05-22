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
import { fetchAllBitableRecords } from "./feishu";

// ── 类型：飞书多维表格 record.fields 的原始形状 ────────────────────
// 字段名需与飞书多维表格中的列名保持一致
interface BitableFields {
  [key: string]: any;
}

// ── 环境变量开关：是否启用飞书数据源 ────────────────────────────────
function isFeishuEnabled(): boolean {
  return (
    !!process.env.FEISHU_APP_ID &&
    !!process.env.FEISHU_APP_SECRET &&
    !!process.env.FEISHU_BITABLE_APP_TOKEN &&
    !!process.env.FEISHU_BITABLE_TABLE_ID
  );
}

// ── 将飞书一条 record 转换为 NewsItem ───────────────────────────────
function mapRecordToNewsItem(record: { fields: BitableFields }): NewsItem {
  const f = record.fields;
  return {
    title:      f["title"]        ?? "",
    url:        f["url"]          ?? "",
    source:     f["source"]       ?? "",
    summary:    f["summary"]      ?? "",
    pub_time:   f["pub_time"]    ?? "",
    main_section: f["main_section"] ?? "",
    sub_section:  f["sub_section"]  ?? "",
    relevance:  Number(f["relevance"])  ?? 0,
    hot_level:  Number(f["hot_level"])  ?? 0,
    rank:       Number(f["rank"])       ?? 0,
    headline:   f["headline"]     ?? "",
    plain_explain: f["plain_explain"] ?? "",
    impacts:    parseArrayField(f["impacts"]),
    digest_for_outline: f["digest_for_outline"] ?? "",
    vertical_tags: parseArrayField(f["vertical_tags"]),
    general_tags:  parseArrayField(f["general_tags"]),
    hot:        f["hot"]          ?? "",
  };
}

/** 飞书多维表格多选/文本字段 → string[] */
function parseArrayField(val: any): string[] {
  if (Array.isArray(val)) return val.map(String);
  if (typeof val === "string") return [val];
  return [];
}

// ── 按日期聚合：将飞书 records 转换为 { [date]: Briefing } ─────────
function buildBriefingsFromRecords(
  records: { fields: BitableFields }[]
): Record<string, Briefing> {
  const map: Record<string, ReturnType<typeof mapRecordToNewsItem>[]> = {};

  for (const rec of records) {
    const item = mapRecordToNewsItem(rec);
    // 从 pub_time 提取日期（格式 YYYY-MM-DD）
    const date = item.pub_time?.slice(0, 10) ?? "unknown";
    if (!map[date]) map[date] = [];
    map[date].push(item);
  }

  const result: Record<string, Briefing> = {};

  for (const [date, items] of Object.entries(map)) {
    // 按 rank 排序
    items.sort((a, b) => a.rank - b.rank);

    const grouped = groupBySection(items);
    const footerTexts: string[] =
      items.flatMap((it) => it.plain_explain ? [it.plain_explain] : []);

    result[date] = {
      blocks: {
        header: {
          date_str:     date,
          coverage_line:
            "AI 基石与算力 · 大模型与核心技术 · AI 智能体与交互 · AI+ 垂直应用 · AI 产业与观察",
          data_sources: "飞书多维表格",
          tags_full:    "#AI早报",
        },
        footer: {
          foundation: grouped.foundation.slice(0, 2).map((it) => it.headline),
          core_tech:  grouped.core_tech .slice(0, 2).map((it) => it.headline),
          agent:      grouped.agent     .slice(0, 2).map((it) => it.headline),
          vertical:   grouped.vertical  .slice(0, 2).map((it) => it.headline),
          industry:   grouped.industry  .slice(0, 2).map((it) => it.headline),
        },
      },
      items,
    };
  }

  return result;
}

// ── 缓存：避免每次请求都调飞书 API ────────────────────────────────────
let _briefingsCache: Record<string, Briefing> | null = null;
let _briefingsCacheTime = 0;
const CACHE_TTL = 5 * 60 * 1000; // 5 分钟

async function getBriefingsMap(): Promise<Record<string, Briefing>> {
  // 使用缓存
  if (_briefingsCache && Date.now() - _briefingsCacheTime < CACHE_TTL) {
    return _briefingsCache;
  }

  if (!isFeishuEnabled()) {
    console.log("[content] 飞书未配置，使用 mock 数据");
    return MOCK_BRIEFINGS;
  }

  try {
    const viewId = process.env.FEISHU_BITABLE_VIEW_ID || undefined;
    const records = await fetchAllBitableRecords({ viewId });
    const briefings = buildBriefingsFromRecords(records);

    if (Object.keys(briefings).length === 0) {
      console.warn("[content] 飞书返回空数据，fallback 到 mock");
      return MOCK_BRIEFINGS;
    }

    _briefingsCache = briefings;
    _briefingsCacheTime = Date.now();
    return briefings;
  } catch (err: any) {
    console.error("[content] 飞书读取失败，fallback 到 mock:", err.message);
    return MOCK_BRIEFINGS;
  }
}

// ── 以下为对外的导出函数（与原有 API 保持一致）─────────────────────

export const getAllDates = cache((): string[] => {
  return Object.keys(MOCK_BRIEFINGS).sort((a, b) => (a < b ? 1 : -1));
});

/** 异步版本：优先读飞书，失败 fallback mock */
export async function getAllDatesAsync(): Promise<string[]> {
  const briefings = await getBriefingsMap();
  return Object.keys(briefings).sort((a, b) => (a < b ? 1 : -1));
}

export const getLatestDate = cache((): string | null => {
  const dates = getAllDates();
  return dates[0] ?? null;
});

export async function getLatestDateAsync(): Promise<string | null> {
  const dates = await getAllDatesAsync();
  return dates[0] ?? null;
}

export const getBriefing = cache((date: string): Briefing | null => {
  return MOCK_BRIEFINGS[date] ?? null;
});

/** 异步版本 */
export async function getBriefingAsync(date: string): Promise<Briefing | null> {
  const briefings = await getBriefingsMap();
  return briefings[date] ?? null;
}

export async function getLatestBriefingAsync(): Promise<Briefing | null> {
  const date = await getLatestDateAsync();
  return date ? getBriefingAsync(date) : null;
}

// ── 分组 / Summary 工具函数（同步版仍用 mock，异步版用飞书）────────

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

export async function getBriefingSummaryAsync(
  date: string
): Promise<BriefingSummary | null> {
  const briefing = await getBriefingAsync(date);
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

export function getAllBriefingSummaries(): BriefingSummary[] {
  return getAllDates()
    .map(getBriefingSummary)
    .filter((s): s is BriefingSummary => s !== null);
}

export async function getAllBriefingSummariesAsync(): Promise<BriefingSummary[]> {
  const dates = await getAllDatesAsync();
  const results = await Promise.all(dates.map(getBriefingSummaryAsync));
  return results.filter((s): s is BriefingSummary => s !== null);
}
