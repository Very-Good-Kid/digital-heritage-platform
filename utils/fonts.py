"""
字体管理模块 - 修复版 V4 (针对 Render 免费版优化)
处理 PDF 生成中的中文字体问题
支持 Windows、Linux (Render)、macOS 等多个平台
"""
import os
import sys
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFont
import urllib.request
import tempfile
import requests

# 字体注册状态
fonts_registered = False
normal_font_name = 'Helvetica'
bold_font_name = 'Helvetica-Bold'

# Windows控制台兼容性：设置UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def register_chinese_font():
    """
    注册中文字体
    支持多个平台和字体源
    """
    global fonts_registered, normal_font_name, bold_font_name

    if fonts_registered:
        return True

    try:
        # 1. 尝试使用系统字体 - 按优先级排序
        font_paths = [
            # Linux (Render) 优先使用文泉驿
            ('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 'WQYMicroHei', 'WQYMicroHei-Bold', 0),
            ('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 'WQYMicroHei', 'WQYMicroHei-Bold', 1),
            ('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 'WQYZenHei', 'WQYZenHei-Bold', 0),
            ('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 'WQYZenHei', 'WQYZenHei-Bold', 1),

            # 尝试其他常见字体位置
            ('/usr/share/fonts/truetype/wqy/wqy-microhei.ttf', 'WQYMicroHei', 'WQYMicroHei-Bold'),
            ('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttf', 'WQYZenHei', 'WQYZenHei-Bold'),

            # Windows 字体
            ('C:\\Windows\\Fonts\\msyh.ttc', 'MicrosoftYaHei', 'MicrosoftYaHei-Bold', 0),
            ('C:\\Windows\\Fonts\\simhei.ttf', 'SimHei', 'SimHei-Bold'),
            ('C:\\Windows\\Fonts\\simsun.ttc', 'SimSun', 'SimSun-Bold', 0),

            # macOS 字体
            ('/System/Library/Fonts/PingFang.ttc', 'PingFang', 'PingFang-Bold', 1),
            ('/System/Library/Fonts/STHeiti Light.ttc', 'STHeiti', 'STHeiti-Bold', 0),

            # Linux 通用字体位置
            ('/usr/share/fonts/truetype/chinese/SimHei.ttf', 'SimHei', 'SimHei-Bold'),
            ('/usr/share/fonts/chinese/SimHei.ttf', 'SimHei', 'SimHei-Bold'),
            ('/usr/share/fonts/truetype/SimHei.ttf', 'SimHei', 'SimHei-Bold'),
        ]

        for font_info in font_paths:
            try:
                if len(font_info) == 3:
                    path, normal, bold = font_info
                    subfont = 0
                else:
                    path, normal, bold, subfont = font_info

                if os.path.exists(path):
                    pdfmetrics.registerFont(TTFont(normal, path, subfontIndex=subfont))
                    # 尝试注册粗体，如果失败则使用常规字体
                    try:
                        pdfmetrics.registerFont(TTFont(bold, path, subfontIndex=subfont))
                    except:
                        bold = normal  # 使用常规字体作为粗体

                    normal_font_name = normal
                    bold_font_name = bold
                    fonts_registered = True
                    print(f"[OK] Successfully registered system font: {path}")
                    return True
            except Exception as e:
                print(f"[FAIL] Failed to register font {font_info[0]}: {e}")
                continue

        # 2. 如果系统字体不可用，尝试下载开源中文字体
        print("[WARN] No system Chinese font found, attempting to download open-source font...")

        # 尝试多个可靠的下载源
        font_urls = [
            # 方案1: 使用 Google Fonts 官方 CDN (最可靠)
            "https://fonts.gstatic.com/s/notosanssc/v36/k3kXo84MPvpLmixcA63oeALZTYKLgASIOQ.woff2",

            # 方案2: 使用 GitHub releases (备用)
            "https://github.com/notofonts/noto-cjk/releases/download/Sans2.004/09_NotoSansCJK-SC.zip",

            # 方案3: 使用 jsDelivr CDN (备用)
            "https://cdn.jsdelivr.net/gh/notofonts/noto-cjk@main/Sans/OTF/SimplifiedChinese/NotoSansSC-Regular.otf",
        ]

        for url in font_urls:
            try:
                print(f"Attempting to download from: {url}")

                if url.endswith('.zip'):
                    # 处理 ZIP 文件
                    font_name = download_and_register_font_from_zip(url)
                else:
                    # 处理直接字体文件
                    font_name = download_and_register_font(url, 'DownloadedChinese')

                if font_name:
                    normal_font_name = font_name
                    bold_font_name = font_name
                    fonts_registered = True
                    print(f"[OK] Successfully downloaded and registered font: {font_name}")
                    return True
            except Exception as e:
                print(f"[FAIL] Failed to download from {url}: {e}")
                continue

        # 3. 如果所有方法都失败，使用默认字体并给出警告
        print("[WARN] WARNING: No Chinese font available!")
        print("PDF will use default fonts and may not display Chinese characters correctly.")
        print("To fix this issue, ensure Chinese fonts are installed on the server.")
        print("For Render deployment:")
        print("  1. Open Render Shell")
        print("  2. Run: apt-get update && apt-get install -y fonts-wqy-microhei fonts-wqy-zenhei")
        print("  3. Run: fc-cache -fv")
        print("  4. Trigger manual deploy")

        normal_font_name = 'Helvetica'
        bold_font_name = 'Helvetica-Bold'
        fonts_registered = True  # 标记为已注册，避免重复尝试
        return False

    except Exception as e:
        print(f"[ERROR] Error registering Chinese font: {e}")
        import traceback
        traceback.print_exc()
        normal_font_name = 'Helvetica'
        bold_font_name = 'Helvetica-Bold'
        fonts_registered = True
        return False


def download_and_register_font(url, font_name='DownloadedChinese'):
    """
    下载并注册字体文件（支持 TTF/TTC/WOFF2 格式）
    """
    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()

        # 确定文件扩展名
        if url.endswith('.ttf'):
            ext = '.ttf'
        elif url.endswith('.ttc'):
            ext = '.ttc'
        elif url.endswith('.otf'):
            ext = '.otf'
        elif url.endswith('.woff2'):
            ext = '.woff2'
        else:
            ext = '.ttf'  # 默认

        # 下载字体文件
        print(f"Downloading font from {url}...")
        font_path = os.path.join(temp_dir, f'font{ext}')

        # 使用 requests 库下载（更可靠）
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()

        with open(font_path, 'wb') as f:
            f.write(response.content)

        if os.path.exists(font_path):
            file_size = os.path.getsize(font_path)
            print(f"Font downloaded successfully: {font_path}")
            print(f"File size: {file_size} bytes")

            # 验证文件大小（字体文件应该至少有 100KB）
            if file_size < 100 * 1024:
                print(f"[WARN] Downloaded file is too small ({file_size} bytes), may be invalid")
                return None

            # 如果是 WOFF2 格式，需要转换为 TTF
            if ext == '.woff2':
                print("Converting WOFF2 to TTF format...")
                try:
                    from fontTools.ttLib import TTFont
                    from io import BytesIO

                    with open(font_path, 'rb') as f:
                        font_data = BytesIO(f.read())

                    # 尝试直接加载 WOFF2
                    try:
                        font = TTFont(font_data)
                        ttf_path = os.path.join(temp_dir, 'font.ttf')
                        font.save(ttf_path)
                        font_path = ttf_path
                        ext = '.ttf'
                        print(f"Converted to TTF: {font_path}")
                    except:
                        print("[WARN] Cannot convert WOFF2, trying to use it directly...")
                except ImportError:
                    print("[WARN] fontTools not available, trying to use WOFF2 directly...")
                except Exception as e:
                    print(f"[WARN] WOFF2 conversion failed: {e}, trying to use it directly...")

            # 注册字体
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                return font_name
            except Exception as e:
                print(f"[WARN] Failed to register font as TTF: {e}")
                print("Font may be in unsupported format")
                return None

        return None

    except Exception as e:
        print(f"Failed to download font: {e}")
        return None


def download_and_register_font_from_zip(url):
    """
    从ZIP文件下载并注册字体
    """
    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()

        # 下载字体文件
        print(f"Downloading font from {url}...")
        zip_path = os.path.join(temp_dir, 'font.zip')

        # 使用 requests 库下载（更可靠）
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()

        with open(zip_path, 'wb') as f:
            f.write(response.content)

        # 解压字体文件
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # 查找中文字体文件
        font_file = None
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.endswith('.ttf') or file.endswith('.ttc') or file.endswith('.otf'):
                    # 优先选择简体中文字体
                    if 'SC' in file or 'Simplified' in file or 'CN' in file or 'zh' in file.lower():
                        font_file = os.path.join(root, file)
                        break
                    elif not font_file:
                        font_file = os.path.join(root, file)

        if font_file and os.path.exists(font_file):
            file_size = os.path.getsize(font_file)
            print(f"Found font file: {font_file}")
            print(f"File size: {file_size} bytes")

            # 验证文件大小
            if file_size < 100 * 1024:
                print(f"[WARN] Font file is too small, may be invalid")
                return None

            font_name = 'DownloadedChinese'
            pdfmetrics.registerFont(TTFont(font_name, font_file))
            return font_name

        return None

    except Exception as e:
        print(f"Failed to download font from zip: {e}")
        return None


def get_chinese_font_name():
    """获取中文字体名称"""
    if not fonts_registered:
        register_chinese_font()
    return normal_font_name


def get_chinese_bold_font_name():
    """获取中文字体名称（粗体）"""
    if not fonts_registered:
        register_chinese_font()
    return bold_font_name


# 自动注册字体（在模块导入时）
if not fonts_registered:
    register_chinese_font()
