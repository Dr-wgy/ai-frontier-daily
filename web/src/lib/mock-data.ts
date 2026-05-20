import type { Briefing } from "./types";

const briefing_2026_05_21: Briefing = {
  blocks: {
    header: {
      date_str: "2026-05-21",
      coverage_line:
        "AI 基石与算力 · 大模型与核心技术 · AI 智能体与交互 · AI+ 垂直应用 · AI 产业与观察",
      data_sources: "36氪 · 雷锋网 · 机器之心 · 量子位 · InfoQ · 钛媒体",
      tags_full: "#AI早报 #大模型 #智能体 #算力 #投融资",
    },
    footer: {
      foundation: [
        "英伟达发布新一代 Blackwell Ultra GPU，单卡 FP4 算力突破 30 PFLOPS。",
        "国内首座 100 EFLOPS 智算中心在合肥落地。",
      ],
      core_tech: [
        "DeepSeek 开源 V4 模型，长上下文窗口扩展至 256 万 tokens。",
        "谷歌 Gemini 3 Pro 在 SWE-Bench 上首次突破 80% 准确率。",
      ],
      agent: [
        "Anthropic 推出 Claude Agent SDK 2.0，新增浏览器自动化原语。",
        "字节扣子（Coze）上线企业版，支持多智能体协作编排。",
      ],
      vertical: [
        "腾讯医典联合北大医学院发布 AI 辅助诊断大模型 MedicX。",
        "理想汽车 NOA 城市领航全量推送，端到端模型完全替代规则代码。",
      ],
      industry: [
        "OpenAI 完成 400 亿美元新一轮融资，估值 5000 亿美元。",
        "欧盟 AI 法案高风险条款将于 8 月正式生效。",
      ],
    },
  },
  items: [
    {
      title: "英伟达发布 Blackwell Ultra：FP4 算力 30 PFLOPS，HBM4 内存 288GB",
      url: "https://example.com/news/nvidia-blackwell-ultra",
      source: "雷锋网",
      summary:
        "英伟达在 GTC 春季活动中正式揭幕 B300 系列加速卡，FP4 算力较 B200 提升约 50%，单卡 HBM4 显存达 288GB，预计 Q3 量产。",
      pub_time: "2026-05-21 08:30:00",
      main_section: "AI 基石与算力",
      sub_section: "AI 芯片",
      relevance: 0.96,
      hot_level: 0.95,
      rank: 1,
      headline:
        "英伟达 Blackwell Ultra 登场：FP4 算力突破 30 PFLOPS，HBM4 内存达 288GB",
      plain_explain:
        "新卡相当于一台 A100 集群的算力塞进一张卡，AI 训练成本会再降一档，国产替代压力更大。",
      impacts: [
        "训练成本进一步下行，万亿参数模型门槛降至千卡级别",
        "HBM4 量产节奏倒逼三星/海力士产线扩张",
        "国内厂商需在 7nm 工艺受限下寻找架构突破口",
      ],
      digest_for_outline:
        "英伟达发布 Blackwell Ultra 系列加速卡，单卡 FP4 算力 30 PFLOPS，相比 B200 提升 50%。HBM4 显存升至 288GB，互联带宽提升至 1.8TB/s。该产品瞄准下一代万亿参数大模型训练，预计 2026 年第三季度大规模出货。配套的 NVL576 机柜可提供约 17 EFLOPS 算力。",
      vertical_tags: ["AI 芯片"],
      general_tags: ["新品发布", "硬件"],
      hot: "🔥🔥🔥",
    },
    {
      title: "合肥智算中心二期投运，规划总算力达 100 EFLOPS",
      url: "https://example.com/news/hefei-aidc",
      source: "InfoQ",
      summary:
        "中科曙光联合安徽省政府在合肥滨湖科学城建设的智算中心二期完成验收，新增 50 EFLOPS 算力，已与超过 30 家大模型企业签订合作协议。",
      pub_time: "2026-05-21 09:15:00",
      main_section: "AI 基石与算力",
      sub_section: "算力中心",
      relevance: 0.78,
      hot_level: 0.7,
      rank: 2,
      headline: "合肥智算中心二期投运，总规划算力突破 100 EFLOPS",
      plain_explain:
        "国内一线智算中心持续扩容，给国产大模型公司提供了相对充足的训练资源池。",
      impacts: [
        "降低长三角地区大模型企业的算力获取门槛",
        "国产 GPU 部署比例首次超过 50%",
      ],
      digest_for_outline:
        "合肥智算中心二期通过验收，部署超过 1 万张国产加速卡，整体算力达 100 EFLOPS（FP16）。中心采用液冷方案，PUE 控制在 1.15 以下。",
      vertical_tags: ["算力中心"],
      general_tags: ["基建", "国产化"],
      hot: "🔥🔥",
    },
    {
      title: "DeepSeek 开源 V4 模型：256 万上下文，MoE 总参数突破 1.2 万亿",
      url: "https://example.com/news/deepseek-v4",
      source: "机器之心",
      summary:
        "DeepSeek 团队在 GitHub 与 Hugging Face 同步发布 V4 系列模型，提供 16B/120B 激活参数两档选择，原生支持 256 万 tokens 上下文窗口。",
      pub_time: "2026-05-21 07:50:00",
      main_section: "大模型与核心技术",
      sub_section: "开源模型",
      relevance: 0.97,
      hot_level: 0.96,
      rank: 1,
      headline:
        "DeepSeek-V4 开源发布：1.2T MoE 模型 + 256 万上下文，推理性价比再创新高",
      plain_explain:
        "国产开源模型再次刷新性价比纪录，长文本能力第一次真正逼近 Claude 4 / Gemini 3。",
      impacts: [
        "进一步压低开源模型推理成本，挤压闭源 API 利润空间",
        "国内 RAG 与代码 Agent 项目可显著降低对上下文截断的依赖",
        "推动 vLLM / SGLang 等推理框架升级 KV cache 管理",
      ],
      digest_for_outline:
        "DeepSeek-V4 采用 MoE 架构，总参 1.2T、激活 16B/120B，原生 256K 上下文并通过 YaRN 扩展到 256 万。在 MMLU-Pro、SWE-Bench、LongBench 等基准上达到或超过 GPT-5、Claude 4.5 水平。同步开源训练数据配方与强化学习管线。",
      vertical_tags: ["开源模型"],
      general_tags: ["大模型", "开源"],
      hot: "🔥🔥🔥",
    },
    {
      title: "Gemini 3 Pro 在 SWE-Bench Verified 上达到 81.2% 准确率",
      url: "https://example.com/news/gemini-3-pro",
      source: "量子位",
      summary:
        "谷歌 DeepMind 公布 Gemini 3 Pro 在权威代码评测 SWE-Bench Verified 上得分 81.2%，刷新榜单纪录，并将 IO 大会演示纳入 Code Assist 产品。",
      pub_time: "2026-05-21 10:20:00",
      main_section: "大模型与核心技术",
      sub_section: "闭源模型",
      relevance: 0.9,
      hot_level: 0.88,
      rank: 2,
      headline:
        "Gemini 3 Pro 在 SWE-Bench Verified 上取得 81.2% 创纪录成绩",
      plain_explain:
        "代码能力是当下大模型最直接的生产力指标，Gemini 3 这一跃，反过来会逼 OpenAI 加速 GPT-6 节奏。",
      impacts: [
        "代码类 Agent 的基线门槛被显著抬高",
        "谷歌云 Code Assist 的付费转化率有望提升",
      ],
      digest_for_outline:
        "Gemini 3 Pro 在 SWE-Bench Verified 上的 pass@1 成绩达到 81.2%，相比上一代提升 18 个百分点。模型在工具使用、长链路规划上引入 reinforcement self-improvement 训练阶段。",
      vertical_tags: ["闭源模型"],
      general_tags: ["大模型", "代码"],
      hot: "🔥🔥",
    },
    {
      title: "Anthropic Claude Agent SDK 2.0 发布：浏览器原语 + 长任务记忆",
      url: "https://example.com/news/claude-agent-sdk-2",
      source: "InfoQ",
      summary:
        "Anthropic 在开发者大会发布 Claude Agent SDK 2.0，新增 browser、screen、file_system 三类原生工具，并内置可持久化长任务记忆。",
      pub_time: "2026-05-21 11:00:00",
      main_section: "AI 智能体与交互",
      sub_section: "Agent 框架",
      relevance: 0.93,
      hot_level: 0.9,
      rank: 1,
      headline:
        "Claude Agent SDK 2.0 发布：浏览器/屏幕/文件原语 + 持久化记忆",
      plain_explain:
        "Anthropic 想把 LangChain、AutoGen 这些胶水层吃掉，开发者写 Agent 会越来越像写脚本。",
      impacts: [
        "降低构建 Computer Use Agent 的工程复杂度",
        "对 LangChain、CrewAI 等开源框架形成压力",
        "推动企业重新评估 Agent 平台选型",
      ],
      digest_for_outline:
        "Claude Agent SDK 2.0 引入 browser/screen/file_system 三类原生工具，统一调用接口；并提供基于向量与摘要的 long-running memory 模块，可在多轮会话间持久化。SDK 同时整合了批处理任务、子代理（subagent）调度与可观测性 hooks。",
      vertical_tags: ["Agent 框架"],
      general_tags: ["智能体", "开发工具"],
      hot: "🔥🔥🔥",
    },
    {
      title: "字节扣子推出企业版：支持多智能体协作与私有部署",
      url: "https://example.com/news/coze-enterprise",
      source: "36氪",
      summary:
        "字节跳动旗下扣子（Coze）平台推出企业版，原生支持多智能体编排（Multi-Agent）、私有化部署及与飞书的深度集成。",
      pub_time: "2026-05-21 09:40:00",
      main_section: "AI 智能体与交互",
      sub_section: "智能体平台",
      relevance: 0.82,
      hot_level: 0.78,
      rank: 2,
      headline:
        "字节扣子企业版上线，主打多智能体协作 + 私有部署 + 飞书集成",
      plain_explain:
        "国内大厂 Agent 平台从 To C 一脚迈向 To B，企业 IT 部门要开始认真选型。",
      impacts: [
        "拉开国内多智能体平台商业化竞争",
        "飞书生态进一步绑定企业知识资产",
      ],
      digest_for_outline:
        "扣子企业版支持图形化编排 Multi-Agent 流程，提供与飞书文档/审批/通讯录的预制连接器，并支持基于 BytePlus 的私有部署方案。同时上线效果监控、AB 测试与权限分级模块。",
      vertical_tags: ["智能体平台"],
      general_tags: ["智能体", "To B"],
      hot: "🔥🔥",
    },
    {
      title: "腾讯医典 + 北大医学院发布 MedicX 医疗大模型",
      url: "https://example.com/news/medicx",
      source: "钛媒体",
      summary:
        "腾讯医典联合北大医学院发布 MedicX 医疗诊断大模型，覆盖 32 个临床科室，在多病种鉴别诊断准确率上超过主治医师平均水平。",
      pub_time: "2026-05-21 10:50:00",
      main_section: "AI+ 垂直应用",
      sub_section: "医疗",
      relevance: 0.85,
      hot_level: 0.8,
      rank: 1,
      headline:
        "腾讯医典联合北大医学院发布 MedicX 医疗大模型，覆盖 32 科室",
      plain_explain:
        "医疗大模型从科普问答迈向辅助诊断，监管态度会成为下一步关键变量。",
      impacts: [
        "国内医疗 AI 进入临床决策辅助阶段",
        "基层医院诊断质量有望显著改善",
        "卫健委对 AI 辅助诊断的审批路径将被加速讨论",
      ],
      digest_for_outline:
        "MedicX 基于 DeepSeek-V4 训练，融合 1.3 亿份真实病例与 200 万条医学文献，覆盖 32 个临床科室。在内部 5000 例多病种鉴别测试中诊断准确率达 87%，高于主治医师平均的 82%。",
      vertical_tags: ["医疗"],
      general_tags: ["大模型", "行业应用"],
      hot: "🔥🔥",
    },
    {
      title: "理想 AD Max V5 全量推送：端到端模型替代全部规则代码",
      url: "https://example.com/news/lixiang-ad-max",
      source: "36氪",
      summary:
        "理想汽车官方宣布 AD Max V5 城市领航 NOA 全量推送，底层架构完全转向端到端神经网络，删除超过 30 万行规则代码。",
      pub_time: "2026-05-21 08:00:00",
      main_section: "AI+ 垂直应用",
      sub_section: "智能驾驶",
      relevance: 0.88,
      hot_level: 0.85,
      rank: 2,
      headline:
        "理想 AD Max V5 全量推送：端到端模型完全取代规则代码",
      plain_explain:
        "国内辅助驾驶从分模块拼装，正式进入端到端时代，事故归因体系也要随之重写。",
      impacts: [
        "国内主流车企端到端落地进度对标特斯拉 FSD V13",
        "供应链对超高带宽车载芯片需求上升",
        "智能驾驶法规与责任认定迎来新挑战",
      ],
      digest_for_outline:
        "AD Max V5 采用 VLM + 世界模型双系统，硬件平台为 Thor + Orin 双 SoC，端到端模型每 2 周完成一次 OTA 更新。理想披露城市 NOA 月活渗透率已达 76%，平均接管里程突破 240 公里。",
      vertical_tags: ["智能驾驶"],
      general_tags: ["自动驾驶", "行业应用"],
      hot: "🔥🔥🔥",
    },
    {
      title: "OpenAI 完成 400 亿美元新一轮融资，估值升至 5000 亿美元",
      url: "https://example.com/news/openai-funding",
      source: "雷锋网",
      summary:
        "OpenAI 完成由软银、微软、Thrive 等领投的 400 亿美元新一轮融资，公司投后估值达到 5000 亿美元，募资将用于数据中心建设。",
      pub_time: "2026-05-21 06:30:00",
      main_section: "AI 产业与观察",
      sub_section: "投融资",
      relevance: 0.94,
      hot_level: 0.92,
      rank: 1,
      headline:
        "OpenAI 完成 400 亿美元融资，估值飙升至 5000 亿美元",
      plain_explain:
        "钱继续往头部 AI 公司涌，资本市场默认 OpenAI 是这一代基础设施级选手。",
      impacts: [
        "全球 AI 资本进一步集中到头部 3-4 家",
        "支撑 Stargate 数据中心计划资金到位",
        "推高估值锚点，二级市场 AI 概念延续高估值",
      ],
      digest_for_outline:
        "OpenAI 完成 400 亿美元 H 轮融资，软银领投 100 亿美元，微软追加 80 亿美元。本轮资金主要投入 Stargate 数据中心项目，规划在 2028 年前部署 10GW 级算力。公司同时披露 ARR 已达 320 亿美元。",
      vertical_tags: ["投融资"],
      general_tags: ["投融资", "OpenAI"],
      hot: "🔥🔥🔥",
    },
    {
      title: "欧盟 AI 法案高风险条款将于 8 月正式生效",
      url: "https://example.com/news/eu-ai-act",
      source: "InfoQ",
      summary:
        "欧盟委员会确认 AI 法案高风险类别条款将于 2026 年 8 月 2 日起强制执行，涉及合规义务包括数据治理、风险管理、人类监督等。",
      pub_time: "2026-05-21 11:30:00",
      main_section: "AI 产业与观察",
      sub_section: "政策监管",
      relevance: 0.83,
      hot_level: 0.75,
      rank: 2,
      headline:
        "欧盟 AI 法案高风险条款 2026/8 生效，违规罚款最高 3500 万欧元",
      plain_explain:
        "出海欧洲的 AI 产品要立刻盘点高风险用途，准备一套合规材料并不便宜。",
      impacts: [
        "出海企业合规成本上升",
        "通用大模型供应商需提供详尽技术档案",
      ],
      digest_for_outline:
        "欧盟 AI 法案 (EU AI Act) 高风险条款将于 2026 年 8 月 2 日生效。涉及医疗、金融、招聘、关键基础设施等场景的 AI 系统将面临严格合规义务，包括数据治理、风险管理、人类监督、透明度等。违规最高可处全球年营业额 7% 或 3500 万欧元罚款。",
      vertical_tags: ["政策监管"],
      general_tags: ["政策", "合规"],
      hot: "🔥🔥",
    },
  ],
};

