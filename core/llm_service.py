"""
AI智能写作助手 - 大模型调用服务 (LLM Service)
基于标准 OpenAI 协议封装，全面兼容主流云端与本地大模型。
支持流式响应（Streaming）、非流式生成、一键连通性测试与异常容错。
"""

from typing import List, Dict, Generator, Optional, Any
import time
import os
from openai import OpenAI
from core.config import DEFAULT_BASE_URL, DEFAULT_MODEL, get_default_api_key

class LLMService:
    """大模型通信与生成服务类，负责与各大模型 API 进行交互"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key if api_key is not None else get_default_api_key()
        self.base_url = base_url if base_url else DEFAULT_BASE_URL
        self._init_client()

    def _init_client(self) -> None:
        """初始化 OpenAI 兼容客户端"""
        # 对于本地 Ollama 或无需 key 的服务，传入非空占位符
        effective_key = self.api_key.strip() if self.api_key else "sk-placeholder"
        self.client = OpenAI(
            api_key=effective_key,
            base_url=self.base_url.strip(),
            timeout=120.0
        )

    def update_credentials(self, api_key: str, base_url: Optional[str] = None) -> None:
        """动态更新 API 凭证与目标服务端点"""
        self.api_key = api_key.strip() if api_key else ""
        if base_url:
            self.base_url = base_url.strip()
        self._init_client()

    def test_connection(self, model: str = DEFAULT_MODEL) -> Dict[str, Any]:
        """
        测试当前 API 凭证与所选模型的连通性与响应速度
        返回: {"success": bool, "latency_ms": int, "message": str, "reply": str}
        """
        if not self.api_key and "localhost" not in self.base_url and "127.0.0.1" not in self.base_url:
            return {
                "success": False,
                "latency_ms": 0,
                "message": "未配置 API Key。请在左侧边栏填写有效的 API 密钥后再试。",
                "reply": ""
            }

        start_time = time.time()
        try:
            # 发送最简测试提问
            test_messages = [{"role": "user", "content": "请回复'pong'，以确认API通信正常。"}]
            params = {
                "model": model,
                "messages": test_messages,
                "max_tokens": 30,
            }
            # 推理型模型（如 deepseek-reasoner 或 o1 系列）通常不接受自定义 temperature
            if not self._is_reasoning_model(model):
                params["temperature"] = 0.5

            response = self.client.chat.completions.create(**params)
            latency = int((time.time() - start_time) * 1000)
            
            reply_text = ""
            if response.choices:
                reply_text = response.choices[0].message.content or ""

            return {
                "success": True,
                "latency_ms": latency,
                "message": f"连接成功！延迟: {latency}ms",
                "reply": reply_text.strip()
            }
        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            error_msg = self._format_error(str(e))
            return {
                "success": False,
                "latency_ms": latency,
                "message": f"连接失败: {error_msg}",
                "reply": ""
            }

    def _is_reasoning_model(self, model_name: str) -> bool:
        """判断是否为推理型/思考型模型（通常需禁用自定义 temperature 等参数）"""
        lower = model_name.lower()
        return any(flag in lower for flag in ["reasoner", "o1-", "o3-", "r1"])

    def _format_error(self, raw_err: str) -> str:
        """将底层 API 报错转换为开发者与创作者易懂的中文说明"""
        if "AuthenticationError" in raw_err or "401" in raw_err:
            return "API Key 无效、过期或未激活，请检查填写的密钥是否正确。"
        elif "RateLimitError" in raw_err or "429" in raw_err:
            return "请求已被服务商限流，或账户额度已耗尽，请检查账户余额或稍后重试。"
        elif "NotFoundError" in raw_err or "404" in raw_err or "model_not_found" in raw_err:
            return f"模型名称在当前服务商中不存在，请检查模型名称是否拼写正确。"
        elif "ConnectionError" in raw_err or "ConnectError" in raw_err:
            return f"无法连接到 API Base URL ({self.base_url})，请检查网络或是否需要代理/服务未启动。"
        elif "timeout" in raw_err.lower():
            return "请求超时，大模型生成耗时较长，请稍后重试。"
        return raw_err

    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: str = DEFAULT_MODEL,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Generator[str, None, None]:
        """
        流式生成文本（Generator 模式，配合 Streamlit 实时流式渲染）
        """
        if not self.api_key and "localhost" not in self.base_url and "127.0.0.1" not in self.base_url:
            yield "⚠️ **未配置 API Key**：请在左侧侧边栏填入有效的 API 密钥后重试。"
            return

        try:
            params = {
                "model": model,
                "messages": messages,
                "stream": True,
            }
            if not self._is_reasoning_model(model):
                params["temperature"] = temperature
                params["max_tokens"] = max_tokens

            response = self.client.chat.completions.create(**params)
            
            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    content = getattr(delta, "content", "") or ""
                    if content:
                        yield content
        except Exception as e:
            friendly_err = self._format_error(str(e))
            yield f"\n\n❌ **模型调用发生错误**：{friendly_err}\n*(底层详情: `{str(e)}`)*"

    def generate_text(
        self,
        messages: List[Dict[str, str]],
        model: str = DEFAULT_MODEL,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> str:
        """
        非流式生成整段文本
        """
        if not self.api_key and "localhost" not in self.base_url and "127.0.0.1" not in self.base_url:
            return "⚠️ 未配置 API Key，请先在侧边栏完成设置。"

        try:
            params = {
                "model": model,
                "messages": messages,
                "stream": False,
            }
            if not self._is_reasoning_model(model):
                params["temperature"] = temperature
                params["max_tokens"] = max_tokens

            response = self.client.chat.completions.create(**params)
            if response.choices:
                return response.choices[0].message.content or ""
            return ""
        except Exception as e:
            return f"❌ 调用失败: {self._format_error(str(e))}"
