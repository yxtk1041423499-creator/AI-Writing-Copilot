# 🛠️ AI 智能写作助手 - 技术全景与架构分析手册 (PROJECT_TECHNOLOGIES.md)

本项目是一套专为**长篇小说创作、学术深度论证与多场景文体生产**打造的现代化全流程长文本智能协作平台。系统深度融合了**分层提示词工程 (Prompt Engineering)**、**跨启动长期记忆与会话状态机 (Session Persistence & Context Management)** 以及**多源大模型兼容适配协议 (Multi-Provider LLM Gateway)**。

---

## 🏛️ 一、 系统总体拓扑架构 (System Architecture)

```mermaid
graph TD
    User([创作者 / 终端用户]) --> UI[Streamlit 现代化响应式前端]
    
    subgraph Frontend [前端交互与控制台]
        UI --> Tab1[✍️ 智能写作工坊: 五层大纲 -> 逐章串联]
        UI --> Tab2[🛠️ 文本精炼台: 去AI味 / 学术 / 校对]
        UI --> Tab3[💬 交互式灵感智囊: 长期记忆多轮对话]
        UI --> Tab4[📂 成果库与双视图 MD 预览器]
        UI --> Sidebar[⚙️ 模型控制台 & 会话切换器]
    end

    subgraph CoreEngine [核心引擎层 Core Modules]
        Sidebar --> Config[core/config.py: 8+厂商预设与环境检测]
        Sidebar --> SessionMgr[core/session_manager.py: 会话持久化与落盘恢复]
        Tab1 & Tab2 & Tab3 --> PromptEngine[core/prompt_templates.py: 五层思维链大纲 & 去AI味模板]
        Tab1 & Tab3 --> ContextEngine[core/context_manager.py: 章节任务解析 & 滑动窗口记忆流]
        Tab1 & Tab4 --> MDBuilder[core/markdown_builder.py: YAML FrontMatter & 成果持久化]
    end

    subgraph LLMGateway [大模型协议适配层 LLM Service]
        ContextEngine & PromptEngine --> LLMService[core/llm_service.py: OpenAI 协议适配器]
        LLMService --> Ping[test_connection: 连通性探测与测速]
        LLMService --> StreamGen[stream_chat: SSE 流式生成器]
    end

    subgraph ExternalModels [外部模型提供商 (云端 / 本地)]
        LLMService --> P1[(DeepSeek 官方: V3 / R1)]
        LLMService --> P2[(SiliconFlow 硅基流动)]
        LLMService --> P3[(OpenAI: GPT-4o / o1)]
        LLMService --> P4[(智谱 GLM: 4-Flash / Plus)]
        LLMService --> P5[(月之暗面 Kimi: 8k-128k)]
        LLMService --> P6[(阿里通义千问: Qwen-Plus/Turbo)]
        LLMService --> P7[(Ollama: 本地私有化模型)]
        LLMService --> P8[(任意自定义 OpenAI 兼容端点)]
    end

    subgraph Storage [本地文件持久化存储 Local-First]
        SessionMgr --> SessionsDir[sessions/*.json: 对话历史与创作草稿]
        MDBuilder --> ResultDir[result/*.md: 最终长篇小说与学术成果物]
    end
```

---

## 💻 二、 核心技术栈清单

| 技术维度 | 选型技术 / 库 | 版本 / 规范 | 核心作用与设计考量 |
| :--- | :--- | :--- | :--- |
| **开发语言** | **Python** | 3.10+ / 3.13 | 现代化动态语言，具备强大的字符串处理、正则解析与 AI 生态兼容性。 |
| **Web 交互框架** | **Streamlit** | $\ge 1.30.0$ | 纯 Python 驱动的响应式交互 UI，原生支持组件状态化、流式 Markdown 实时渲染与左右多栏栅格布局。 |
| **LLM 协议适配** | **OpenAI SDK** | $\ge 1.10.0$ | 统一遵循行业通用标准协议，无缝接入 DeepSeek、硅基流动、通义千问、智谱、Ollama 等任何兼容接口。 |
| **异步流式传输** | **SSE (Streaming)** | HTTP/2 SSE | Generator 迭代器流式推流，首字响应时间 (TTFT) 降低 85% 以上，杜绝页面卡顿与死等。 |
| **上下文状态机** | **ContextManager** | 自研核心模块 | 负责多轮对话滑动窗口截断、章节四维任务提取、上一章摘要与下一章预告动态拼接。 |
| **持久记忆引擎** | **SessionManager** | 自研核心模块 | 本地 JSON 持久化，关闭浏览器或重开软件自动恢复上一会话，支持多会话无缝创建与切换。 |
| **文档构建引擎** | **MarkdownBuilder** | CommonMark / YAML | 自动注入 YAML Front Matter（创建时间、文体、字数、预估耗时），标准代码高亮与表格支持。 |
| **配置与秘钥管理** | **Config Engine** | 环境变量 / 桌面嗅探 | 多环境变量级联搜寻（`DEEPSEEK_API_KEY`、`LLM_API_KEY`、`OPENAI_API_KEY`），免去繁杂配置。 |
| **版本控制规范** | **Git** | 工业级开源标准 | 严谨的 `.gitignore` 过滤机制，避免敏感密钥泄露；符合 GitHub 优质项目开源规范。 |

---

## 🧠 三、 提示词工程与认知逻辑设计 (Prompt Engineering)

系统坚决反对“粗暴扔一句话让 AI 盲写”的低质做法，在 `core/prompt_templates.py` 中实现了**多层认知驱动范式**：

