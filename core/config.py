"""
AI智能写作助手 - 配置管理模块
支持主流外部大模型厂商预设、自定义模型导入、环境凭证加载与工作区路径管理。
"""

import os
from pathlib import Path
from typing import Dict, Any, List

# 获取工作区根目录
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

# 成果输出目录与文档目录
RESULT_DIR = WORKSPACE_ROOT / "result"
DOCS_DIR = WORKSPACE_ROOT / "docs"

# 确保关键目录存在
RESULT_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

# ==================== 大模型提供商预设配置 ====================
# 支持各大主流云端与本地大模型接口（统一遵循 OpenAI API 规范）
MODEL_PROVIDERS: Dict[str, Dict[str, Any]] = {
    "DeepSeek (官方)": {
        "base_url": "https://api.deepseek.com",
        "default_model": "deepseek-chat",
        "models": ["deepseek-chat", "deepseek-reasoner"],
        "description": "国产顶尖大模型，文笔流畅、高性价比，支持深度推理",
        "env_key": "DEEPSEEK_API_KEY",
        "is_local": False
    },
    "SiliconFlow (硅基流动)": {
        "base_url": "https://api.siliconflow.cn/v1",
        "default_model": "deepseek-ai/DeepSeek-V3",
        "models": [
            "deepseek-ai/DeepSeek-V3",
            "deepseek-ai/DeepSeek-R1",
            "Qwen/Qwen2.5-72B-Instruct",
            "Qwen/Qwen2.5-14B-Instruct",
            "meta-llama/Llama-3.3-70B-Instruct"
        ],
        "description": "极速云端推理平台，支持 DeepSeek R1/V3、通义千问等全系列模型",
        "env_key": "SILICONFLOW_API_KEY",
        "is_local": False
    },
    "OpenAI (官方)": {
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o",
        "models": ["gpt-4o", "gpt-4o-mini", "o1-mini", "o1-preview", "gpt-3.5-turbo"],
        "description": "OpenAI 官方旗舰模型，具备卓越的指令遵循与逻辑分析能力",
        "env_key": "OPENAI_API_KEY",
        "is_local": False
    },
    "智谱 GLM (BigModel)": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "default_model": "glm-4-flash",
        "models": ["glm-4-flash", "glm-4-plus", "glm-4-long", "glm-4-air"],
        "description": "智谱清言大模型，中文理解与长文本能力出众（glm-4-flash 免费高效）",
        "env_key": "ZHIPU_API_KEY",
        "is_local": False
    },
    "月之暗面 Kimi (Moonshot)": {
        "base_url": "https://api.moonshot.cn/v1",
        "default_model": "moonshot-v1-8k",
        "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
        "description": "超长文本处理先锋，适合长篇小说全景推演与设定检索",
        "env_key": "MOONSHOT_API_KEY",
        "is_local": False
    },
    "阿里百炼通义千问 (DashScope)": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "default_model": "qwen-plus",
        "models": ["qwen-plus", "qwen-turbo", "qwen-max", "qwen2.5-72b-instruct"],
        "description": "阿里云通义千问系列，知识面广，中文创作能力极其丰富",
        "env_key": "DASHSCOPE_API_KEY",
        "is_local": False
    },
    "Ollama (本地私有化大模型)": {
        "base_url": "http://localhost:11434/v1",
        "default_model": "deepseek-r1:latest",
        "models": ["deepseek-r1:latest", "deepseek-v3:latest", "qwen2.5:7b", "llama3.3:latest"],
        "description": "纯本地部署大模型，100% 数据隐私安全，无需联网与 API Key",
        "env_key": "",
        "is_local": True
    },
    "自定义兼容接口 (Custom OpenAI-Compatible)": {
        "base_url": "https://api.openai.com/v1",
        "default_model": "custom-model",
        "models": ["custom-model"],
        "description": "支持用户接入自建中转、OneAPI、NewAPI 或其他兼容 OpenAI 格式的模型",
        "env_key": "CUSTOM_LLM_API_KEY",
        "is_local": False
    }
}

DEFAULT_PROVIDER_NAME = "DeepSeek (官方)"
DEFAULT_BASE_URL = MODEL_PROVIDERS[DEFAULT_PROVIDER_NAME]["base_url"]
DEFAULT_MODEL = MODEL_PROVIDERS[DEFAULT_PROVIDER_NAME]["default_model"]
AVAILABLE_MODELS = MODEL_PROVIDERS[DEFAULT_PROVIDER_NAME]["models"]

def get_default_api_key(provider_name: str = DEFAULT_PROVIDER_NAME) -> str:
    """
    智能搜寻并返回可用的 API Key：
    1. 优先读取系统环境变量（如 LLM_API_KEY 或特定提供商的环境变量）
    2. 次选读取 Windows 桌面的 deepseek API key.txt（兼容旧习惯）
    3. 找不到则返回空字符串
    """
    provider_info = MODEL_PROVIDERS.get(provider_name, {})
    env_var_name = provider_info.get("env_key", "")
    
    # 检查特定环境变量
    if env_var_name:
        key = os.getenv(env_var_name, "").strip()
        if key:
            return key
            
    # 检查通用大模型变量
    for common_var in ["LLM_API_KEY", "DEEPSEEK_API_KEY", "OPENAI_API_KEY"]:
        key = os.getenv(common_var, "").strip()
        if key:
            return key

    # 尝试查找桌面上的文件
    desktop_candidates = [
        Path(os.path.expanduser("~")) / "Desktop" / "deepseek API key.txt",
        Path("C:/Users/Administrator/Desktop/deepseek API key.txt"),
    ]
    for candidate in desktop_candidates:
        if candidate.exists() and candidate.is_file():
            try:
                content = candidate.read_text(encoding="utf-8")
                for line in content.splitlines():
                    cleaned = line.strip()
                    if cleaned.startswith("sk-"):
                        return cleaned
            except Exception:
                pass

    return ""
