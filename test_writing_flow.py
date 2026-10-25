"""
测试与验证脚本：模拟全流程长文智能写作工作流
测试提示词工程构建、上下文流转、长文串联扩写与 Markdown 自动归档落盘。
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from pathlib import Path
from core.config import DEFAULT_MODEL, get_default_api_key
from core.prompt_templates import (
    build_system_prompt,
    build_outline_prompt,
    build_chapter_writing_prompt
)
from core.context_manager import ContextManager
from core.llm_service import LLMService
from core.markdown_builder import MarkdownBuilder

def run_test():
    print("=" * 60)
    print("🚀 开始执行 AI 智能写作助手端到端功能验证...")
    print("=" * 60)

    # 1. 验证密钥与服务
    api_key = get_default_api_key()
    print(f"[*] 检测到 API Key: {api_key[:6]}...{api_key[-4:] if len(api_key) > 10 else ''}")
    llm = LLMService(api_key=api_key)

    # 2. 模拟写作任务
    topic = "大语言模型赋能现代软件工程：从代码生成到自主软件智能体"
    genre = "技术方案与开发文档"
    audience = "软件架构师与人工智能研发工程师"
    length_goal = "中篇长文 (~3500字)"
    
    print(f"\n[1/4] 正在根据提示词工程生成结构大纲...")
    print(f"      主题: {topic}")
    sys_prompt = build_system_prompt(genre)
    outline_prompt = build_outline_prompt(topic, genre, audience, length_goal, "包含系统架构图说明与演进趋势对比")
    
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": outline_prompt}
    ]
    
    outline_text = llm.generate_text(messages, model=DEFAULT_MODEL, max_tokens=1500)
    print("\n----- 生成的结构大纲预览 -----")
    print(outline_text[:400] + "\n...")

    # 3. 初始化上下文管理器
    ctx_mgr = ContextManager()
    ctx_mgr.init_document(topic, genre, topic, audience, outline_text)
    chapters = ctx_mgr.doc_state["chapters"]
    print(f"\n[2/4] 大纲解析成功，提取到 {len(chapters)} 个核心章节。")

    # 4. 模拟逐章节扩写（生成前2章作为完整闭环验证）
    test_chapters_to_gen = chapters[:2]
    accumulated_content = []

    for i, ch in enumerate(test_chapters_to_gen):
        ch_idx = i + 1
        ch_title = ch.get("title", f"第 {ch_idx} 章")
        print(f"\n[3/4] 正在基于上下文扩写第 {ch_idx} 章: {ch_title}...")
        
        prev_summary = chapters[i - 1].get("summary", "") if i > 0 else ""
        next_title = chapters[i + 1].get("title", "") if i + 1 < len(chapters) else ""
        
        ch_prompt = build_chapter_writing_prompt(
            doc_title=topic,
            genre=genre,
            chapter_index=ch_idx,
            total_chapters=len(chapters),
            chapter_title=ch_title,
            chapter_outline="\n".join(ch.get("points", [])) if ch.get("points") else ch_title,
            prev_chapter_summary=prev_summary,
            next_chapter_title=next_title,
            target_words=600
        )
        
        ch_messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": ch_prompt}
        ]
        
        content = llm.generate_text(ch_messages, model=DEFAULT_MODEL, max_tokens=1500)
        ctx_mgr.update_chapter_content(i, content)
        accumulated_content.append(content)
        print(f"      第 {ch_idx} 章撰写完成，长度: {len(content)} 字符，已提取过渡摘要。")

    # 5. 装配与落盘 Markdown
    print(f"\n[4/4] 正在汇编标准 Markdown 并注入 Front Matter 元数据...")
    full_body = "\n\n---\n\n".join(accumulated_content)
    final_md = MarkdownBuilder.assemble_document(
        title=topic,
        genre=genre,
        body_content=full_body,
        tags=["软件工程", "大语言模型", "自主智能体", "技术架构"],
        model_name=DEFAULT_MODEL
    )
    
    saved_file = MarkdownBuilder.save_to_result(topic, final_md)
    print(f"✅ 测试完成！Markdown成果已持久化存储至:\n   {saved_file}")
    
    word_count = MarkdownBuilder.count_words(final_md)
    read_time = MarkdownBuilder.estimate_reading_time(word_count)
    print(f"📊 统计数据：总字数 = {word_count} 字，预估阅读时间 = {read_time} 分钟。")

if __name__ == "__main__":
    run_test()
