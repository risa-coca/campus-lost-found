import json
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

def extract_item_attributes(title: str, description: str) -> dict:
    """调用本地 Qwen 提取物品的结构化属性"""
    prompt = f"""
    你是一个校园失物招领系统的AI助手。请从以下物品信息中提取关键属性。
    标题：{title}
    描述：{description}
    
    请严格输出JSON格式，不要包含任何其他文字：
    {{"color": "颜色(没有填未知)", "brand": "品牌(没有填未知)", "item_type": "物品具体类型(如雨伞/手机/校园卡)", "special_marks": "特殊标记特征(如挂件/贴纸/破损)"}}
    """
    
    payload = {
        "model": "qwen2.5:1.5b",
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return json.loads(result["response"])
    except Exception as e:
        print(f"LLM 抽取失败，降级处理: {e}")
        return {"color": "未知", "brand": "未知", "item_type": "其他", "special_marks": "无"}