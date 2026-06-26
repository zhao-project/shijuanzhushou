"""
大模型API封装模块
统一抽象层，支持多模型切换
"""

import os
import time
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class LLMClient(ABC):
    """大模型客户端基类"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        pass


class QwenClient(LLMClient):
    """通义千问客户端"""
    
    def __init__(self, api_key: str, model: str = "qwen3.7-plus", 
                 timeout: int = 30, retry: int = 3):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.retry = retry
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    
    def generate(self, prompt: str, **kwargs) -> str:
        """调用通义千问API生成文本"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "input": {
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            "parameters": {
                "result_format": "message"
            }
        }
        
        for attempt in range(self.retry):
            try:
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                result = response.json()
                if "output" in result and "choices" in result["output"]:
                    return result["output"]["choices"][0]["message"]["content"]
                else:
                    raise Exception(f"API返回格式错误: {result}")
                    
            except Exception as e:
                if attempt < self.retry - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
                else:
                    raise Exception(f"API调用失败（重试{self.retry}次）: {str(e)}")


class MockClient(LLMClient):
    """Mock客户端，用于测试"""
    
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


def create_llm_client(config: Dict) -> LLMClient:
    """工厂方法：根据配置创建客户端"""
    provider = config.get("provider", "qwen")
    
    if provider == "qwen":
        api_key = os.getenv("QWEN_API_KEY") or config.get("api_key")
        if not api_key:
            raise ValueError("缺少QWEN_API_KEY环境变量或配置")
        return QwenClient(
            api_key=api_key,
            model=config.get("model", "qwen3.7-plus"),
            timeout=config.get("timeout", 30),
            retry=config.get("retry", 3)
        )
    elif provider == "mock":
        return MockClient(config.get("mock_responses", []))
    else:
        raise ValueError(f"不支持的provider: {provider}")
