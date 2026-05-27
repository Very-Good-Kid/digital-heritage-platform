"""
Embedding 层 - 将文本转化为向量表示

双后端支持:
  - SiliconFlow BAAI/bge-large-zh-v1.5 (免费, 中文专用, 1024维, 512 tokens)
  - 智谱AI embedding-3 (备选, 2048维)

默认使用SiliconFlow免费模型，智谱AI作为备选。
通过环境变量 EMBEDDING_PROVIDER 切换: 'siliconflow'(默认) | 'zhipu'

API文档:
  - SiliconFlow: https://docs.siliconflow.cn/cn/api-reference/embeddings
  - 智谱AI: https://open.bigmodel.cn/dev/api/text/embedding-3
"""
import os
import requests


# ===== SiliconFlow Embedding (免费) =====
def _siliconflow_embed(texts, api_key):
    """调用SiliconFlow BAAI/bge-large-zh-v1.5 生成向量

    Args:
        texts: 文本列表(list[str])，单次最多32个文本
        api_key: SiliconFlow API密钥(str)

    Returns:
        list[list[float]]: 向量列表，每个向量是1024维浮点数组

    模型: BAAI/bge-large-zh-v1.5
      - 中文专用embedding，C-MTEB榜单排名靠前
      - 1024维，最大512 tokens
      - SiliconFlow上免费调用（实名认证后）

    API端点: https://api.siliconflow.cn/v1/embeddings (OpenAI兼容格式)
    """
    url = "https://api.siliconflow.cn/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "BAAI/bge-large-zh-v1.5",
        "input": texts,
        "encoding_format": "float"
    }
    resp = requests.post(url, headers=headers, json=data, timeout=30)
    resp.raise_for_status()
    result = resp.json()
    embeddings = sorted(result['data'], key=lambda x: x['index'])
    return [item['embedding'] for item in embeddings]


# ===== 智谱AI Embedding (备选) =====
def _zhipu_embed(texts, api_key):
    """调用智谱AI Embedding API 生成向量

    Args:
        texts: 文本列表(list[str])，单次最多16个文本
        api_key: 智谱AI API密钥(str)

    Returns:
        list[list[float]]: 向量列表，每个向量是2048维浮点数组

    模型: embedding-3 (智谱最新embedding模型，2048维)
    """
    url = "https://open.bigmodel.cn/api/paas/v4/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "embedding-3",
        "input": texts
    }
    resp = requests.post(url, headers=headers, json=data, timeout=30)
    resp.raise_for_status()
    result = resp.json()
    embeddings = sorted(result['data'], key=lambda x: x['index'])
    return [item['embedding'] for item in embeddings]


# ===== 统一接口 =====
def get_embedding_provider():
    """获取当前的 Embedding 提供者

    环境变量:
        EMBEDDING_PROVIDER: 'siliconflow' | 'zhipu'，默认 'siliconflow'

    Returns:
        str: 当前提供者名称
    """
    return os.environ.get('EMBEDDING_PROVIDER', 'siliconflow').lower()


def embed_texts(texts):
    """将文本列表转化为向量列表

    Args:
        texts: 待向量化的文本列表(list[str])

    Returns:
        list[list[float]]: 向量列表

    自动根据 EMBEDDING_PROVIDER 环境变量选择后端:
        - siliconflow(默认): BAAI/bge-large-zh-v1.5, 免费, 1024维, 批量32
        - zhipu: embedding-3, 2048维, 批量16
    """
    provider = get_embedding_provider()

    if provider == 'siliconflow':
        api_key = os.environ.get('SILICONFLOW_API_KEY')
        if not api_key:
            raise ValueError("未设置 SILICONFLOW_API_KEY 环境变量，请在 .env 中配置")
        batch_size = 32
        embed_fn = _siliconflow_embed
    elif provider == 'zhipu':
        api_key = os.environ.get('ZHIPU_API_KEY')
        if not api_key:
            raise ValueError("未设置 ZHIPU_API_KEY 环境变量，请在 .env 中配置")
        batch_size = 16
        embed_fn = _zhipu_embed
    else:
        raise ValueError(f"不支持的 EMBEDDING_PROVIDER: {provider}，可选: siliconflow, zhipu")

    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embs = embed_fn(batch, api_key)
        all_embeddings.extend(embs)

    return all_embeddings


def embed_single(text):
    """将单条文本转化为向量（便捷方法）

    Args:
        text: 待向量化的文本(str)

    Returns:
        list[float]: 向量（浮点数组）
    """
    return embed_texts([text])[0]


def cosine_similarity(vec_a, vec_b):
    """计算两个向量的余弦相似度

    Args:
        vec_a: 向量A(list[float])
        vec_b: 向量B(list[float])

    Returns:
        float: 余弦相似度，范围[-1, 1]，越大越相似

    公式: cos(A,B) = (A·B) / (|A| * |B|)
    """
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = sum(a * a for a in vec_a) ** 0.5
    norm_b = sum(b * b for b in vec_b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)
