"""
文本分块器 - 将长文本切分为适合向量化的短文本块
RAG的核心步骤之一：合理的分块策略直接影响检索效果
"""


def split_text(text, chunk_size=500, chunk_overlap=50):
    """将长文本切分为固定长度的文本块，相邻块之间有重叠
    
    Args:
        text: 待切分的纯文本(str)
        chunk_size: 每个文本块的最大字符数(int)，默认500
            - 500字适合中文知识库，既能保留语义完整性又不会太长
        chunk_overlap: 相邻块之间的重叠字符数(int)，默认50
            - 重叠可以避免关键信息被截断在块边界处
    
    Returns:
        list[str]: 切分后的文本块列表
    
    分块策略说明:
        1. 首先按段落(双换行符)分割文本，保留语义完整性
        2. 将短段落合并，直到接近chunk_size
        3. 如果单个段落超过chunk_size，再按字符数硬切分
        4. 相邻块之间保留overlap字符的重叠，减少信息丢失
    """
    if not text or not text.strip():
        return []

    # 按段落分割
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

    chunks = []
    current_chunk = ""

    for para in paragraphs:
        # 如果当前块加上这个段落不超过限制，则合并
        if len(current_chunk) + len(para) + 2 <= chunk_size:
            if current_chunk:
                current_chunk += '\n\n' + para
            else:
                current_chunk = para
        else:
            # 当前块已满，先保存
            if current_chunk:
                chunks.append(current_chunk)
            # 如果段落本身超过chunk_size，需要硬切分
            if len(para) > chunk_size:
                # 先把current_chunk中不足一个chunk的部分处理完
                sub_chunks = _hard_split(para, chunk_size, chunk_overlap)
                chunks.extend(sub_chunks)
                # 最后一个子块作为新的current_chunk继续合并
                if chunks and chunk_overlap > 0:
                    current_chunk = chunks[-1][-chunk_overlap:] if len(chunks[-1]) > chunk_overlap else chunks[-1]
                else:
                    current_chunk = ""
            else:
                current_chunk = para

    # 不要忘记最后一个块
    if current_chunk:
        chunks.append(current_chunk)

    # 去除过短的块（可能是空块或仅含标点）
    chunks = [c for c in chunks if len(c.strip()) >= 10]

    return chunks


def _hard_split(text, chunk_size, chunk_overlap):
    """对超长段落进行硬切分（按字符数强制分割）
    
    Args:
        text: 超长文本(str)
        chunk_size: 每块最大字符数(int)
        chunk_overlap: 重叠字符数(int)
    
    Returns:
        list[str]: 切分后的文本块列表
    
    示例(chunk_size=10, overlap=3):
        "ABCDEFGHIJKLMNO" -> ["ABCDEFGHIJ", "HIJKLMNO"]  (HIJ为重叠部分)
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        # 下一个块的起始位置后退overlap个字符，形成重叠
        start = end - chunk_overlap
        # 防止overlap过大导致无限循环
        if start <= end - chunk_size:
            start = end
    return chunks
