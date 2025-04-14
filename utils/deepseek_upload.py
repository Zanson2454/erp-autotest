import os
import requests
from typing import Optional, Dict, Any

class DeepSeekAPI:
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 DeepSeek API 客户端
        
        参数:
            api_key: API密钥，如果不提供则从环境变量 DEEPSEEK_API_KEY 中获取
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DeepSeek API key is required. Set it via constructor or DEEPSEEK_API_KEY environment variable.")
        
        self.base_url = "https://api.deepseek.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def chat_completion(self, messages: list, model: str = "deepseek-chat", temperature: float = 0.0, **kwargs) -> Dict[str, Any]:
        """
        向 DeepSeek API 发送聊天完成请求
        
        参数:
            messages: 消息列表，每个消息是一个包含 'role' 和 'content' 的字典
            model: 使用的模型名称
            temperature: 控制响应的随机性（0.0 表示最确定性）
            **kwargs: API 调用的其他参数
        
        返回:
            API 响应的字典
        """
        endpoint = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        
        response = requests.post(endpoint, headers=self.headers, json=payload)
        response.raise_for_status()
        
        return response.json()

def test_deepseek_connection():
    """
    测试 DeepSeek API 连接
    使用一个简单的提示来验证 API 是否正常工作
    """
    try:
        api = DeepSeekAPI(api_key="sk-b7faf6c6196b40a8be0cd984277d8196")
        messages = [
            {"role": "user", "content": "请用Python写一个简单的计算器函数，要求支持加减乘除基本运算。"}
        ]
        
        response = api.chat_completion(messages, temperature=0.0)
        print("DeepSeek API 连接成功！")
        print("响应:", response)
        return True
    except Exception as e:
        print(f"连接 DeepSeek API 时出错: {str(e)}")
        return False

if __name__ == "__main__":
    test_deepseek_connection()
