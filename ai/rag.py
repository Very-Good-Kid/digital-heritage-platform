"""
RAG 核心逻辑 - 检索增强生成
流程: 用户提问 → 向量检索知识库 → (可选)网络搜索补充 → 组装Prompt → LLM生成回答
这是整个AI对话功能的核心模块
"""
import json
import math
from flask import current_app
from ai.embedding import embed_single, cosine_similarity
from ai.llm import chat, get_system_prompt, build_image_message
from ai.search import search_web, format_search_results
from models import db, KnowledgeChunk, KnowledgeFile, ChatMessage


def retrieve_knowledge(query, top_k=5, similarity_threshold=0.3):
    """从知识库中检索与问题最相关的文本块
    
    Args:
        query: 用户提问(str)
        top_k: 返回最相关的K个结果(int)，默认5
        similarity_threshold: 相似度阈值(float)，低于此值的结果被过滤，默认0.3
    
    Returns:
        list[dict]: 检索结果列表，每项包含:
            - content: 文本内容
            - source: 来源文件名
            - similarity: 与问题的相似度得分
            - chunk_id: 文本块ID
    
    检索流程:
        1. 检查知识库是否有数据，无数据则直接返回空列表
        2. 将用户问题转化为向量
        3. 遍历知识库中所有文本块的向量
        4. 计算余弦相似度
        5. 按相似度降序排列，返回top_k个结果
    """
    # 先检查知识库是否有数据，避免无意义地调用embedding API
    try:
        chunk_count = KnowledgeChunk.query.filter(KnowledgeChunk.embedding.isnot(None)).count()
        if chunk_count == 0:
            return []
    except Exception:
        # 数据库表可能尚未创建，返回空列表
        return []

    # 将问题向量化（可能因embedding服务不可用而失败，需捕获异常）
    try:
        query_embedding = embed_single(query)
    except Exception as e:
        print(f"[WARN] Embedding失败，跳过知识库检索: {e}")
        return []

    # 获取所有有向量的知识库文本块
    try:
        chunks = KnowledgeChunk.query.filter(KnowledgeChunk.embedding.isnot(None)).all()
    except Exception as e:
        db.session.rollback()
        print(f"[WARN] 查询知识库失败: {e}")
        return []

    if not chunks:
        return []

    # 3. 计算每个块与问题的相似度
    scored_chunks = []
    for chunk in chunks:
        try:
            chunk_embedding = json.loads(chunk.embedding)
            similarity = cosine_similarity(query_embedding, chunk_embedding)
            if similarity >= similarity_threshold:
                # 获取来源文件名
                source_file = KnowledgeFile.query.get(chunk.file_id)
                source_name = source_file.filename if source_file else "未知来源"
                scored_chunks.append({
                    'content': chunk.content,
                    'source': source_name,
                    'similarity': round(similarity, 4),
                    'chunk_id': chunk.id
                })
        except (json.JSONDecodeError, TypeError):
            continue

    # 4. 按相似度降序排列，取top_k
    scored_chunks.sort(key=lambda x: x['similarity'], reverse=True)
    return scored_chunks[:top_k]


def format_knowledge_context(chunks):
    """将检索到的知识库片段格式化为文本，用于拼接到LLM的上下文中
    
    Args:
        chunks: retrieve_knowledge() 返回的检索结果列表
    
    Returns:
        str: 格式化后的知识库上下文文本
    
    示例输出:
        【知识库参考资料】
        [来源: 法律法规.pdf | 相关度: 0.85]
        根据《民法典》第一千一百二十二条...
        
        [来源: 继承指南.txt | 相关度: 0.72]
        微信账号继承需要提供...
    """
    if not chunks:
        return ""

    parts = ["【知识库相关资料】"]
    for chunk in chunks:
        parts.append(f"[相关度: {chunk['similarity']}]")
        parts.append(chunk['content'])
        parts.append("")
    return '\n'.join(parts)


def build_messages(query, knowledge_context="", search_context="", history=None, image_base64=None, image_mime_type="image/jpeg"):
    """组装发给LLM的完整消息列表
    
    Args:
        query: 用户当前提问(str)
        knowledge_context: 知识库检索结果文本(str)，由 format_knowledge_context() 生成
        search_context: 网络搜索结果文本(str)，由 format_search_results() 生成
        history: 历史对话列表(list[dict])，格式: [{"role": "user/assistant", "content": "..."}]
        image_base64: 图片的Base64编码(str)，不含data:前缀。为None时表示纯文本对话
        image_mime_type: 图片MIME类型(str)，默认image/jpeg
    
    Returns:
        list[dict]: 完整的消息列表，可直接传给 llm.chat()
    
    消息结构:
        1. system: 系统提示词 + 知识库上下文 + 搜索上下文
        2. 历史对话（最近N轮）
        3. user: 当前问题（如果有图片则为多模态消息）
    
    视觉问答说明:
        当 image_base64 不为None时，当前用户消息会包含图片，
        使用OpenAI兼容的多模态格式，智谱AI和Ollama均支持
    """
    # 组装系统提示
    system_content = get_system_prompt()
    if knowledge_context:
        system_content += "\n\n" + knowledge_context
    if search_context:
        system_content += "\n\n" + search_context

    # 限制系统提示词长度，避免Ollama等模型因超长输入返回400
    if len(system_content) > 8000:
        system_content = system_content[:8000] + "\n\n[注意：知识库内容过长，已截断]"

    messages = [{"role": "system", "content": system_content}]

    # 视觉问答时不发送历史对话（多模态content为数组，与历史纯文本content混排
    # 会导致智谱AI等返回400 Bad Request）
    if not image_base64 and history:
        recent_history = history[-20:]
        messages.extend(recent_history)

    # 添加当前问题（区分纯文本和带图片两种情况）
    if image_base64:
        # 多模态：图片+文字
        user_msg = build_image_message(query, image_base64, image_mime_type)
    else:
        # 纯文本
        user_msg = {"role": "user", "content": query}
    messages.append(user_msg)

    return messages


