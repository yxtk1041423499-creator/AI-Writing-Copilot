# ✍️ AI 智能写作助手 (AI Writing Copilot)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?logo=streamlit&logoColor=white)
![OpenAI Compatible](https://img.shields.io/badge/API-OpenAI%20Compatible-412991?logo=openai&logoColor=white)
![DeepSeek](https://img.shields.io/badge/DeepSeek-V3%20%2F%20R1%20Ready-0066FF)
![License](https://img.shields.io/badge/License-MIT-green)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)

**面向长篇小说创作者、学者与写作者的现代化全流程长文本智能协作平台**  
*集「外部多模型接入 · 五层思维链大纲 · 跨启动持久记忆 · 网文去AI味军规 · 人机协同分步构建」于一体*

[✨ 核心亮点](#-核心亮点与技术革新) • [🚀 快速上手](#-快速启动指南) • [⚙️ 多模型接入](#️-多模型导入与自定义配置) • [📖 技术栈全景](PROJECT_TECHNOLOGIES.md) • [⚖️ 竞品对比](#-开源竞品对比与补全优势)

</div>

---

## 🌟 核心亮点与技术革新

### 1. 🔌 外部大模型 API 自由导入与连通性测速
- **预设 8+ 主流大模型平台**：官方 DeepSeek (V3/R1)、SiliconFlow (硅基流动)、OpenAI (GPT-4o/o1)、智谱 GLM、月之暗面 Kimi、阿里通义千问、Ollama 本地私有化模型。
- **自定义兼容接口**：任意 OpenAI 协议中转站、OneAPI、NewAPI 或自建端点均可一键填入。
- **一键网络测速探针**：界面提供「🔍 测试 API 连接与测速」按钮，毫秒级反馈握手延迟与模型状态。

### 2. 🧠 跨启动持久化记忆与会话状态机
- **告别页面刷新数据丢失**：内置 `SessionManager`，所有多轮灵感对话、未完成的大纲草稿、章节进度均自动持久化落盘（JSON）。
- **多创作会话自由管理**：支持“新建会话”、“历史切换”、“重命名”与“一键归档”。
- **下次打开直接续写**：重启应用或更换浏览器，原创作进度与上下文原汁原味自动载入。

### 3. 📚 五层思维链专业小说大纲工坊 (Novel Outline Engine)
深度提炼工作区沉淀的 **470+ 专业网文实战提示词**（吸收《030-大纲制作》、《031-章级大纲》、《032-黄金三章设计》等规范）：
- **第一层（整体分卷与主线）**：规划分卷使命、阶段目标与主角终极动机；
- **第二层（节奏控制与高潮分布）**：大高潮、小高潮与松弛过渡章节动态排布；
- **第三层（章节四维任务拆解）**：单章精确定义【剧情任务】、【角色变化】、【信息透露】与【情绪体验】；
- **第四层（黄金开篇与章末悬念钩子）**：前300字情绪契约构建；每章末尾强制留下抓人的 **Cliffhanger（章末悬念钩子）**；
- **第五层（伏笔规划与回收时间线）**：主线伏笔与暗线结构化编号，杜绝吃书。

### 4. 🚨 网文“去 AI 味”与高级写作军规 (Anti-AI Cliche Engine)
- **全面清除 AI 常用套话**：彻底杜绝“总而言之”、“不可否认”、“眼神中闪过一丝复杂”、“不得不说”等机械空洞辞令。
- **严格贯彻 Show, don't tell**：用生理细节、具体微动作、环境声效与对话潜台词替代抽象叙述。

### 5. 🤝 人机协同长文流水线 (Human-in-the-Loop)
- **拒绝黑盒式生成**：大纲生成后提供可视化在线编辑台，支持创作者手动调整小节、剧情走向与悬念。
- **承前启后轻量记忆流**：逐章扩写时，系统自动携带全局命题、上一章精要摘要、本章任务卡与后章预告，在保证逻辑连贯的同时降低 70% Token 消耗。

### 6. 🛠️ 成果持久化与多维润色台
- **规范 Front Matter 装配**：自动生成符合静态站点标准的 YAML 元数据（字数统计、阅读耗时、模型指纹）。
- **6 维专业精修润色**：包含【去AI味与生动网文化】、【学术规范化】、【错别字校对】、【扩写丰富】、【精炼提炼】等模式。

---

## ⚖️ 开源竞品对比与补全优势

相较于 GitHub 上现有的 AI 写作工具（如 Pagekin、NovelForge、llm-storyteller 等），本项目针对痛点进行了全面改良：

| 对比维度 | 传统开源竞品现状 | 本项目的深度补全与创新 |
| :--- | :--- | :--- |
| **部署难度** | 强依赖 Node.js/Agent 复杂命令或本地向量库，安装门槛高 | **极简架构**：纯 Python + Streamlit，双击 `run.bat` 即启 |
| **模型支持** | 多固定单一模型（如仅限 Claude 或特定厂商） | **开放生态**：8+ 预设平台 + 任意自定义模型 + 连通测速 |
| **数据持久化** | 普通工具刷新页面数据全丢；或采用复杂数据库难迁移 | **本地优先**：纯 JSON/Markdown 持久化，随时导出备份 |
| **大纲可控性** | 黑盒一键写到底，作者无法插手中间过程 | **人机协同**：大纲可视可编，确认后再逐章流式扩写 |
| **Token 消耗** | 动辄全量向量检索，长篇写作成倍烧钱 | **精简摘要流**：动态生成承前启后微摘要，省流又防遗忘 |
| **文风质感** | 充满“综上所述”机器套话，行文平淡 | **去AI味规范**：融合 470+ 网文提示词实战经验与章末钩子 |

---

## 📁 项目目录结构

```
AI问答助手/
│
├── app.py                       # 现代化交互主程序 (Streamlit UI)
├── run.bat                      # Windows 双击一键启动脚本
├── requirements.txt             # 核心依赖清单 (streamlit, openai 等)
├── README.md                    # 本项目技术说明与开源指南
├── PROJECT_TECHNOLOGIES.md      # 详细的技术栈架构分析手册
├── .env.example                 # 环境变量配置模板
├── .gitignore                   # 工业级 Git 忽略配置 (安全防泄露)
├── LICENSE                      # MIT 开源许可证
│
├── core/                        # 核心架构引擎模块包
│   ├── __init__.py
│   ├── config.py                # 8+ 大模型厂商预设与 API 凭证管理
│   ├── llm_service.py           # 大模型通信服务 (流式生成与连接测速)
│   ├── prompt_templates.py      # 五层思维链大纲引擎与去AI味模板库
│   ├── context_manager.py       # 章节任务解析与承前启后轻量记忆流
│   ├── session_manager.py       # 本地会话持久化与跨启动长期记忆
│   └── markdown_builder.py      # Markdown 构建与 YAML Front Matter 装配
│
├── sessions/                    # 本地会话持久化存储库 (*.json)
├── result/                      # 最终生成的 Markdown 长篇著作库 (*.md)
├── docs/                        # 系统架构与提示词技术规范
└── 写小说提示词/                 # 470+ 专业网文小说全流程实战提示词集
```

---

## 🚀 快速启动指南

### 方式一：双击一键运行（推荐 Windows 用户）
在项目根目录直接双击 **`run.bat`**：
系统将自动检测运行环境并启动服务，自动弹出浏览器访问 `http://localhost:8501`。

### 方式二：命令行手动启动
```bash
# 1. 安装核心依赖
pip install -r requirements.txt

# 2. 启动 Streamlit 服务
streamlit run app.py
```
终端启动后，访问浏览器地址：`http://localhost:8501`。

---

## ⚙️ 多模型导入与自定义配置

1. 打开应用后，在左侧侧边栏的 **「模型提供商预设」** 下拉列表中选择您使用的服务商：
   - **DeepSeek (官方)**：支持 `deepseek-chat` (V3) 与 `deepseek-reasoner` (R1)；
   - **SiliconFlow (硅基流动)**：超低成本极速推理平台，支持各类顶尖开源模型；
   - **OpenAI (官方)**：支持 `gpt-4o`, `gpt-4o-mini`, `o1-mini`；
   - **智谱 GLM / Kimi / 通义千问**：国内各大主流旗舰模型；
   - **Ollama (本地私有化)**：无需任何 API Key，100% 隐私安全；
   - **自定义兼容接口**：填入任何第三方 API Base URL 与模型标识。
2. 填入您的 **API Key**（系统亦会自动尝试识别系统环境变量或桌面密钥）；
3. 点击 **「🔍 测试 API 连接与测速」**，即可实时查看接口响应延迟与连通状态！

---

## 📚 详细技术架构手册

关于本项目的完整拓扑图、认知工程框架、提示词设计哲学及竞品深度对比，请参阅：
👉 [PROJECT_TECHNOLOGIES.md - 架构与技术全景分析手册](PROJECT_TECHNOLOGIES.md)

---

## 🤝 贡献与开源协议

欢迎提交 Issue 与 Pull Request 共同改进本项目！  
本项目采用 [MIT License](LICENSE) 开源许可证，可自由用于学术研究、个人创作与商业应用。
