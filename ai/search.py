"""
网络搜索模块 - 在知识库信息不足时补充网络搜索结果
支持: Tavily API（有免费额度）/ 可选关闭
"""
import os
import requests


def search_web(query, max_results=3):
    """使用 Tavily API 进行网络搜索
    
    Args:
        query: 搜索关键词(str)
        max_results: 返回结果数量(int)，默认3
    
    Returns:
        list[dict]: 搜索结果列表，每项包含:
            - title: 标题
            - url: 链接
            - content: 内容摘要
    
    Note:
        Tavily 免费额度: 1000次/月，足够日常使用
        需要设置环境变量 TAVILY_API_KEY
        如果未设置API Key或搜索失败，返回空列表（不影响主流程）
    
    Tavily官网: https://tavily.com/
    """
    api_key = os.environ.get('TAVILY_API_KEY')
    if not api_key:
        # 未配置Tavily，跳过网络搜索
        return []

    try:
        url = "https://api.tavily.com/search"
        data = {
            "api_key": api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "basic",  # basic模式，节省API调用
            "include_answer": False,
            "include_raw_content": False,
        }
        resp = requests.post(url, json=data, timeout=15)
        resp.raise_for_status()
        result = resp.json()

        results = []
        for item in result.get('results', []):
            results.append({
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'content': item.get('content', ''),
            })
        return results

    except Exception as e:
        # 搜索失败不影响主流程，仅打印警告
        print(f"[WARN] 网络搜索失败: {e}")
        return []


def format_search_results(results):
    """将搜索结果格式化为文本，用于拼接到LLM的上下文中
    
    Args:
        results: search_web() 返回的搜索结果列表
    
    Returns:
        str: 格式化后的搜索结果文本
    
    示例输出:
        【网络搜索结果】
        1. [标题1]
           内容摘要1
        
        2. [标题2]
           内容摘要2
    """
    if not results:
        return ""

    parts = ["【网络搜索结果】"]
    for i, item in enumerate(results, 1):
        parts.append(f"{i}. {item['title']}")
        parts.append(f"   {item['content'][:300]}")  # 截取前300字避免过长
        parts.append("")
    return '\n'.join(parts)
