"""
字体管理模块 - 修复版
处理 PDF 生成中的中文字体问题
支持 Windows、Linux (Render)、macOS 等多个平台
"""
import os
import sys
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import urllib.request
import tempfile

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
        # 1. 尝试使用系统字体
        font_paths = [
            # Windows 字体
            ('C:\\Windows\\Fonts\\simhei.ttf', 'SimHei', 'SimHei-Bold'),
            ('C:\\Windows\\Fonts\\msyh.ttc', 'MicrosoftYaHei', 'MicrosoftYaHei-Bold', 0),
            ('C:\\Windows\\Fonts\\simsun.ttc', 'SimSun', 'SimSun-Bold', 0),

            # Linux (Render) 字体
            ('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 'WQYZenHei', 'WQYZenHei-Bold', 0),
            ('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 'WQYMicroHei', 'WQYMicroHei-Bold', 0),
            ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 'DejaVuSans', 'DejaVuSans-Bold'),
            ('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', 'NotoSansCJK', 'NotoSansCJK-Bold', 0),
            ('/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc', 'NotoSansCJK', 'NotoSansCJK-Bold', 0),

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
                    pdfmetrics.registerFont(TTFont(bold, path, subfontIndex=subfont))
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

        try:
            # 使用文泉驿微米黑（开源中文字体）
            font_url = "https://github.com/googlefonts/noto-cjk/releases/download/Sans2.004/02_NotoSansCJK-OTC.zip"
            font_name = download_and_register_font(font_url)

            if font_name:
                normal_font_name = font_name
                bold_font_name = font_name  # 使用同一字体
                fonts_registered = True
                print(f"[OK] Successfully downloaded and registered font: {font_name}")
                return True
        except Exception as e:
            print(f"[FAIL] Failed to download font: {e}")

        # 3. 最后尝试使用reportlab内置的中文字体支持
        print("[WARN] Attempting to use reportlab built-in font support...")

        try:
            # 某些reportlab版本内置了中文字体
            pdfmetrics.registerFont(TTFont('STSong-Light', '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 0))
            normal_font_name = 'STSong-Light'
            bold_font_name = 'STSong-Light'
            fonts_registered = True
            print("[OK] Using built-in font support")
            return True
        except:
            pass

        # 4. 如果所有方法都失败，使用默认字体并给出警告
        print("[WARN] WARNING: No Chinese font available!")
        print("PDF will use default fonts and may not display Chinese characters correctly.")
        print("To fix this issue, ensure Chinese fonts are installed on the server.")
        print("For Render deployment, add build command to install fonts:")
        print("  Build Command: apt-get update && apt-get install -y fonts-wqy-microhei fonts-wqy-zenhei")

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


def download_and_register_font(url):
    """
    下载并注册字体文件
    """
    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()

        # 下载字体文件
        print(f"Downloading font from {url}...")
        zip_path = os.path.join(temp_dir, 'font.zip')
        urllib.request.urlretrieve(url, zip_path)

        # 解压字体文件
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # 查找中文字体文件
        font_file = None
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.endswith('.ttf') or file.endswith('.ttc'):
                    # 优先选择简体中文字体
                    if 'SC' in file or 'Simplified' in file or 'CN' in file:
                        font_file = os.path.join(root, file)
                        break
                    elif not font_file:
                        font_file = os.path.join(root, file)

        if font_file and os.path.exists(font_file):
            font_name = 'DownloadedChinese'
            pdfmetrics.registerFont(TTFont(font_name, font_file))
            return font_name

        return None

    except Exception as e:
        print(f"Failed to download font: {e}")
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
