"""
AI智能写作助手 - 上下文生命周期管理引擎 (Context Management Engine)
负责维护多轮对话历史、滑动窗口截断、多层级小说与长文大纲状态解析、
以及轻量级跨章节衔接记忆流（有效防止 Token 爆炸与前后断层）。
"""

from typing import List, Dict, Optional, Any
import re

class ContextManager:
    """管理写作助手的多轮上下文记忆与长文状态追踪状态机"""

    def __init__(self, max_history_turns: int = 12):
        self.max_history_turns = max_history_turns
        self.chat_history: List[Dict[str, str]] = []
        
        # 长文创作工作流状态机
        self.doc_state: Dict[str, Any] = {
            "title": "",
            "genre": "",
            "sub_genre": "",
            "topic": "",
            "audience": "",
            "outline_raw": "",
            "chapters": [], # 存放解析后的章节对象: {"title": ..., "volume": ..., "points": [...], "content": "", "summary": ""}
            "current_chapter_idx": 0,
            "is_completed": False
        }

    # ==================== 对话上下文管理 ====================

    def add_message(self, role: str, content: str) -> None:
        """追加一条消息至对话历史，并执行滑动窗口修剪"""
        self.chat_history.append({"role": role, "content": content})
        self._prune_history()

    def get_messages_for_llm(self, system_prompt: Optional[str] = None) -> List[Dict[str, str]]:
        """获取传递给大模型的完整消息序列（包含可选 System 角色提示词）"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(self.chat_history)
        return messages

    def clear_chat(self) -> None:
        """清空对话历史"""
        self.chat_history.clear()

    def _prune_history(self) -> None:
        """根据滑动窗口截断历史记录，确保不会超出模型上下文限制"""
        max_messages = self.max_history_turns * 2
        if len(self.chat_history) > max_messages:
            self.chat_history = self.chat_history[-max_messages:]

    # ==================== 长文分步创作状态管理 ====================

    def init_document(
        self,
        title: str,
        genre: str,
        topic: str,
        audience: str,
        outline_raw: str,
        sub_genre: str = ""
    ) -> None:
        """初始化长文与小说创作状态，自动解析大纲为章节任务列表"""
        self.doc_state["title"] = title
        self.doc_state["genre"] = genre
        self.doc_state["sub_genre"] = sub_genre
        self.doc_state["topic"] = topic
        self.doc_state["audience"] = audience
        self.doc_state["outline_raw"] = outline_raw
        self.doc_state["chapters"] = self.parse_outline(outline_raw)
        self.doc_state["current_chapter_idx"] = 0
        self.doc_state["is_completed"] = False

    def parse_outline(self, outline_text: str) -> List[Dict[str, Any]]:
        """
        智能解析 Markdown 大纲文本，兼容通用长文大纲与专业分卷小说大纲。
        提取出各章节名称、所属分卷以及细纲要点（任务、冲突、章末钩子等）。
        """
        chapters: List[Dict[str, Any]] = []
        lines = outline_text.splitlines()
        current_volume = "正篇"
        current_ch: Optional[Dict[str, Any]] = None

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            # 1. 识别分卷，例如: "### 第一卷：潜龙在渊" 或 "## 卷一：xxx"
            vol_match = re.search(r'^(?:#{2,4}|\*\*)\s*(?:第[一二三四五六七八九十\d]+卷|卷[一二三四五六七八九十\d]+)\s*[:：]?\s*(.*?)(?:\*\*)?$', line_str)
            if vol_match:
                vol_name = vol_match.group(1).replace("**", "").strip()
                current_volume = vol_name if vol_name else line_str.replace("#", "").strip()
                continue

            # 2. 识别章节行，例如:
            # "- **第1章：退婚台前的黑石戒**"
            # "- **第一章：引言与背景**"
            # "## 第1章 xxx" 或 "1. 第1章 xxx"
            ch_match = re.search(
                r'^(?:-|\*|\d+\.)?\s*(?:\*\*)?(?:第[一二三四五六七八九十\d]+章|[0-9]+[\.、])\s*[:：]?\s*(.*?)(?:\*\*)?$',
                line_str
            )
            # 兼容以 ## 第X章 开头的写法
            if not ch_match and (line_str.startswith("## ") or line_str.startswith("### ")):
                cleaned_h = line_str.lstrip("#").strip()
                if "章" in cleaned_h or re.match(r'^\d+[\.、]', cleaned_h):
                    ch_match = re.search(r'^(.*)$', cleaned_h)

            if ch_match:
                title = ch_match.group(1).replace("**", "").strip()
                if not title:
                    title = line_str.replace("#", "").replace("*", "").strip()

                current_ch = {
                    "title": title,
                    "volume": current_volume,
                    "points": [],
                    "content": "",
                    "summary": ""
                }
                chapters.append(current_ch)
            elif current_ch:
                # 累加本章节下的小节、四维任务卡、章末钩子等
                # 避免把无关的大标题吸纳进上一章节
                if not line_str.startswith("# ") and not line_str.startswith("## 📚"):
                    current_ch["points"].append(line_str)

        # 后备机制：若未成功匹配章节标识，则按有序列表行提取
        if not chapters:
            for line in lines:
                cleaned = line.strip().lstrip("-*# 0123456789.、")
                if cleaned and len(cleaned) > 2 and ("章" in cleaned or "节" in cleaned or line.strip().startswith("- ")):
                    chapters.append({
                        "title": cleaned,
                        "volume": current_volume,
                        "points": [],
                        "content": "",
                        "summary": ""
                    })

        return chapters

    def update_chapter_content(self, index: int, content: str) -> None:
        """更新指定章节的正文，并自动提炼轻量级承前启后摘要"""
        if 0 <= index < len(self.doc_state["chapters"]):
            self.doc_state["chapters"][index]["content"] = content
            # 生成承前启后摘要（提取前180字与后120字章末悬念，避免Token膨胀）
            clean_content = re.sub(r'#+\s*', '', content).strip()
            summary = clean_content[:180]
            if len(clean_content) > 250:
                summary += " ... [尾声悬念] " + clean_content[-120:]
            self.doc_state["chapters"][index]["summary"] = summary

    def get_full_assembled_markdown(self) -> str:
        """汇编已生成的各章节为完整长篇 Markdown 正文"""
        parts = []
        for ch in self.doc_state.get("chapters", []):
            if ch.get("content"):
                parts.append(ch["content"].strip())
        return "\n\n---\n\n".join(parts)

    # ==================== 会话状态导出与恢复 ====================

    def export_state(self) -> Dict[str, Any]:
        """导出当前状态用于持久化"""
        return {
            "chat_history": list(self.chat_history),
            "doc_state": dict(self.doc_state)
        }

    def load_state(self, chat_history: List[Dict[str, str]], doc_state: Dict[str, Any]) -> None:
        """从持久化记录中恢复对话历史与创作状态"""
        self.chat_history = list(chat_history)
        if doc_state:
            self.doc_state = dict(doc_state)
