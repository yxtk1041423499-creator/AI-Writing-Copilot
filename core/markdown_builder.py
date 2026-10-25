"""
AI智能写作助手 - Markdown 构建与成果管理模块 (Markdown Builder)
负责 Front Matter 元数据注入、字数与统计计算、成果自动落盘保存以及文档库管理。
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from core.config import RESULT_DIR

class MarkdownBuilder:
    """Markdown 文档构建与存储管理器"""

    @staticmethod
    def count_words(text: str) -> int:
        """
        计算中英文混合字数统计：
        中文字符算 1 字，英文连续单词算 1 词。
        """
        # 移除 Markdown 标记符号
        cleaned = re.sub(r'[#*`~>|\-_\[\]\(\)]', ' ', text)
        # 匹配中文字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fa5]', cleaned))
        # 匹配英文单词
        english_words = len(re.findall(r'\b[a-zA-Z0-9_-]+\b', cleaned))
        return chinese_chars + english_words

    @staticmethod
    def estimate_reading_time(word_count: int) -> int:
        """根据人均 350-400字/分钟 估算阅读所需时间（分钟）"""
        minutes = max(1, round(word_count / 350))
        return minutes

    @classmethod
    def assemble_document(
        cls,
        title: str,
        genre: str,
        body_content: str,
        author: str = "AI智能写作助手",
        tags: Optional[List[str]] = None,
        model_name: str = "deepseek-chat"
    ) -> str:
        """
        构建包含标准 YAML Front Matter 声明的 Markdown 文档
        """
        word_count = cls.count_words(body_content)
        read_time = cls.estimate_reading_time(word_count)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        tags_str = ", ".join(tags) if tags else "AI写作, 结构化构建, Markdown"

        front_matter = f"""---
title: "{title}"
date: {now_str}
author: "{author}"
genre: "{genre}"
tags: [{tags_str}]
model: "{model_name}"
word_count: {word_count}
reading_time: "{read_time} 分钟"
---

"""
        # 如果正文开头没有大标题，补全一级大标题
        if not body_content.strip().startswith("# "):
            assembled = front_matter + f"# {title}\n\n" + body_content.strip()
        else:
            assembled = front_matter + body_content.strip()

        return assembled

    @classmethod
    def save_to_result(cls, title: str, markdown_content: str) -> Path:
        """
        将生成的 Markdown 文档自动持久化存储至 result/ 目录
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 清洗文件名中的非法字符
        safe_title = re.sub(r'[\\/:*?"<>| ]', '_', title)[:30]
        filename = f"{timestamp}_{safe_title}.md"
        file_path = RESULT_DIR / filename

        file_path.write_text(markdown_content, encoding="utf-8")
        return file_path

    @classmethod
    def list_saved_documents(cls) -> List[Dict[str, Any]]:
        """
        列出 result/ 目录下所有的 Markdown 文档及其元数据
        """
        doc_list = []
        if not RESULT_DIR.exists():
            return doc_list

        files = sorted(RESULT_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        for f in files:
            stat = f.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            doc_list.append({
                "filename": f.name,
                "path": str(f.resolve()),
                "size_kb": round(stat.st_size / 1024, 2),
                "modified_time": mtime
            })
        return doc_list

    @classmethod
    def read_document(cls, filename: str) -> str:
        """读取指定的 Markdown 文档内容"""
        file_path = RESULT_DIR / filename
        if file_path.exists():
            return file_path.read_text(encoding="utf-8")
        return ""
