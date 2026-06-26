"""
大模型API封装模块
统一抽象层，支持多模型切换
"""

import os
import time
import json
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from pathlib import Path


class LLMClient(ABC):
    """大模型客户端基类"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        pass


class OpenAICompatibleClient(LLMClient):
    """OpenAI兼容API客户端（支持qwen3.7-plus等）"""
    
    def __init__(self, api_key: str, base_url: str, model: str,
                 timeout: int = 120, retry: int = 3):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = timeout
        self.retry = retry
        
        # 成本控制
        self.usage_log = []
        self.log_file = Path("output/api_usage.log")
        self.log_file.parent.mkdir(exist_ok=True)
    
    def generate(self, prompt: str, **kwargs) -> str:
        """调用OpenAI兼容API生成文本"""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 4096)
        }
        
        for attempt in range(self.retry):
            try:
                start_time = time.time()
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                result = response.json()
                
                # 记录用量
                usage = result.get("usage", {})
                self._log_usage(prompt, usage, time.time() - start_time)
                
                # 提取内容
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    raise Exception(f"API返回格式错误: {result}")
                    
            except Exception as e:
                if attempt < self.retry - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
                else:
                    raise Exception(f"API调用失败（重试{self.retry}次）: {str(e)}")
    
    def _log_usage(self, prompt: str, usage: Dict, duration: float):
        """记录API调用用量"""
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model": self.model,
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "duration_seconds": round(duration, 2)
        }
        self.usage_log.append(log_entry)
        
        # 追加到日志文件
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def get_total_usage(self) -> Dict:
        """获取总用量统计"""
        total_prompt = sum(u["prompt_tokens"] for u in self.usage_log)
        total_completion = sum(u["completion_tokens"] for u in self.usage_log)
        total_tokens = sum(u["total_tokens"] for u in self.usage_log)
        
        return {
            "calls": len(self.usage_log),
            "total_prompt_tokens": total_prompt,
            "total_completion_tokens": total_completion,
            "total_tokens": total_tokens
        }


class MockClient(LLMClient):
    """Mock客户端，用于测试（不消耗API额度）"""
    
    def __init__(self, mock_responses: Optional[List[Dict]] = None):
        self.mock_responses = mock_responses or []
        self.call_count = 0
    
    def generate(self, prompt: str, **kwargs) -> str:
        """返回mock响应"""
        if self.call_count < len(self.mock_responses):
            response = self.mock_responses[self.call_count]
            self.call_count += 1
            return response
        return "Mock响应"


def load_env_config() -> Dict:
    """从.env文件加载配置"""
    env_path = Path(__file__).parent.parent / ".env"
    config = {}
    
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()
    
    return config


def create_llm_client(config: Dict = None, use_mock: bool = False) -> LLMClient:
    """工厂方法：根据配置创建客户端
    
    Args:
        config: API配置（可选，默认从.env读取）
        use_mock: 是否使用Mock客户端（测试用，不消耗API）
    """
    if use_mock:
        return MockClient()
    
    # 优先使用传入配置，否则从.env读取
    if not config:
        config = load_env_config()
    
    api_key = config.get("LLM_API_KEY") or os.getenv("LLM_API_KEY")
    base_url = config.get("LLM_API_BASE_URL") or os.getenv("LLM_API_BASE_URL", "http://172.16.1.250:3000/v1")
    model = config.get("LLM_MODEL") or os.getenv("LLM_MODEL", "qwen3.7-plus")
    
    if not api_key:
        raise ValueError("缺少LLM_API_KEY配置，请检查.env文件")
    
    return OpenAICompatibleClient(
        api_key=api_key,
        base_url=base_url,
        model=model,
        timeout=config.get("timeout", 30),
        retry=config.get("retry", 3)
    )
