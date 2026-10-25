"""
AI智能写作助手 - 现代化交互主程序 (Streamlit Application)
功能特色：
1. 外部大模型 API 自由导入与一键连通性测速（支持 DeepSeek、硅基流动、OpenAI、智谱、Kimi、通义千问、Ollama 及自定义）；
2. 跨启动长期记忆与持久化会话管理（多会话保存、自动恢复、历史追踪）；
3. 融入工作区专业网文五层思维链大纲引擎（分卷蓝图、章级四维任务、黄金开篇、章末钩子与去AI味军规）；
4. 全流程结构化长文流水线（大纲生成 → 在线微调 → 逐章扩写 → 全文落盘与导出）；
5. 多维度文本润色与对话式灵感智囊团。
"""

import streamlit as st
import os
import time
from pathlib import Path

# 导入核心模块
from core.config import (
    MODEL_PROVIDERS,
    DEFAULT_PROVIDER_NAME,
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    AVAILABLE_MODELS,
    RESULT_DIR,
    DOCS_DIR,
    get_default_api_key
)
from core.prompt_templates import (
    GENRE_ROLES,
    NOVEL_GENRE_PRESETS,
    POLISH_MODES,
    build_system_prompt,
    build_outline_prompt,
    build_chapter_writing_prompt,
    build_polish_prompt
)
from core.context_manager import ContextManager
from core.llm_service import LLMService
from core.session_manager import SessionManager
from core.markdown_builder import MarkdownBuilder