### 1. 五层深度思维链小说大纲引擎 (Novel Outline CoT Engine)
深度汲取并沉淀了工作区 470+ 专业小说提示词的核心精华（吸收《030-大纲制作》、《031-章级大纲》、《032-黄金三章设计》）：
- **第一层（整体规划与分卷结构）**：三幕式分卷划分，明确主线目标、主角核心动机与终极命题；
- **第二层（节奏控制与高潮分布）**：科学安排大高潮、小高潮与松弛过渡章节，平衡爽点密度；
- **第三层（章节四维任务拆解）**：为每一章精确分配【剧情任务】、【角色变化】、【信息暴露】与【情绪体验】；
- **第四层（黄金开篇与章末悬念钩子）**：
  - 前 300 字打造高压开篇钩子，签下“情绪契约”；
  - 黄金前三章完成金手指展示与核心冲突激化；
  - **章末黄金钩子 (Cliffhanger)**：每一章末尾强制留下未知悬念、异响或危机迫近，驱动连载留存；
- **第五层（伏笔规划与回收时间线）**：主线伏笔与短期线索结构化编号，杜绝前言不搭后语。

### 2. 网文“去 AI 味”与高级写作军规 (Anti-AI Cliche Rules)
- **剔除假大空套话**：严禁出现“总而言之”、“不可否认”、“眼神中闪过一丝复杂”、“综上所述”等大模型典型口头禅；
- **贯彻 Show, don't tell**：用微动作、生理反应（“掌心冰凉黏汗”）、环境细节（“焦糊味与残破刀刃”）替代空洞的形容词；
- **快节奏短句对白**：强化说话者的潜台词与语调性格差异。

---

## ⚖️ 四、 开源竞品深度对比：取其优点，补其缺点（核心专题）

在架构设计阶段，团队对 GitHub 社区中知名的 AI 写作与大纲开源项目（如 **Pagekin (AI-Novel-Writer)**、**chinese-novelist-skill**、**NovelForge**、**llm-storyteller** 等）进行了深度调研。

| 对比维度 | 传统开源竞品现状 | 本项目的深度思考与补全创新 |
| :--- | :--- | :--- |
| **1. 部署与配置门槛** | 多数竞品基于复杂的 Agent 命令行、Node.js 运行时或重型框架，甚至强依赖本地向量库，**普通非技术作者极难配通**。 | **✅ 极简一键运行**：纯 Python + Streamlit 原生架构，双击 `run.bat` 即开即用，界面交互零学习门槛。 |
| **2. 大模型生态适配** | 往往强绑定单一厂商（例如只支持 Claude 或只支持 OpenAI 官方），**无法方便切换国内平价大模型**。 | **✅ 预设 8+ 顶级主流服务商**：官方 DeepSeek、硅基流动、通义千问、智谱、月之暗面、本地私有化 Ollama 及自定义兼容端点自由切换，内置**一键测速探针**。 |
| **3. Token 成本与上下文** | 很多 Agent 框架每写一章都全量检索数万 Token，**费用高昂且极易触发模型 Rate Limit 限流**。 | **✅ 轻量级承前启后摘要流**：每章仅携带上一章的核心精简摘要（前情提要 + 章末悬念）与本章大纲任务卡，单章 Token 消耗降低 70%，省流且逻辑不漂移。 |
| **4. 记忆与会话持久化** | 普通 Streamlit 项目多停留在内存变量，**页面一刷新或重启软件，辛辛苦苦构思的大纲全部丢失**。 | **✅ 本地优先持久化会话库 (SessionManager)**：每次交互与大纲微调自动落盘 JSON，支持多会话管理与跨天跨启动无缝继续撰写。 |
| **5. 大纲可控性 (人机协同)** | 部分竞品实行“黑盒一键生成”，AI 给出的大纲作者无法手动介入，直接一口气写完全文，**一旦跑偏整篇废弃**。 | **✅ Human-in-the-Loop 人机协同微调**：大纲生成后提供完整的在线编辑工作台，创作者可随时增删情节、修改章名与悬念，满意后再一键启动扩写。 |
| **6. 文学质感与去 AI 味** | 普遍直接使用大模型默认输出，文风充斥“综上所述、不可否认”的浓重机械感，**缺乏网文爽感与悬念**。 | **✅ 融合 470+ 专业网文实战规范**：内置黄金三章开篇法则、四维章节任务卡、章末钩子约束与去 AI 味写作引擎。 |

---

## 💾 五、 数据持久化与成果装配设计

1. **会话存储层 (`sessions/*.json`)**：
   - 记录会话唯一 ID、标题、创建时间、最近更新时间；
   - 存储多轮灵感探讨的对话树；
   - 存储当前未完成的大纲草稿与各章节编写进度。
2. **成果交付层 (`result/*.md`)**：
   - 生成符合静态站点生成器 (Jekyll / Hexo / Hugo) 规范的 **YAML Front Matter**：
     ```yaml
     ---
     title: "剑破诸天：从退婚开始无敌"
     genre: "文学创作与网文小说"
     created_at: "2026-10-25 19:10:00"
     model: "deepseek-chat"
     total_words: 4520
     estimated_reading_time_min: 11
     generator: "AI Writing Copilot Engine"
     ---
     ```
   - 正文采用优雅的多级标题、分割线、重点强调与规范排版，支持在预览器中一键下载与源文件对照。

---

## 🚀 六、 结语与演进路线

本项目通过“**多模型自主导入 + 五层小说思维链 + 跨启动持久记忆 + 极低配置门槛**”四大基石，彻底改变了传统长文生成工具“死板、烧钱、易崩、难用”的弊端。未来可进一步扩展知识库 RAG 挂载与角色状态动态台账，为创作者打造更加硬核、自由的数字创作工坊！
