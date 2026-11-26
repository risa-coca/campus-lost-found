import base64
from app.config import settings
from zai import ZhipuAiClient # 确保导入的是正确的类

def analyze_image_with_glm(image_url: str, prompt: str = "请详细描述这张图片中的物品，包括它的类别、颜色、品牌、材质以及任何显著的特征。"):
    """
    调用智谱GLM-4.6V-Flash模型分析图片 (Base64方式)
    """
    api_key = settings.ZHIPU_API_KEY
    if not api_key:
        print("未配置 ZHIPU_API_KEY")
        return None
        
    # 1. 将本地图片文件读取并转为base64编码
    local_path = image_url.split(settings.PUBLIC_BASE_URL)[-1].lstrip('/')
    try:
        with open(local_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        print(f"读取本地图片失败: {e}")
        return None

    # 2. 初始化客户端并调用
    client = ZhipuAiClient(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="glm-4.6v-flash",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"视觉模型调用失败: {e}")
        return None