# ==================== 页面全局配置 ====================
st.set_page_config(
    page_title="AI智能写作助手 - 结构化长文与多模型平台",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入现代极客风格定制 CSS 样式
st.markdown("""
<style>
    /* 全局主容器内边距 */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
    }
    
    /* 顶部标题栏渐变风格 */
    .app-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 45%, #06B6D4 100%);
        padding: 22px 28px;
        border-radius: 14px;
        color: white;
        margin-bottom: 22px;
        box-shadow: 0 8px 24px rgba(30, 58, 138, 0.16);
    }
    .app-header h1 {
        color: #ffffff !important;
        font-size: 1.95rem;
        font-weight: 700;
        margin: 0 0 6px 0;
    }
    .app-header p {
        color: #E0F2FE !important;
        font-size: 0.95rem;
        margin: 0;
    }
    
    /* 功能卡片样式 */
    .feature-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 14px;
    }
    
    /* 徽标标签 */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        font-size: 0.78rem;
        font-weight: 600;
        border-radius: 12px;
        background-color: #EEF2FF;
        color: #4F46E5;
        margin-right: 6px;
    }
    
    .badge-success {
        background-color: #ECFDF5;
        color: #059669;
    }
    
    /* 状态指示框圆角 */
    .stAlert {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 会话记忆与 Session State 初始化 ====================

# 1. 初始化或加载最近活跃的持久化会话
if "current_session_id" not in st.session_state:
    latest_sess = SessionManager.get_latest_or_default_session()
    st.session_state.current_session_id = latest_sess["id"]
    st.session_state.current_session_title = latest_sess["title"]
    st.session_state.current_outline = latest_sess.get("outline", "")
    st.session_state.full_markdown_result = latest_sess.get("full_markdown_result", "")
    st.session_state.last_saved_path = latest_sess.get("last_saved_path", "")
    
    st.session_state.context_mgr = ContextManager(max_history_turns=12)
    st.session_state.context_mgr.load_state(
        chat_history=latest_sess.get("chat_messages", []),
        doc_state=latest_sess.get("doc_state", {})
    )

# 2. 初始化大模型提供商及 API 凭证
if "selected_provider" not in st.session_state:
    st.session_state.selected_provider = DEFAULT_PROVIDER_NAME

if "api_key" not in st.session_state:
    st.session_state.api_key = get_default_api_key(st.session_state.selected_provider)

if "base_url" not in st.session_state:
    st.session_state.base_url = MODEL_PROVIDERS[st.session_state.selected_provider]["base_url"]

if "selected_model" not in st.session_state:
    st.session_state.selected_model = MODEL_PROVIDERS[st.session_state.selected_provider]["default_model"]

if "llm_service" not in st.session_state:
    st.session_state.llm_service = LLMService(
        api_key=st.session_state.api_key,
        base_url=st.session_state.base_url
    )

def auto_save_current_session():
    """辅助函数：将当前内存状态自动保存落盘"""
    SessionManager.save_session(
        session_id=st.session_state.current_session_id,
        title=st.session_state.current_session_title,
        chat_messages=st.session_state.context_mgr.chat_history,
        doc_state=st.session_state.context_mgr.doc_state,
        outline=st.session_state.current_outline,
        full_markdown_result=st.session_state.full_markdown_result,
        last_saved_path=st.session_state.last_saved_path
    )

def switch_session(target_session_id: str):
    """切换到目标会话并恢复状态"""
    sess_data = SessionManager.get_session(target_session_id)
    if sess_data:
        st.session_state.current_session_id = sess_data["id"]
        st.session_state.current_session_title = sess_data["title"]
        st.session_state.current_outline = sess_data.get("outline", "")
        st.session_state.full_markdown_result = sess_data.get("full_markdown_result", "")
        st.session_state.last_saved_path = sess_data.get("last_saved_path", "")
        st.session_state.context_mgr.load_state(
            chat_history=sess_data.get("chat_messages", []),
            doc_state=sess_data.get("doc_state", {})
        )

# ==================== 侧边栏控制台 ====================
with st.sidebar:
    st.markdown("### 🗂️ 会话与长期记忆管理")
    
    all_sessions = SessionManager.list_sessions()
    session_options = {s["id"]: f"{s['title']} ({s['updated_at'][5:16]})" for s in all_sessions}
    
    # 当前选中的会话
    current_sess_index = 0
    sess_id_list = list(session_options.keys())
    if st.session_state.current_session_id in sess_id_list:
        current_sess_index = sess_id_list.index(st.session_state.current_session_id)

    selected_sess_id = st.selectbox(
        "切换历史创作会话",
        options=sess_id_list,
        index=current_sess_index,
        format_func=lambda sid: session_options.get(sid, sid),
        help="所有对话、大纲构思与扩写进度均自动保存在本地，关闭重开不丢失！"
    )
    if selected_sess_id != st.session_state.current_session_id:
        switch_session(selected_sess_id)
        st.rerun()

    col_s1, col_s2 = st.columns([1, 1])
    with col_s1:
        if st.button("➕ 新建会话", use_container_width=True):
            new_sess = SessionManager.create_new_session(f"写作会话 {len(all_sessions)+1}")
            switch_session(new_sess["id"])
            st.rerun()
    with col_s2:
        if st.button("🗑️ 删除本会话", use_container_width=True):
            if len(all_sessions) > 1:
                SessionManager.delete_session(st.session_state.current_session_id)
                # 切换到列表第一个
                remaining = [s for s in all_sessions if s["id"] != st.session_state.current_session_id]
                switch_session(remaining[0]["id"])
                st.rerun()
            else:
                st.warning("至少保留一个会话")

    st.markdown("---")
    st.markdown("### ⚙️ 模型服务商与 API 导入")

    # 1. 选择大模型提供商预设
    provider_names = list(MODEL_PROVIDERS.keys())
    provider_idx = provider_names.index(st.session_state.selected_provider) if st.session_state.selected_provider in provider_names else 0
    chosen_provider = st.selectbox(
        "模型提供商预设",
        options=provider_names,
        index=provider_idx,
        help="支持 DeepSeek、硅基流动、OpenAI、智谱、Kimi、通义千问、本地 Ollama 以及自定义兼容接口"
    )

    # 若切换提供商，联动更新默认配置
    if chosen_provider != st.session_state.selected_provider:
        st.session_state.selected_provider = chosen_provider
        prov_info = MODEL_PROVIDERS[chosen_provider]
        st.session_state.base_url = prov_info["base_url"]
        st.session_state.selected_model = prov_info["default_model"]
        new_key = get_default_api_key(chosen_provider)
        st.session_state.api_key = new_key
        st.session_state.llm_service.update_credentials(new_key, prov_info["base_url"])
        st.rerun()

    prov_meta = MODEL_PROVIDERS[chosen_provider]
    st.caption(f"ℹ️ {prov_meta['description']}")

    # 2. 输入 API Key 与 Base URL
    with st.expander("🔑 接口密钥与服务地址设置", expanded=True):
        if not prov_meta["is_local"]:
            input_key = st.text_input(
                "API Key (密钥)",
                value=st.session_state.api_key,
                type="password",
                help="已自动识别本地密钥。支持填入用户自备的 API Key。"
            )
        else:
            input_key = ""
            st.info("本地 Ollama 服务无需填写 API Key。")

        input_base_url = st.text_input(
            "API Base URL (服务接口地址)",
            value=st.session_state.base_url,
            help="兼容任何 OpenAI 协议的转发地址"
        )

        if (input_key != st.session_state.api_key) or (input_base_url != st.session_state.base_url):
            st.session_state.api_key = input_key
            st.session_state.base_url = input_base_url
            st.session_state.llm_service.update_credentials(input_key, input_base_url)

    # 3. 选择或自定义模型名称
    with st.expander("🧠 模型选择与参数调校", expanded=True):
        models_for_provider = prov_meta["models"]
        
        use_custom_model = st.checkbox("✍️ 手动输入自定义模型名称", value=(st.session_state.selected_model not in models_for_provider))
        if use_custom_model:
            model_to_use = st.text_input(
                "输入自定义模型名称 (Model ID)",
                value=st.session_state.selected_model,
                help="例如: deepseek-ai/DeepSeek-V3, gpt-4o-2024-11-20, qwen-max-longcontext 等"
            )
        else:
            cur_model_idx = 0
            if st.session_state.selected_model in models_for_provider:
                cur_model_idx = models_for_provider.index(st.session_state.selected_model)
            model_to_use = st.selectbox(
                "选择该厂商模型",
                options=models_for_provider,
                index=cur_model_idx
            )
        st.session_state.selected_model = model_to_use

        # 一键测试 API 连接按钮
        if st.button("🔍 测试 API 连接与测速", use_container_width=True):
            with st.spinner("正在向模型发送握手测试探针..."):
                test_res = st.session_state.llm_service.test_connection(model=model_to_use)
                if test_res["success"]:
                    st.success(f"✅ {test_res['message']} (模型回应: '{test_res['reply']}')")
                else:
                    st.error(f"❌ {test_res['message']}")

        temperature = st.slider(
            "创造力程度 (Temperature)",
            min_value=0.0,
            max_value=1.5,
            value=0.7,
            step=0.05,
            help="越低越严谨客观，越高越具想象力与创意。"
        )
        max_tokens = st.slider(
            "单次最大生成 Token",
            min_value=1024,
            max_value=8192,
            value=4096,
            step=512
        )

    st.markdown("---")
    st.markdown("### 📊 上下文记忆状态")
    turn_count = len(st.session_state.context_mgr.chat_history)
    st.caption(f"当前会话已记忆：**{turn_count // 2}** 轮问答")
    if st.button("🧹 清空当前会话上下文", use_container_width=True):
        st.session_state.context_mgr.clear_chat()
        st.session_state.current_outline = ""
        st.session_state.full_markdown_result = ""
        st.session_state.last_saved_path = ""
        auto_save_current_session()
        st.rerun()

    st.markdown("---")
    st.markdown("### 📂 最近生成的成果物")
    saved_files = MarkdownBuilder.list_saved_documents()
    if saved_files:
        for f_item in saved_files[:5]:
            st.caption(f"📄 [{f_item['filename']}]({f_item['filename']}) ({f_item['size_kb']} KB)")
    else:
        st.caption("成果库暂无文件。")

# ==================== 主界面头部 ====================
st.markdown("""
<div class="app-header">
    <h1>✍️ AI 智能写作助手</h1>
    <p>深度融合<strong>多模型自由接入</strong>、<strong>网文五层思维链大纲</strong>、<strong>跨启动持久记忆</strong>与<strong>去AI味规范</strong>，打造专业级结构化长文创作平台。</p>
</div>
""", unsafe_allow_html=True)

# 核心四大功能工作台
tab_studio, tab_polish, tab_chat, tab_docs = st.tabs([
    "✍️ 智能写作工坊 (长文与小说构建)",
    "🛠️ 文本精炼与润色台",
    "💬 交互式灵感对话 (持久记忆)",
    "📂 成果库与 MD 预览器"
])

# ==================== TAB 1: 智能写作工坊 ====================
with tab_studio:
    st.markdown("#### 🌟 全流程长文与小说写作向导（大纲生成 → 逐章扩写 → 全文汇编）")
    
    col_input1, col_input2 = st.columns([1, 1])
    with col_input1:
        topic_input = st.text_input(
            "📝 写作核心主题 / 小说书名",
            value=st.session_state.context_mgr.doc_state.get("title") or st.session_state.context_mgr.doc_state.get("topic") or "",
            placeholder="例如：大语言模型研发落地指南 / 剑破诸天：从退婚开始无敌"
        )
        genre_choice = st.selectbox(
            "📚 目标文体规范",
            list(GENRE_ROLES.keys()),
            index=0,
            help="选择'文学创作与网文小说'将自动激活工作区专属五层思维链大纲与黄金三章设计引擎！"
        )
    with col_input2:
        audience_input = st.text_input(
            "🎯 目标读者受众",
            value=st.session_state.context_mgr.doc_state.get("audience") or "",
            placeholder="例如：技术架构师 / 网文玄幻核心付费读者群"
        )
        length_choice = st.selectbox(
            "📏 目标总篇幅预期",
            ["短篇精悍 (~1500字)", "中篇长文 (~3500字)", "深度长文 (~6000字)", "万字巨著 / 连载开篇 (~10000字)"],
            index=1
        )

    # 若是文学小说，展开题材流派与专属配置
    is_novel_mode = ("小说" in genre_choice or "文学" in genre_choice)
    sub_genre_choice = "玄幻仙侠 / 升级修真"
    if is_novel_mode:
        col_nov1, col_nov2 = st.columns([1, 1])
        with col_nov1:
            sub_genre_choice = st.selectbox(
                "🎨 小说细分题材流派 (融入预置实战提示词沉淀)",
                list(NOVEL_GENRE_PRESETS.keys()),
                index=0
            )
        with col_nov2:
            preset_info = NOVEL_GENRE_PRESETS[sub_genre_choice]
            st.info(f"💡 **流派卖点**：{preset_info['selling_point']}\n\n⏱️ **节奏要求**：{preset_info['pacing']}")

    extra_req = st.text_area(
        "💡 特殊补充要求 / 核心金手指设定 (可选)",
        placeholder="例如：要求主角性格果断决绝不圣母、必须包含核心异宝觉醒、章末留下强烈的反转悬念...",
        height=72
    )

    st.markdown("---")
    
    # 步骤 1：大纲生成
    st.markdown("##### 步骤 1：运用深度思维链 (CoT) 构建高质大纲")
    if is_novel_mode:
        st.caption("✨ 已启用【五层思维链专业小说大纲引擎】：包含分卷主线规划、节奏高潮分布、章级四维任务（剧情/角色/信息/情绪）、黄金三章钩子与伏笔时间线。")
    
    btn_gen_outline = st.button("🤖 运用提示词工程生成结构大纲", type="primary", use_container_width=True)
    if btn_gen_outline:
        if not topic_input.strip():
            st.warning("请先填写写作核心主题或小说书名！")
        else:
            with st.spinner("AI 正在运用深度思维链进行结构设计与章节拆解..."):
                sys_p = build_system_prompt(genre_choice)
                user_p = build_outline_prompt(
                    topic=topic_input,
                    genre=genre_choice,
                    audience=audience_input,
                    length_goal=length_choice,
                    additional_req=extra_req,
                    sub_genre=sub_genre_choice
                )
                
                messages = [
                    {"role": "system", "content": sys_p},
                    {"role": "user", "content": user_p}
                ]
                
                outline_output = ""
                placeholder = st.empty()
                for chunk in st.session_state.llm_service.stream_chat(
                    messages=messages,
                    model=st.session_state.selected_model,
                    temperature=temperature,
                    max_tokens=max_tokens
                ):
                    outline_output += chunk
                    placeholder.markdown(outline_output)
                
                st.session_state.current_outline = outline_output
                st.session_state.context_mgr.init_document(
                    title=topic_input,
                    genre=genre_choice,
                    topic=topic_input,
                    audience=audience_input,
                    outline_raw=outline_output,
                    sub_genre=sub_genre_choice if is_novel_mode else ""
                )
                # 自动持久化落盘
                auto_save_current_session()
                st.success("🎉 大纲构建完成！已自动保存至会话。您可以在下方进行在线审查与微调。")

    # 步骤 2：大纲审查与微调
    if st.session_state.current_outline:
        st.markdown("##### 步骤 2：大纲在线审查与微调 (Markdown 编辑)")
        edited_outline = st.text_area(
            "当前结构大纲 (支持直接手动增删小节或调整悬念钩子)",
            value=st.session_state.current_outline,
            height=240
        )
        if edited_outline != st.session_state.current_outline:
            st.session_state.current_outline = edited_outline
            st.session_state.context_mgr.init_document(
                title=topic_input or "未命名文稿",
                genre=genre_choice,
                topic=topic_input,
                audience=audience_input,
                outline_raw=edited_outline,
                sub_genre=sub_genre_choice if is_novel_mode else ""
            )
            auto_save_current_session()

        # 步骤 3：逐章节扩写与串联汇编
        st.markdown("##### 步骤 3：基于承前启后记忆流串联逐章扩写")
        chapters = st.session_state.context_mgr.doc_state.get("chapters", [])
        st.info(f"系统从大纲中精准识别出 **{len(chapters)}** 个核心章节。接下来将严格遵守【去AI味军规】，携带前文摘要、本章任务卡与章末钩子进行全文章节流式撰写。")

        col_b1, col_b2 = st.columns([1, 1])
        with col_b1:
            btn_start_write = st.button("🚀 启动全文章节串联构建", type="primary", use_container_width=True)
        with col_b2:
            if st.button("💾 立即保存当前进度与大纲", use_container_width=True):
                auto_save_current_session()
                st.success("已手动保存到当前会话！")

        if btn_start_write:
            full_content_accumulated = ""
            progress_bar = st.progress(0.0)
            status_text = st.empty()
            content_display = st.empty()

            total_chs = len(chapters)
            for idx, ch in enumerate(chapters):
                ch_title = ch.get("title", f"第 {idx+1} 节")
                vol_name = ch.get("volume", "")
                vol_prefix = f"[{vol_name}] " if vol_name and vol_name != "正篇" else ""
                status_text.markdown(f"⏳ **正在撰写第 {idx+1}/{total_chs} 章：{vol_prefix}{ch_title}...**")
                
                # 获取上一章承前启后摘要
                prev_summary = ""
                if idx > 0:
                    prev_summary = chapters[idx - 1].get("summary", "")
                
                # 获取下一章标题预告
                next_title = ""
                if idx + 1 < total_chs:
                    next_title = chapters[idx + 1].get("title", "")

                chapter_prompt = build_chapter_writing_prompt(
                    doc_title=topic_input or "未命名作品",
                    genre=genre_choice,
                    chapter_index=idx + 1,
                    total_chapters=total_chs,
                    chapter_title=f"{vol_prefix}{ch_title}",
                    chapter_outline="\n".join(ch.get("points", [])) if ch.get("points") else ch_title,
                    prev_chapter_summary=prev_summary,
                    next_chapter_title=next_title,
                    target_words=950
                )

                messages = [
                    {"role": "system", "content": build_system_prompt(genre_choice)},
                    {"role": "user", "content": chapter_prompt}
                ]

                chapter_text = ""
                for chunk in st.session_state.llm_service.stream_chat(
                    messages=messages,
                    model=st.session_state.selected_model,
                    temperature=temperature,
                    max_tokens=max_tokens
                ):
                    chapter_text += chunk
                    temp_full = full_content_accumulated + "\n\n" + chapter_text
                    content_display.markdown(temp_full)

                # 记录本章成果与摘要至上下文管理器
                st.session_state.context_mgr.update_chapter_content(idx, chapter_text)
                full_content_accumulated += "\n\n" + chapter_text
                progress_bar.progress((idx + 1) / total_chs)

            status_text.markdown("✅ **全文章节扩写与逻辑串联全部完成！**")
            
            # 汇编 Markdown，注入 Front Matter 元数据并落盘
            final_md = MarkdownBuilder.assemble_document(
                title=topic_input or "智能长篇文稿",
                genre=genre_choice,
                body_content=full_content_accumulated,
                model_name=st.session_state.selected_model
            )
            st.session_state.full_markdown_result = final_md
            saved_path = MarkdownBuilder.save_to_result(topic_input or "长篇成果", final_md)
            st.session_state.last_saved_path = str(saved_path)
            
            # 自动持久化落盘至会话库
            auto_save_current_session()
            st.balloons()

    # 步骤 4：全文成果展示、下载与存储
    if st.session_state.full_markdown_result:
        st.markdown("---")
        st.markdown("##### 步骤 4：成果物展示与导出 (已自动落盘至 result 目录)")
        
        word_count = MarkdownBuilder.count_words(st.session_state.full_markdown_result)
        read_time = MarkdownBuilder.estimate_reading_time(word_count)
        
        st.markdown(f"""
        <div class="feature-card">
            <span class="badge badge-success">已持久化归档</span>
            <span class="badge">会话已记忆</span><br>
            <strong>本地文件路径：</strong><code>{st.session_state.last_saved_path}</code><br>
            <strong>总字数统计：</strong>{word_count} 字 &nbsp;|&nbsp; <strong>预估阅读耗时：</strong>{read_time} 分钟
        </div>
        """, unsafe_allow_html=True)

        col_d1, col_d2 = st.columns([1, 1])
        with col_d1:
            st.download_button(
                label="📥 下载标准 Markdown 文件 (.md)",
                data=st.session_state.full_markdown_result,
                file_name=f"{topic_input[:20] if topic_input else 'article'}.md",
                mime="text/markdown",
                use_container_width=True
            )
        with col_d2:
            if st.button("📋 刷新最新构建内容", use_container_width=True):
                st.rerun()

        with st.expander("📖 查看完整 Markdown 源码", expanded=False):
            st.code(st.session_state.full_markdown_result, language="markdown")

        with st.expander("👁️ 查看渲染排版效果", expanded=True):
            st.markdown(st.session_state.full_markdown_result)

# ==================== TAB 2: 文本精炼与润色台 ====================
with tab_polish:
    st.markdown("#### 🛠️ 文本多维度精炼与专业润色")
    st.caption("针对已有草稿进行去AI味改造、网文生动化、学术化重构、错别字校对或提炼摘要，输出精准修改解析。")

    col_p1, col_p2 = st.columns([3, 2])
    with col_p1:
        raw_text_input = st.text_area(
            "输入原始文本草稿",
            placeholder="请在此粘贴需要润色、校对、去AI味或扩写的原始段落...",
            height=260
        )
    with col_p2:
        polish_mode = st.selectbox("选择润色模式", list(POLISH_MODES.keys()), index=0)
        st.info(f"💡 **模式说明**：{POLISH_MODES[polish_mode]}")
        extra_polish_inst = st.text_input("个性化改写要求 (可选)", placeholder="例如：多用短句动作、突出主角压抑与爆发情绪")
        btn_polish = st.button("✨ 执行智能精修与解析", type="primary", use_container_width=True)

    if btn_polish:
        if not raw_text_input.strip():
            st.warning("请先输入待润色的原始文本！")
        else:
            with st.spinner(f"正在以【{polish_mode}】模式对文本进行深度重构..."):
                prompt = build_polish_prompt(raw_text_input, polish_mode, extra_polish_inst)
                messages = [
                    {"role": "system", "content": "你是一位顶级文学主编、学术审稿人与公文校对专家。"},
                    {"role": "user", "content": prompt}
                ]
                
                polish_result = ""
                res_box = st.empty()
                for chunk in st.session_state.llm_service.stream_chat(
                    messages=messages,
                    model=st.session_state.selected_model,
                    temperature=temperature,
                    max_tokens=max_tokens
                ):
                    polish_result += chunk
                    res_box.markdown(polish_result)
                
                st.success("润色与解析生成完毕！")

# ==================== TAB 3: 交互式灵感对话 (带跨启动记忆) ====================
with tab_chat:
    st.markdown("#### 💬 交互式灵感智囊团（跨启动持久记忆）")
    st.caption(f"当前会话：**{st.session_state.current_session_title}**。围绕写作灵感、角色设定、爽点伏笔自由探讨，对话自动永久落盘。")

    # 渲染历史消息
    for msg in st.session_state.context_mgr.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 输入新消息
    if user_query := st.chat_input("向写作智囊团提问，例如：'帮我设计一个反派表面温和实则狠戾的登场情节'"):
        # 记录用户消息
        st.session_state.context_mgr.add_message("user", user_query)
        with st.chat_message("user"):
            st.markdown(user_query)

        # AI 思考并流式回复
        with st.chat_message("assistant"):
            sys_prompt = "你是一位博学且富有洞察力的故事创作与写作智囊专家。在协助用户写作时，请优先使用清晰规范的 Markdown 格式输出构思、设定卡或对话场景。"
            messages = st.session_state.context_mgr.get_messages_for_llm(system_prompt=sys_prompt)
            
            ai_reply = ""
            msg_box = st.empty()
            for chunk in st.session_state.llm_service.stream_chat(
                messages=messages,
                model=st.session_state.selected_model,
                temperature=temperature,
                max_tokens=max_tokens
            ):
                ai_reply += chunk
                msg_box.markdown(ai_reply)

            # 存入上下文并自动落盘持久化
            st.session_state.context_mgr.add_message("assistant", ai_reply)
            
            # 若是第一轮对话，智能以问题前 12 个字重命名会话
            if len(st.session_state.context_mgr.chat_history) == 2 and st.session_state.current_session_title == "新建创作会话":
                st.session_state.current_session_title = user_query[:16]

            auto_save_current_session()

# ==================== TAB 4: 成果库与 MD 预览器 ====================
with tab_docs:
    st.markdown("#### 📂 成果管理与 Markdown 查看器")
    st.caption(f"集中管理存放在 `{RESULT_DIR}` 下的所有 Markdown 产出物。")

    all_docs = MarkdownBuilder.list_saved_documents()
    if not all_docs:
        st.info("💡 成果库中暂无文档，请在【智能写作工坊】中生成长文，系统将自动归档。")
    else:
        col_list, col_view = st.columns([1, 2])
        with col_list:
            st.markdown("##### 📑 文件列表")
            selected_filename = st.selectbox(
                "选择要查看或导出的文档",
                options=[d["filename"] for d in all_docs]
            )
            for d in all_docs:
                if d["filename"] == selected_filename:
                    st.caption(f"📅 修改时间：{d['modified_time']}")
                    st.caption(f"💾 文件大小：{d['size_kb']} KB")
                    break

        with col_view:
            if selected_filename:
                content = MarkdownBuilder.read_document(selected_filename)
                st.download_button(
                    label=f"📥 导出并下载 {selected_filename}",
                    data=content,
                    file_name=selected_filename,
                    mime="text/markdown",
                    use_container_width=True
                )
                
                view_mode = st.radio("展示模式", ["排版渲染视图", "Markdown 源码视图"], horizontal=True)
                if view_mode == "排版渲染视图":
                    st.markdown(content)
                else:
                    st.code(content, language="markdown")
