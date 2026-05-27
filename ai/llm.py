"""
LLM 模块 - 调用大语言模型生成回答

双后端支持:
  - 智谱AI (主): 文本对话 glm-4-flash(免费), 视觉问答 glm-4.6v-flash(免费)
  - SiliconFlow (备): 文本对话 Qwen/Qwen2.5-7B-Instruct(免费), 429排队时自动切换

支持输出模式:
  - 流式输出(SSE): 逐token推送，适用于文本对话
  - 非流式输出: 一次性返回完整回答，适用于视觉问答

环境变量:
  ZHIPU_API_KEY: 智谱AI API密钥(必需)，在 https://open.bigmodel.cn/ 注册获取
  SILICONFLOW_API_KEY: SiliconFlow API密钥(可选)，在 https://cloud.siliconflow.cn/ 注册获取
"""
import os
import json
import requests


# ==============================================================================
# 系统提示词
# ==============================================================================
SYSTEM_PROMPT = """你是"故里助手"，一个专业的数字资产规划与继承法律顾问AI。

你的职责：
1. 回答用户关于数字资产继承的法律问题
2. 根据知识库资料给出准确、专业的建议
3. 知识库信息不足时，可结合常识回答，但须标注"以上建议仅供参考，请以最新法律法规为准"
4. 用户上传图片时，根据图片内容理解和回答

回答要求：
- 使用中文回答
- 专业、准确、有条理
- 直接回答用户问题，不要自我介绍（如"你好，我是故里助手"），不要寒暄，直接切入正题
- 涉及法律问题时，提醒用户咨询专业律师
- 不要编造不存在的法律条文或政策
- 引用知识库内容时，说"根据知识库资料"或"根据相关资料"，不要说"根据您提供的参考资料"或"根据上传的文档"
- 知识库对用户不可见，不要暴露知识库的技术细节（如文件名、分块、向量化等）
- 用户上传图片时，先描述图片内容，再结合问题给出回答
"""


# ==============================================================================
# API 端点和模型常量
# ==============================================================================
# 智谱AI
ZHIPU_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
ZHIPU_TEXT_MODEL = "glm-4.7-flash"

# SiliconFlow (OpenAI兼容格式)
SILICONFLOW_API_URL = "https://api.siliconflow.cn/v1/chat/completions"
SILICONFLOW_TEXT_MODEL = "Qwen/Qwen3.5-4B"

# 视觉模型优先级列表（仅智谱AI，429排队时按顺序自动尝试下一个）
VISION_MODELS = ["glm-4.6v-flash", "glm-4.1v-thinking-flash", "glm-4v-flash"]


# ==============================================================================
# 核心函数: chat()
# ==============================================================================
def chat(messages, stream=False):
    """调用大语言模型生成回答（统一入口）

    策略:
      - 文本对话: 优先智谱AI glm-4-flash, 429时自动切换SiliconFlow Qwen2.5-7B
      - 视觉问答: 仅智谱AI视觉模型(SiliconFlow无免费视觉模型), 429时自动切换备选视觉模型

    Args:
        messages: 对话消息列表(list[dict])
            纯文本格式:
                [{"role": "system", "content": "系统提示"},
                 {"role": "user", "content": "用户问题"},
                 {"role": "assistant", "content": "AI回答"}]
            视觉问答格式(content为列表):
                [{"role": "user", "content": [
                    {"type": "text", "text": "请描述这张图片"},
                    {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
                ]}]
        stream: 是否启用流式输出(bool)
            - 纯文本对话: stream=True时逐token返回生成器
            - 视觉问答: 自动使用非流式(stream参数被忽略)，一次性返回完整回答

    Returns:
        stream=False时: 返回完整回答文本(str)
        stream=True时:  返回生成器，每次yield一个token文本片段(str)
    """
    zhipu_key = os.environ.get('ZHIPU_API_KEY')
    if not zhipu_key:
        raise Exception("未设置ZHIPU_API_KEY，请在.env中配置智谱AI API密钥")

    has_image = _has_image_in_messages(messages)

    if has_image:
        # 视觉问答: 仅智谱AI（SiliconFlow无免费视觉模型）
        return _chat_vision(messages, zhipu_key)
    else:
        # 文本对话: 智谱AI优先，429时切换SiliconFlow
        return _chat_text(messages, stream, zhipu_key)