const briefing_2026_05_20: Briefing = {
  blocks: {
    header: {
      date_str: "2026-05-20",
      coverage_line:
        "AI 基石与算力 · 大模型与核心技术 · AI 智能体与交互 · AI+ 垂直应用 · AI 产业与观察",
      data_sources: "36氪 · 机器之心 · 量子位 · 雷锋网 · 钛媒体",
      tags_full: "#AI早报 #大模型 #智能体",
    },
    footer: {
      foundation: [
        "华为昇腾 920 流片成功，FP16 单卡算力对标 H200。",
      ],
      core_tech: [
        "阿里通义千问 Qwen4 发布，激活 32B 参数对齐 Claude 4.5。",
        "Mistral 推出 Mixtral-Next，原生支持工具调用强化学习。",
      ],
      agent: [
        "OpenAI Operator 升级到 v2，可独立完成 50 步以上 Web 任务。",
      ],
      vertical: [
        "京东推出 AI 客服全栈方案，承接淘宝/拼多多商家迁移需求。",
        "波士顿动力 Atlas 工业版部署到现代汽车装配线。",
      ],
      industry: [
        "微软重组 AI 部门，Mustafa Suleyman 出任消费 AI CEO。",
      ],
    },
  },
  items: [
    {
      title: "华为昇腾 920 流片成功：FP16 算力对标 H200，年底量产",
      url: "https://example.com/news/ascend-920",
      source: "雷锋网",
      summary:
        "华为海思在内部技术大会确认昇腾 920 流片成功，FP16 算力 1.8 PFLOPS，HBM3e 显存 192GB，目标 2026 年底量产。",
      pub_time: "2026-05-20 09:00:00",
      main_section: "AI 基石与算力",
      sub_section: "AI 芯片",
      relevance: 0.94,
      hot_level: 0.93,
      rank: 1,
      headline:
        "昇腾 920 流片成功：FP16 算力 1.8 PFLOPS，对标 H200",
      plain_explain:
        "国产卡再补一发硬实力，国内大模型公司多了一个真正可商用的算力选项。",
      impacts: [
        "缓解国内大模型训练对英伟达的依赖",
        "国产 HBM 与先进封装供应链需求加速",
      ],
      digest_for_outline:
        "昇腾 920 采用自研达芬奇 3.0 架构，FP16 算力达 1.8 PFLOPS，配备 192GB HBM3e 显存，互联带宽 1.2TB/s。预计 2026 年底量产，2027 年规模出货，主要面向运营商、互联网大厂与国家级智算项目。",
      vertical_tags: ["AI 芯片"],
      general_tags: ["国产化", "硬件"],
      hot: "🔥🔥🔥",
    },
    {
      title: "阿里通义千问 Qwen4 发布：MoE 激活 32B，对齐 Claude 4.5",
      url: "https://example.com/news/qwen4",
      source: "机器之心",
      summary:
        "阿里通义千问团队发布 Qwen4 系列，包含 4B/32B 激活两档以及视觉、代码、Math 三个领域专用版本，整体能力对齐 Claude 4.5。",
      pub_time: "2026-05-20 10:00:00",
      main_section: "大模型与核心技术",
      sub_section: "开源模型",
      relevance: 0.92,
      hot_level: 0.9,
      rank: 1,
      headline:
        "通义千问 Qwen4 发布：MoE 激活 32B，对齐 Claude 4.5 水准",
      plain_explain:
        "国产开源模型集体爬到第一梯队尾部，海外开发者也开始日常用国内模型。",
      impacts: [
        "Hugging Face 国产模型下载榜继续被刷新",
        "推动国内 RAG、Agent 应用进一步降低 LLM 成本",
      ],
      digest_for_outline:
        "Qwen4 系列模型采用稀疏 MoE 架构，总参数 240B / 激活 32B，在 MMLU-Pro、AIME、SWE-Bench 等评测上对齐 Claude 4.5。同时开源 Qwen4-VL、Qwen4-Coder、Qwen4-Math 三个垂直版本，并提供 API 与 PAI 平台一键部署。",
      vertical_tags: ["开源模型"],
      general_tags: ["大模型", "开源"],
      hot: "🔥🔥🔥",
    },
    {
      title: "Mistral 发布 Mixtral-Next：原生强化学习训练工具调用",
      url: "https://example.com/news/mixtral-next",
      source: "InfoQ",
      summary:
        "Mistral AI 发布 Mixtral-Next 系列，140B 总参 / 23B 激活，首次将工具调用与多轮交互纳入预训练后期 RLHF 流程。",
      pub_time: "2026-05-20 11:20:00",
      main_section: "大模型与核心技术",
      sub_section: "开源模型",
      relevance: 0.78,
      hot_level: 0.72,
      rank: 2,
      headline:
        "Mistral 推出 Mixtral-Next，原生强化学习训练工具调用能力",
      plain_explain:
        "工具调用从 prompt 工程变成模型自带技能，对开源 Agent 生态是关键拼图。",
      impacts: [
        "Mistral 在欧洲市场继续巩固开源旗手地位",
        "Agent 应用对 prompt 工程师的依赖进一步降低",
      ],
      digest_for_outline:
        "Mixtral-Next 总参 140B、激活 23B，对工具调用、ReAct 等多步行为进行原生强化学习训练。在 BFCL v3、AgentBench 等评测上显著超越同尺寸开源模型。Apache 2.0 协议开源。",
      vertical_tags: ["开源模型"],
      general_tags: ["大模型", "智能体"],
      hot: "🔥🔥",
    },
    {
      title: "OpenAI Operator v2 升级：可独立完成 50+ 步 Web 任务",
      url: "https://example.com/news/operator-v2",
      source: "量子位",
      summary:
        "OpenAI 发布 Operator v2，浏览器智能体能够独立完成跨网站、跨账号的复杂任务，平均成功率提升至 78%。",
      pub_time: "2026-05-20 08:30:00",
      main_section: "AI 智能体与交互",
      sub_section: "浏览器 Agent",
      relevance: 0.86,
      hot_level: 0.84,
      rank: 1,
      headline:
        "OpenAI Operator v2 升级：50+ 步 Web 任务成功率达 78%",
      plain_explain:
        "浏览器 Agent 从“能用”迈向“好用”，未来一年大量重复性工作有被替代的风险。",
      impacts: [
        "重新定义 SaaS 工具的接入与计费方式",
        "网站反爬虫策略迎来新一轮对抗",
      ],
      digest_for_outline:
        "Operator v2 基于 GPT-5o 推理引擎与定制 Computer Use 模型，可在多个网站之间连续完成预订、对账、跨平台搬运等任务。任务计划由内置 planner 自动拆解，并在失败时触发反思与重试。",
      vertical_tags: ["浏览器 Agent"],
      general_tags: ["智能体", "OpenAI"],
      hot: "🔥🔥",
    },
    {
      title: "京东推出 AI 客服全栈方案，承接电商商家迁移需求",
      url: "https://example.com/news/jd-ai-cs",
      source: "36氪",
      summary:
        "京东云推出面向中小商家的 AI 客服全栈解决方案，整合大模型、知识库、声音克隆、工单系统，单坐席月费 199 元起。",
      pub_time: "2026-05-20 09:50:00",
      main_section: "AI+ 垂直应用",
      sub_section: "电商",
      relevance: 0.74,
      hot_level: 0.68,
      rank: 1,
      headline:
        "京东 AI 客服全栈方案上线，单坐席月费 199 元起",
      plain_explain:
        "AI 客服从大企业专属变成开箱即用 SaaS，电商客服外包行业模式被加速重构。",
      impacts: [
        "中小商家 7x24 服务能力显著提升",
        "传统人工客服外包行业承压",
      ],
      digest_for_outline:
        "方案集成京东自研客服大模型 JDAI-CS、知识库管理、声纹克隆、工单系统与质检模块。可与淘宝、拼多多、抖音电商等平台 API 深度集成，平均会话成本降至人工的 1/8。",
      vertical_tags: ["电商"],
      general_tags: ["行业应用", "SaaS"],
      hot: "🔥",
    },
    {
      title: "波士顿动力 Atlas 工业版部署到现代汽车装配线",
      url: "https://example.com/news/atlas-hyundai",
      source: "钛媒体",
      summary:
        "波士顿动力宣布全电动版 Atlas 工业型号 ATLAS-W 在现代汽车蔚山工厂完成产线集成，可完成搬运、装配、检测等 30 余类任务。",
      pub_time: "2026-05-20 12:00:00",
      main_section: "AI+ 垂直应用",
      sub_section: "具身智能",
      relevance: 0.84,
      hot_level: 0.83,
      rank: 2,
      headline:
        "波士顿动力 Atlas 工业版进入现代汽车装配线，可执行 30+ 类任务",
      plain_explain:
        "人形机器人从展示视频走向真实产线，全球具身智能竞赛进入交付期。",
      impacts: [
        "海外汽车厂率先验证人形机器人 ROI",
        "国内具身智能公司面临商业化时间窗压力",
      ],
      digest_for_outline:
        "ATLAS-W 采用电动驱动方案，单台续航 6 小时。在蔚山工厂部署 12 台，覆盖底盘装配、零部件转运与质检三大场景。系统由 Atlas Cortex 大模型驱动，可通过自然语言下发任务并实时调整动作策略。",
      vertical_tags: ["具身智能"],
      general_tags: ["机器人", "行业应用"],
      hot: "🔥🔥",
    },
    {
      title: "微软重组 AI 部门：Mustafa Suleyman 出任消费 AI CEO",
      url: "https://example.com/news/msft-ai-reorg",
      source: "InfoQ",
      summary:
        "微软宣布重组 AI 业务，Mustafa Suleyman 出任新成立的“Microsoft Consumer AI”CEO，负责整合 Copilot、Bing、Edge AI 等业务。",
      pub_time: "2026-05-20 07:30:00",
      main_section: "AI 产业与观察",
      sub_section: "组织变动",
      relevance: 0.81,
      hot_level: 0.78,
      rank: 1,
      headline:
        "微软成立 Consumer AI 事业群，Suleyman 出任 CEO 统筹 Copilot 产品线",
      plain_explain:
        "微软终于把 AI to C 战略拢到一个老板手里，未来 Copilot 在系统层的整合会更激进。",
      impacts: [
        "微软 to C AI 产品迭代速度有望加快",
        "OpenAI 与微软关系再次微调",
      ],
      digest_for_outline:
        "微软将 Copilot、Bing、Edge AI、MSN AI 等业务整合为 Microsoft Consumer AI 事业群，由 Suleyman 直接向 CEO Satya Nadella 汇报。同时 Azure AI 与企业 Copilot 仍由 Scott Guthrie 负责。",
      vertical_tags: ["组织变动"],
      general_tags: ["微软", "组织"],
      hot: "🔥🔥",
    },
    {
      title: "AI 投融资周报：本周国内披露 9 起，总额约 47 亿元",
      url: "https://example.com/news/funding-weekly",
      source: "36氪",
      summary:
        "本周国内 AI 领域披露 9 起融资，覆盖大模型、Agent、机器人与垂直应用，总融资额约 47 亿元人民币。",
      pub_time: "2026-05-20 17:00:00",
      main_section: "AI 产业与观察",
      sub_section: "投融资",
      relevance: 0.7,
      hot_level: 0.62,
      rank: 2,
      headline:
        "本周国内 AI 融资周报：9 起、47 亿元，机器人方向最热",
      plain_explain:
        "钱继续往机器人方向走，大模型公司估值进入分化期。",
      impacts: [
        "具身智能成为机构 2026 上半年重点配置方向",
        "中腰部大模型公司融资难度上升",
      ],
      digest_for_outline:
        "本周国内披露 9 起 AI 融资。其中机器人方向 4 起（合计 28 亿元），通用大模型 2 起，Agent 平台 2 起，垂直 AI 1 起。最大单笔为某具身智能创业公司 B 轮 12 亿元。",
      vertical_tags: ["投融资"],
      general_tags: ["投融资", "周报"],
      hot: "🔥",
    },
  ],
};

