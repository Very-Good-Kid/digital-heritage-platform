"""
文档解析器 - 从上传的文件中提取纯文本内容
支持格式: PDF, TXT, Markdown, DOCX
"""
import io


def parse_pdf(file_data):
    """从PDF二进制数据中提取文本
    
    Args:
        file_data: PDF文件的二进制内容(bytes)
    
    Returns:
        str: 提取的纯文本内容
    
    Note:
        使用 PyPDF2 逐页提取文本，适用于文字型PDF
        扫描件/图片型PDF无法提取，需要OCR（暂不支持）
    """
    from PyPDF2 import PdfReader
    text_parts = []
    reader = PdfReader(io.BytesIO(file_data))
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
    return '\n\n'.join(text_parts)


def parse_txt(file_data):
    """从TXT文件二进制数据中提取文本
    
    Args:
        file_data: TXT文件的二进制内容(bytes)
    
    Returns:
        str: 文本内容，尝试UTF-8解码，失败则用GBK
    """
    try:
        return file_data.decode('utf-8')
    except UnicodeDecodeError:
        return file_data.decode('gbk', errors='ignore')


def parse_markdown(file_data):
    """从Markdown文件二进制数据中提取文本
    
    Args:
        file_data: Markdown文件的二进制内容(bytes)
    
    Returns:
        str: Markdown原始文本（Markdown本身是文本格式，直接返回）
    """
    return parse_txt(file_data)


def parse_docx(file_data):
    """从DOCX文件二进制数据中提取文本
    
    Args:
        file_data: DOCX文件的二进制内容(bytes)
    
    Returns:
        str: 提取的纯文本内容（按段落拼接）
    """
    from docx import Document
    doc = Document(io.BytesIO(file_data))
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
    return '\n\n'.join(paragraphs)


# 支持的文件类型及其对应的解析函数
PARSERS = {
    'pdf': parse_pdf,
    'txt': parse_txt,
    'md': parse_markdown,
    'docx': parse_docx,
}


def parse_document(file_data, file_type):
    """根据文件类型自动选择解析器提取文本
    
    Args:
        file_data: 文件的二进制内容(bytes)
        file_type: 文件类型后缀(str)，如 'pdf', 'txt', 'md', 'docx'
    
    Returns:
        str: 提取的纯文本内容
    
    Raises:
        ValueError: 不支持的文件类型
    """
    file_type = file_type.lower().strip('.')
    parser = PARSERS.get(file_type)
    if not parser:
        raise ValueError(f"不支持的文件类型: {file_type}，支持类型: {list(PARSERS.keys())}")
    return parser(file_data)


def get_supported_types():
    """获取支持的文件类型列表
    
    Returns:
        list: 支持的文件类型后缀列表
    """
    return list(PARSERS.keys())
