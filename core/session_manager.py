"""
AI智能写作助手 - 会话持久化与长期记忆管理模块 (Session & Memory Manager)
实现跨启动的对话历史保存、多会话切换、长文创作状态持久化与自动恢复。
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from core.config import WORKSPACE_ROOT

# 会话本地落盘目录
SESSIONS_DIR = WORKSPACE_ROOT / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

class SessionManager:
    """管理写作会话的本地持久化、历史载入与自动记忆恢复"""

    @staticmethod
    def _generate_session_id() -> str:
        """生成带时间戳的唯一会话标识"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    @staticmethod
    def list_sessions() -> List[Dict[str, Any]]:
        """
        获取所有已保存的会话列表，按更新时间倒序排列
        """
        sessions = []
        for file_path in SESSIONS_DIR.glob("*.json"):
            try:
                content = file_path.read_text(encoding="utf-8")
                data = json.loads(content)
                sessions.append({
                    "id": data.get("id", file_path.stem),
                    "title": data.get("title", "未命名会话"),
                    "updated_at": data.get("updated_at", ""),
                    "message_count": len(data.get("chat_messages", [])),
                    "has_outline": bool(data.get("outline", "").strip()),
                    "file_path": str(file_path)
                })
            except Exception:
                continue

        # 按更新时间倒序
        sessions.sort(key=lambda s: s.get("updated_at", ""), reverse=True)
        return sessions

    @staticmethod
    def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        """读取指定会话的完整数据"""
        file_path = SESSIONS_DIR / f"{session_id}.json"
        if not file_path.exists():
            return None
        try:
            content = file_path.read_text(encoding="utf-8")
            return json.loads(content)
        except Exception:
            return None

    @staticmethod
    def save_session(
        session_id: str,
        title: str,
        chat_messages: List[Dict[str, str]],
        doc_state: Dict[str, Any],
        outline: str = "",
        full_markdown_result: str = "",
        last_saved_path: str = ""
    ) -> bool:
        """
        持久化保存会话状态至本地 JSON 文件
        """
        file_path = SESSIONS_DIR / f"{session_id}.json"
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 若会话已存在，保留原创建时间
        created_at = now_str
        if file_path.exists():
            try:
                old_data = json.loads(file_path.read_text(encoding="utf-8"))
                created_at = old_data.get("created_at", now_str)
            except Exception:
                pass

        session_data = {
            "id": session_id,
            "title": title.strip() or "新建创作会话",
            "created_at": created_at,
            "updated_at": now_str,
            "chat_messages": chat_messages,
            "doc_state": doc_state,
            "outline": outline,
            "full_markdown_result": full_markdown_result,
            "last_saved_path": last_saved_path
        }

        try:
            file_path.write_text(json.dumps(session_data, ensure_ascii=False, indent=2), encoding="utf-8")
            return True
        except Exception as e:
            print(f"会话保存失败: {e}")
            return False

    @staticmethod
    def create_new_session(title: str = "新建创作会话") -> Dict[str, Any]:
        """创建一个全新的空白会话并落盘"""
        new_id = SessionManager._generate_session_id()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        initial_data = {
            "id": new_id,
            "title": title,
            "created_at": now_str,
            "updated_at": now_str,
            "chat_messages": [],
            "doc_state": {
                "title": "",
                "genre": "",
                "topic": "",
                "audience": "",
                "outline_raw": "",
                "chapters": [],
                "current_chapter_idx": 0,
                "is_completed": False
            },
            "outline": "",
            "full_markdown_result": "",
            "last_saved_path": ""
        }
        file_path = SESSIONS_DIR / f"{new_id}.json"
        file_path.write_text(json.dumps(initial_data, ensure_ascii=False, indent=2), encoding="utf-8")
        return initial_data

    @staticmethod
    def delete_session(session_id: str) -> bool:
        """删除指定会话"""
        file_path = SESSIONS_DIR / f"{session_id}.json"
        if file_path.exists():
            try:
                file_path.unlink()
                return True
            except Exception:
                return False
        return False

    @staticmethod
    def get_latest_or_default_session() -> Dict[str, Any]:
        """获取最近活跃的会话；若不存在则自动新建"""
        sessions = SessionManager.list_sessions()
        if sessions:
            latest_data = SessionManager.get_session(sessions[0]["id"])
            if latest_data:
                return latest_data
        return SessionManager.create_new_session("默认创作会话")