# ==============================================================================
# 文本对话（智谱AI优先 + SiliconFlow备选）
# ==============================================================================
def _chat_text(messages, stream, zhipu_key):
    """文本对话：智谱AI优先，429排队时自动切换SiliconFlow

    Args:
        messages: 对话消息列表(list[dict])
        stream: 是否流式输出(bool)
        zhipu_key: 智谱AI API密钥(str)

    Returns:
        流式时返回生成器，非流式时返回完整文本(str)
    """
    # 构建智谱AI请求
    headers = {
        "Authorization": f"Bearer {zhipu_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": ZHIPU_TEXT_MODEL,
        "messages": messages,
        "stream": stream,
        "max_tokens": 4096,
        "temperature": 0.7
    }

    if stream:
        # 流式请求: 先尝试智谱AI，429时切换SiliconFlow
        # timeout=(连接超时, 读取超时): 读取设300s防止长回答中途断开
        resp = requests.post(ZHIPU_API_URL, headers=headers, json=data, stream=True, timeout=(30, 300))
        if resp.ok:
            return _parse_sse_stream(resp)
        elif resp.status_code == 429:
            # 智谱AI排队，尝试SiliconFlow
            sf_result = _try_siliconflow_stream(messages)
            if sf_result is not None:
                return sf_result
            # SiliconFlow也不行，抛异常
            _raise_api_error(resp, "智谱AI")
        else:
            _raise_api_error(resp, "智谱AI")
    else:
        # 非流式请求
        resp = requests.post(ZHIPU_API_URL, headers=headers, json=data, timeout=120)
        if resp.ok:
            return resp.json()['choices'][0]['message']['content']
        elif resp.status_code == 429:
            # 智谱AI排队，尝试SiliconFlow
            sf_result = _try_siliconflow_non_stream(messages)
            if sf_result is not None:
                return sf_result
            _raise_api_error(resp, "智谱AI")
        else:
            _raise_api_error(resp, "智谱AI")


def _try_siliconflow_stream(messages):
    """尝试SiliconFlow流式请求

    Args:
        messages: 对话消息列表(list[dict])

    Returns:
        生成器或None(SiliconFlow不可用时)
    """
    sf_key = os.environ.get('SILICONFLOW_API_KEY')
    if not sf_key:
        print("[INFO] 未配置SILICONFLOW_API_KEY，跳过SiliconFlow备选")
        return None

    print(f"[INFO] 智谱AI排队中，尝试SiliconFlow {SILICONFLOW_TEXT_MODEL}...")
    headers = {
        "Authorization": f"Bearer {sf_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": SILICONFLOW_TEXT_MODEL,
        "messages": messages,
        "stream": True,
        "max_tokens": 4096,
        "temperature": 0.7
    }
    try:
        resp = requests.post(SILICONFLOW_API_URL, headers=headers, json=data, stream=True, timeout=(30, 300))
        if resp.ok:
            print(f"[INFO] 切换到SiliconFlow {SILICONFLOW_TEXT_MODEL} 成功")
            return _parse_sse_stream(resp)
        else:
            print(f"[WARN] SiliconFlow请求失败({resp.status_code})")
            return None
    except Exception as e:
        print(f"[WARN] SiliconFlow请求异常: {e}")
        return None


def _try_siliconflow_non_stream(messages):
    """尝试SiliconFlow非流式请求

    Args:
        messages: 对话消息列表(list[dict])

    Returns:
        str或None(SiliconFlow不可用时)
    """
    sf_key = os.environ.get('SILICONFLOW_API_KEY')
    if not sf_key:
        print("[INFO] 未配置SILICONFLOW_API_KEY，跳过SiliconFlow备选")
        return None

    print(f"[INFO] 智谱AI排队中，尝试SiliconFlow {SILICONFLOW_TEXT_MODEL}...")
    headers = {
        "Authorization": f"Bearer {sf_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": SILICONFLOW_TEXT_MODEL,
        "messages": messages,
        "stream": False,
        "max_tokens": 4096,
        "temperature": 0.7
    }
    try:
        resp = requests.post(SILICONFLOW_API_URL, headers=headers, json=data, timeout=120)
        if resp.ok:
            print(f"[INFO] 切换到SiliconFlow {SILICONFLOW_TEXT_MODEL} 成功")
            return resp.json()['choices'][0]['message']['content']
        else:
            print(f"[WARN] SiliconFlow请求失败({resp.status_code})")
            return None
    except Exception as e:
        print(f"[WARN] SiliconFlow请求异常: {e}")
        return None


