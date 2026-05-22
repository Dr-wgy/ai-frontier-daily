const FEISHU_TOKEN_URL =
  'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal';
const FEISHU_API_BASE = 'https://open.feishu.cn/open-apis';

// 内存缓存（开发环境用；生产建议换 Redis / Next.js Cache）
let cachedToken: { token: string; expiresAt: number } | null = null;

// Token 失效错误码列表
const TOKEN_EXPIRED_CODES = [99991663, 10101, 10102]; // token 过期、无效等错误码

async function getFeishuToken(forceRefresh = false): Promise<string> {
  // 如果没有强制刷新且缓存有效，返回缓存的token
  if (!forceRefresh && cachedToken && Date.now() < cachedToken.expiresAt) {
    return cachedToken.token;
  }

  const res = await fetch(FEISHU_TOKEN_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      app_id: process.env.FEISHU_APP_ID,
      app_secret: process.env.FEISHU_APP_SECRET,
    }),
  });

  const data = await res.json();
  if (data.code !== 0) {
    throw new Error(`飞书 token 获取失败 (${data.code}): ${data.msg}`);
  }

  console.log('飞书 token 获取成功', data);

  cachedToken = {
    token: data.tenant_access_token,
    // 提前 5 分钟过期，避免边界问题
    expiresAt: Date.now() + (data.expire - 300) * 1000,
  };

  return cachedToken.token;
}

export async function fetchBitableRecords(options?: {
  viewId?: string;
  pageSize?: number;
  pageToken?: string;
}): Promise<{ items: any[]; hasMore: boolean; pageToken: string }> {
  const appToken = process.env.FEISHU_BITABLE_APP_TOKEN;
  const tableId = process.env.FEISHU_BITABLE_TABLE_ID;

  if (!appToken || !tableId) {
    throw new Error('缺少环境变量 FEISHU_BITABLE_APP_TOKEN / FEISHU_BITABLE_TABLE_ID');
  }

  const params = new URLSearchParams();
  if (options?.viewId) params.set('view_id', options.viewId);
  if (options?.pageSize) params.set('page_size', String(options.pageSize));
  if (options?.pageToken) params.set('page_token', options.pageToken);

  const url = `${FEISHU_API_BASE}/bitable/v1/apps/${appToken}/tables/${tableId}/records?${params.toString()}`;

  const fetchWithRetry = async (forceRefresh = false): Promise<{ items: any[]; hasMore: boolean; pageToken: string }> => {
    // 当 forceRefresh=true 时，强制调用API获取新token，不使用缓存
    const token = await getFeishuToken(forceRefresh);
    const res = await fetch(url, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    const data = await res.json();
    
    // 如果是 token 失效错误，强制刷新token并重试一次
    if (data.code !== 0 && TOKEN_EXPIRED_CODES.includes(data.code) && !forceRefresh) {
      return fetchWithRetry(true); // 强制刷新token并重试请求
    }

    if (data.code !== 0) {
      throw new Error(`飞书多维表格读取失败 (${data.code}): ${data.msg}`);
    }

    return {
      items: data.data.items ?? [],
      hasMore: data.data.has_more ?? false,
      pageToken: data.data.page_token ?? '',
    };
  };

  return fetchWithRetry();
}

/** 一次性拉取所有分页数据 */
export async function fetchAllBitableRecords(options?: {
  viewId?: string;
}): Promise<any[]> {
  const all: any[] = [];
  let pageToken: string | undefined;

  do {
    const result = await fetchBitableRecords({
      ...options,
      pageSize: 500,
      pageToken,
    });
    all.push(...result.items);
    pageToken = result.hasMore ? result.pageToken : undefined;
  } while (pageToken);

  return all;
}