def rag_query(query, user_id=None, session_id=None, enable_search=True, stream=False, image_base64=None, image_mime_type="image/jpeg"):
    """RAG 完整流程：检索 + 增强 + 生成
    
    Args:
        query: 用户提问(str)
        user_id: 用户ID(int)，用于保存对话记录
        session_id: 会话ID(str)，用于关联对话记录
        enable_search: 是否启用网络搜索补充(bool)，默认True
        stream: 是否流式输出(bool)，默认False
        image_base64: 图片Base64编码(str)，不含data:前缀。None表示纯文本
        image_mime_type: 图片MIME类型(str)，默认image/jpeg
    
    Returns:
        如果 stream=False: 返回 dict，包含:
            - answer: AI回答文本
            - sources: 引用的知识库来源列表
            - search_used: 是否使用了网络搜索
        如果 stream=True: 返回生成器，逐token产出文本片段
            （注意：流式模式下不保存对话记录，需在流结束后调用save_chat_message）
    
    完整流程:
        1. 知识库向量检索 → 获取最相关的文本片段
        2. (可选) 网络搜索 → 补充知识库未覆盖的信息
        3. 组装Prompt → 将检索结果和搜索结果拼入上下文（含图片则为多模态）
        4. 调用LLM → 生成回答
        5. 保存对话记录 → 存入数据库
    """
    # ① 知识库检索（仅对文字部分做检索，不检索图片）
    knowledge_chunks = retrieve_knowledge(query)
    knowledge_context = format_knowledge_context(knowledge_chunks)

    # ② 网络搜索（可选，仅当无图片且知识库无结果时）
    search_context = ""
    search_used = False
    if enable_search and not knowledge_chunks and not image_base64:
        # 有图片时不做网络搜索，图片本身已提供足够上下文
        search_results = search_web(query)
        search_context = format_search_results(search_results)
        search_used = bool(search_results)

    # ③ 获取历史对话
    history = []
    if user_id and session_id:
        history = get_chat_history(user_id, session_id)

    # ④ 组装消息（可能包含图片）
    messages = build_messages(query, knowledge_context, search_context, history,
                              image_base64=image_base64, image_mime_type=image_mime_type)

    # ⑤ 调用LLM生成回答
    if stream:
        # 流式模式：返回生成器
        return chat(messages, stream=True)
    else:
        # 非流式模式：获取完整回答
        answer = chat(messages, stream=False)

        # ⑥ 保存对话记录
        sources = [chunk['source'] for chunk in knowledge_chunks]
        if user_id and session_id:
            # 保存用户消息时标注是否有图片
            user_content = query
            if image_base64:
                user_content = f"[图片问答] {query}"
            save_chat_message(user_id, session_id, 'user', user_content)
            save_chat_message(user_id, session_id, 'assistant', answer,
                              sources=json.dumps(sources, ensure_ascii=False))

        return {
            'answer': answer,
            'sources': sources,
            'search_used': search_used
        }


def get_chat_history(user_id, session_id, limit=20):
    """获取指定会话的最近对话历史
    
    Args:
        user_id: 用户ID(int)
        session_id: 会话ID(str)
        limit: 最多返回的消息条数(int)，默认20（即10轮对话）
    
    Returns:
        list[dict]: 消息列表，格式: [{"role": "user/assistant", "content": "..."}]
    """
    try:
        messages = ChatMessage.query.filter_by(
            user_id=user_id,
            session_id=session_id
        ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
        messages.reverse()
        return [{'role': msg.role, 'content': msg.content} for msg in messages]
    except Exception as e:
        db.session.rollback()
        print(f"[WARN] 获取对话历史失败: {e}")
        return []


def save_chat_message(user_id, session_id, role, content, sources=None):
    """保存一条对话消息到数据库
    
    Args:
        user_id: 用户ID(int)
        session_id: 会话ID(str)
        role: 消息角色(str)，'user' 或 'assistant'
        content: 消息内容(str)
        sources: 引用的知识库来源(str/JSON)，可选
    
    Note:
        对话记录保存失败不应阻断AI对话，因此异常仅打印警告
        Neon休眠后首次写入可能失败(SSL connection closed)，
        自动重试最多3次，每次重试前关闭旧连接重新获取
    """
    for attempt in range(3):
        try:
            msg = ChatMessage(
                user_id=user_id,
                session_id=session_id,
                role=role,
                content=content,
                sources=sources
            )
            db.session.add(msg)
            db.session.commit()
            return
        except Exception as e:
            db.session.rollback()
            if attempt < 2:
                try:
                    db.session.close()
                    db.get_engine(current_app._get_current_object()).dispose()
                except:
                    pass
                import time
                time.sleep(2 * (attempt + 1))
                continue
            print(f"[WARN] 保存对话记录失败(已重试3次): {e}")