# ==============================================================================
# 视觉问答（仅智谱AI）
# ==============================================================================
def _chat_vision(messages, zhipu_key):
    """视觉问答：仅使用智谱AI视觉模型，429排队时自动切换备选视觉模型

    Args:
        messages: 包含图片的对话消息列表(list[dict])
        zhipu_key: 智谱AI API密钥(str)

    Returns:
        str: 模型生成的完整回答文本

    注意: 视觉问答不支持流式输出，始终返回完整文本
    """
    model = VISION_MODELS[0]
    headers = {
        "Authorization": f"Bearer {zhipu_key}",
        "Content-Type": "application/json"
    }
    # 视觉模型不支持stream/temperature/max_tokens参数，传了会返回400
    data = {"model": model, "messages": messages}

    resp = requests.post(ZHIPU_API_URL, headers=headers, json=data, timeout=120)

    # 429排队时，逐个尝试备选视觉模型
    if not resp.ok and resp.status_code == 429:
        tried = [model]
        for fallback in VISION_MODELS[1:]:
            print(f"[INFO] 视觉模型 {model} 排队中，尝试备选 {fallback}...")
            tried.append(fallback)
            data["model"] = fallback
            resp = requests.post(ZHIPU_API_URL, headers=headers, json=data, timeout=120)
            if resp.ok:
                print(f"[INFO] 切换到 {fallback} 成功")
                break
        else:
            err_info = _extract_error_message(resp)
            raise Exception(f"智谱AI视觉模型全部排队({', '.join(tried)})，请稍后重试: {err_info}")

    if not resp.ok:
        _raise_api_error(resp, "智谱AI")

    return resp.json()['choices'][0]['message']['content']


# ==============================================================================
# 错误处理
# ==============================================================================
def _extract_error_message(resp):
    """从API响应中提取错误信息

    Args:
        resp: requests响应对象

    Returns:
        str: 错误信息文本
    """
    try:
        err_body = resp.json()
        return err_body.get('error', {}).get('message', '') or str(err_body)[:300]
    except:
        return resp.text[:300]


def _raise_api_error(resp, provider="API"):
    """从API响应中提取错误信息并抛出异常

    Args:
        resp: requests响应对象
        provider: API提供者名称(str)

    Raises:
        Exception: 包含状态码和错误信息的异常
    """
    err_info = _extract_error_message(resp)
    raise Exception(f"{provider}请求失败({resp.status_code}): {err_info}")


# ==============================================================================
# 多模态工具函数
# ==============================================================================
def _has_image_in_messages(messages):
    """检查消息列表中是否包含图片（多模态内容）

    Args:
        messages: 消息列表(list[dict])

    Returns:
        bool: 是否包含图片

    检测格式:
        OpenAI/智谱AI格式: messages[i]["content"] 是列表且包含 type="image_url" 的元素
    """
    for msg in messages:
        content = msg.get('content', '')
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get('type') == 'image_url':
                    return True
    return False


def build_image_message(text, image_base64, image_mime_type="image/jpeg"):
    """构建包含图片的多模态消息（智谱AI GLM-4V系列格式）

    Args:
        text: 用户文字提问(str)
        image_base64: 图片的Base64编码(str)，不含data:前缀
        image_mime_type: 图片MIME类型(str)，默认image/jpeg

    Returns:
        dict: 可直接加入messages列表的消息对象，格式:
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "请用中文回答。你的问题"},
                    {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
                ]
            }

    注意:
        - 自动在文字前添加"请用中文回答"前缀
        - 图片以data URL格式传递(data:mime;base64,xxx)，智谱AI支持此格式
        - 图片大小限制约2MB(base64编码后约2.7MB)，前端已做自动压缩
    """
    full_text = f"请用中文回答。{text}"
    data_url = f"data:{image_mime_type};base64,{image_base64}"
    return {
        "role": "user",
        "content": [
            {"type": "text", "text": full_text},
            {"type": "image_url", "image_url": {"url": data_url}}
        ]
    }


# ==============================================================================
# 流式输出解析
# ==============================================================================
def _parse_sse_stream(response):
    """解析标准SSE(Server-Sent Events)格式的流式响应

    智谱AI和SiliconFlow均使用OpenAI兼容的SSE格式

    Args:
        response: requests的流式响应对象

    Yields:
        str: 逐个token的文本片段

    SSE格式示例:
        data: {"choices":[{"delta":{"content":"你"}}]}
        data: {"choices":[{"delta":{"content":"好"}}]}
        data: [DONE]
    """
    for line in response.iter_lines(decode_unicode=True):
        if not line or not line.startswith('data:'):
            continue
        data_str = line[5:].strip()
        if data_str == '[DONE]':
            break
        try:
            data = json.loads(data_str)
            delta = data['choices'][0].get('delta', {})
            content = delta.get('content', '')
            if content:
                yield content
        except (json.JSONDecodeError, KeyError, IndexError):
            continue


# ==============================================================================
# 系统提示词获取
# ==============================================================================
def get_system_prompt():
    """获取系统提示词

    Returns:
        str: 系统提示词文本
    """
    return SYSTEM_PROMPT