const briefing_2026_05_19: Briefing = {
  blocks: {
    header: {
      date_str: "2026-05-19",
      coverage_line:
        "AI 基石与算力 · 大模型与核心技术 · AI 智能体与交互 · AI+ 垂直应用 · AI 产业与观察",
      data_sources: "36氪 · 雷锋网 · 量子位 · 机器之心",
      tags_full: "#AI早报 #大模型 #算力",
    },
    footer: {
      foundation: [
        "SK 海力士宣布 HBM4 良率突破 70%，三季度量产。",
      ],
      core_tech: [
        "Anthropic 发布 Claude 4.7 1M 上下文版本，强化文档分析。",
      ],
      agent: [
        "智谱 AutoGLM 升级到 v3，原生支持 Android 应用代理。",
      ],
      vertical: [
        "Adobe Firefly 5 集成端到端视频生成，时长可达 60 秒。",
      ],
      industry: [
        "国内首份《大模型安全治理白皮书》发布。",
      ],
    },
  },
  items: [
    {
      title: "SK 海力士 HBM4 良率突破 70%，Q3 进入量产",
      url: "https://example.com/news/sk-hbm4",
      source: "雷锋网",
      summary:
        "SK 海力士在投资者沟通会披露 HBM4 工程样品良率已突破 70%，预计 2026 年第三季度进入大规模量产。",
      pub_time: "2026-05-19 09:10:00",
      main_section: "AI 基石与算力",
      sub_section: "存储",
      relevance: 0.79,
      hot_level: 0.74,
      rank: 1,
      headline:
        "SK 海力士 HBM4 良率突破 70%，Q3 进入大规模量产",
      plain_explain:
        "HBM 一直是 AI 算力扩张的瓶颈，良率破 70 意味着 Blackwell Ultra 这类新卡能按时上量。",
      impacts: [
        "缓解 HBM4 供给紧张，加速新一代 GPU 出货",
        "三星、美光产能压力加大",
      ],
      digest_for_outline:
        "SK 海力士 HBM4 工程样品良率突破 70%，目前以 12-Hi 与 16-Hi 堆叠为主，单颗最大容量 36GB。客户群覆盖英伟达、AMD 与谷歌 TPU 团队。",
      vertical_tags: ["存储"],
      general_tags: ["硬件", "供应链"],
      hot: "🔥🔥",
    },
    {
      title: "Anthropic 推出 Claude 4.7 (1M 上下文) 版本",
      url: "https://example.com/news/claude-4-7-1m",
      source: "机器之心",
      summary:
        "Anthropic 发布 Claude 4.7 1M Context 版本，新增 1M tokens 上下文窗口选项，重点强化长文档分析、代码仓库理解与企业知识检索。",
      pub_time: "2026-05-19 10:20:00",
      main_section: "大模型与核心技术",
      sub_section: "闭源模型",
      relevance: 0.93,
      hot_level: 0.9,
      rank: 1,
      headline:
        "Claude 4.7 推出 1M 上下文版本，主打长文档与全仓代码分析",
      plain_explain:
        "Anthropic 在长上下文上拉到第一梯队，企业知识库类应用迎来真·全量喂入选项。",
      impacts: [
        "企业知识库 RAG 设计被重新评估",
        "代码 Agent 可一次性载入大型仓库",
      ],
      digest_for_outline:
        "Claude 4.7 1M Context 版本支持最大 1,000,000 tokens 上下文窗口，长上下文召回准确率在内部 needle-in-haystack 测试中超过 96%。同时优化推理成本，1M 输入价格相比之前 200K 版本仅上涨约 25%。",
      vertical_tags: ["闭源模型"],
      general_tags: ["大模型", "长上下文"],
      hot: "🔥🔥🔥",
    },
    {
      title: "智谱 AutoGLM v3 升级：原生支持 Android 应用代理",
      url: "https://example.com/news/autoglm-v3",
      source: "量子位",
      summary:
        "智谱发布 AutoGLM v3，新增原生 Android 应用代理能力，可在手机上自动执行点外卖、购票、收发消息等任务。",
      pub_time: "2026-05-19 11:00:00",
      main_section: "AI 智能体与交互",
      sub_section: "手机 Agent",
      relevance: 0.84,
      hot_level: 0.82,
      rank: 1,
      headline:
        "AutoGLM v3 升级：手机 Agent 可代点外卖、订票、回消息",
      plain_explain:
        "国内手机 Agent 比海外更落地一些，因为小程序与超级 App 的边界更清晰。",
      impacts: [
        "国产手机厂商系统级 AI 入口竞争加剧",
        "推动 App 开放更多 Accessibility 与 Intent 接口",
      ],
      digest_for_outline:
        "AutoGLM v3 通过自研 GUI 大模型 + 系统层 Accessibility 协议执行 Android 任务，已与小米、vivo 等手机厂商达成深度合作，覆盖外卖、出行、社交、购物等 200+ 高频应用。",
      vertical_tags: ["手机 Agent"],
      general_tags: ["智能体", "国产"],
      hot: "🔥🔥",
    },
    {
      title: "Adobe Firefly 5 集成端到端视频生成，单镜头可达 60 秒",
      url: "https://example.com/news/firefly-5",
      source: "36氪",
      summary:
        "Adobe Max 大会发布 Firefly 5，新增原生视频生成能力，单镜头长度最长 60 秒，并与 Premiere Pro 实现剪辑工作流无缝集成。",
      pub_time: "2026-05-19 09:40:00",
      main_section: "AI+ 垂直应用",
      sub_section: "创意工具",
      relevance: 0.86,
      hot_level: 0.85,
      rank: 1,
      headline:
        "Adobe Firefly 5 推出端到端视频生成，最长 60 秒、与 Premiere 深度集成",
      plain_explain:
        "创意 SaaS 老牌厂商正式把视频生成做到工具链里，剪辑师角色面临重塑。",
      impacts: [
        "短视频/广告行业生产成本进一步下行",
        "Runway、Pika 等独立厂商压力加大",
      ],
      digest_for_outline:
        "Firefly 5 视频模型支持 1080p、60s 单镜头生成，支持人物一致性与镜头语言控制。Premiere Pro 内可一键扩写镜头、生成 B-roll、补全过渡，所有生成内容自动写入 Content Credentials。",
      vertical_tags: ["创意工具"],
      general_tags: ["视频生成", "工具"],
      hot: "🔥🔥🔥",
    },
    {
      title: "Meta 推出 RayBan-3 智能眼镜：原生 LLM 推理，电池续航 12h",
      url: "https://example.com/news/rayban-3",
      source: "钛媒体",
      summary:
        "Meta 发布与 EssilorLuxottica 联合开发的 RayBan-3 智能眼镜，搭载本地 LLM 推理芯片，支持实时翻译、信息流摘要与第一人称视频生成。",
      pub_time: "2026-05-19 08:00:00",
      main_section: "AI+ 垂直应用",
      sub_section: "AI 硬件",
      relevance: 0.82,
      hot_level: 0.84,
      rank: 2,
      headline:
        "Meta RayBan-3 智能眼镜发布：本地 LLM 推理 + 12 小时续航",
      plain_explain:
        "AI 眼镜从噱头变日用品的关键一代，国内厂商压力会迅速跟上。",
      impacts: [
        "推动小型化 NPU 与超低功耗 LLM 加速发展",
        "国内 AI 眼镜创业项目融资节奏加快",
      ],
      digest_for_outline:
        "RayBan-3 重 42g，搭载 Meta 自研 NPU，可本地运行 3B 参数模型。续航 12 小时（普通使用），支持实时翻译、信息流摘要、第一人称视频生成等场景。预计 6 月开售，起售价 449 美元。",
      vertical_tags: ["AI 硬件"],
      general_tags: ["智能硬件", "Meta"],
      hot: "🔥🔥",
    },
    {
      title: "国内首份《大模型安全治理白皮书》发布",
      url: "https://example.com/news/llm-security-whitepaper",
      source: "InfoQ",
      summary:
        "中国信通院联合多家头部企业发布《大模型安全治理白皮书 (2026)》，提出分级评估、红队测试、内容溯源等十大治理建议。",
      pub_time: "2026-05-19 14:00:00",
      main_section: "AI 产业与观察",
      sub_section: "安全治理",
      relevance: 0.7,
      hot_level: 0.62,
      rank: 1,
      headline:
        "信通院发布《大模型安全治理白皮书》，给出十条落地建议",
      plain_explain:
        "国内合规框架进一步具体化，企业模型上线前的红队测试将成为必选项。",
      impacts: [
        "推动企业上线大模型前进行系统化安全评估",
        "安全评测、红队服务商需求增加",
      ],
      digest_for_outline:
        "《大模型安全治理白皮书 (2026)》系统梳理风险类别、评估方法与治理框架。提出包括分级备案、红队测试、内容溯源、训练数据治理、第三方审计等十项落地建议，已被多个省份纳入参考标准。",
      vertical_tags: ["安全治理"],
      general_tags: ["政策", "安全"],
      hot: "🔥",
    },
    {
      title: "Hugging Face 周下载榜：国产开源模型占据前 5 中 3 席",
      url: "https://example.com/news/hf-weekly-chart",
      source: "机器之心",
      summary:
        "Hugging Face 公布上周下载榜，国产开源模型 Qwen4-32B、DeepSeek-V4、智谱 GLM-5 分别位列第一、第二与第五。",
      pub_time: "2026-05-19 16:30:00",
      main_section: "AI 产业与观察",
      sub_section: "生态",
      relevance: 0.72,
      hot_level: 0.7,
      rank: 2,
      headline:
        "HF 周下载榜：国产开源模型占据前五中三席",
      plain_explain:
        "国产开源模型在全球开发者社区的认可度进入新阶段。",
      impacts: [
        "国产模型出海开发者生态进一步加强",
        "海外二开/微调产业链兴起",
      ],
      digest_for_outline:
        "Hugging Face 上周下载榜显示，Qwen4-32B 周下载 130 万次居首，DeepSeek-V4 紧随其后，GLM-5 位列第五。海外开发者占下载量约 65%。",
      vertical_tags: ["生态"],
      general_tags: ["开源", "生态"],
      hot: "🔥",
    },
  ],
};

export const MOCK_BRIEFINGS: Record<string, Briefing> = {
  "2026-05-21": briefing_2026_05_21,
  "2026-05-20": briefing_2026_05_20,
  "2026-05-19": briefing_2026_05_19,
};

export const MOCK_DATES: string[] = Object.keys(MOCK_BRIEFINGS).sort((a, b) =>
  a < b ? 1 : -1
);
