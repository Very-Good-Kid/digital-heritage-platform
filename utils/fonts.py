"""
字体管理模块 - 修复版 V2
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
        # 1. 尝试使用系统字体 - 按优先级排序
        font_paths = [
            # Linux (Render) 优先使用文泉驿（更可靠）
            ('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 'WQYMicroHei', 'WQYMicroHei-Bold', 0),
            ('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 'WQYMicroHei', 'WQYMicroHei-Bold', 1),
            ('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 'WQYZenHei', 'WQYZenHei-Bold', 0),
            ('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 'WQYZenHei', 'WQYZenHei-Bold', 1),

            # 尝试 Noto Sans CJK（如果安装）
            ('/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc', 'NotoSansCJK', 'NotoSansCJK-Bold', 0),
            ('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', 'NotoSansCJK', 'NotoSansCJK-Bold', 0),

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

        # 2. 如果系统字体不可用，尝试下载开源中文字体（使用 TTF 格式）
        print("[WARN] No system Chinese font found, attempting to download open-source font...")

        try:
            # 使用文泉驿微米黑 TTF 版本（更可靠的下载源）
            font_url = "https://github.com/googlefonts/wqy-microhei/raw/master/wqy-microhei.ttc"
            font_name = download_and_register_font(font_url, 'WQYMicroHei')

            if font_name:
                normal_font_name = font_name
                bold_font_name = font_name  # 使用同一字体
                fonts_registered = True
                print(f"[OK] Successfully downloaded and registered font: {font_name}")
                return True
        except Exception as e:
            print(f"[FAIL] Failed to download WQY MicroHei: {e}")

        # 3. 尝试备用下载源（使用 TTF 格式）
        try:
            # 使用 Noto Sans SC TTF 版本
            font_url = "https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansSC-Regular.otf"
            # 转换为 TTF 的下载链接
            font_url = "https://github.com/notofonts/noto-cjk/raw/main/Sans/TTF/NotoSansSC-Regular.ttf"
            font_name = download_and_register_font(font_url, 'NotoSansSC')

            if font_name:
                normal_font_name = font_name
                bold_font_name = font_name
                fonts_registered = True
                print(f"[OK] Successfully downloaded and registered font: {font_name}")
                return True
        except Exception as e:
            print(f"[FAIL] Failed to download Noto Sans SC: {e}")

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


def download_and_register_font(url, font_name='DownloadedChinese'):
    """
    下载并注册字体文件（支持 TTF/TTC 格式）
    """
    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()

        # 确定文件扩展名
        if url.endswith('.ttf'):
            ext = '.ttf'
        elif url.endswith('.ttc'):
            ext = '.ttc'
        else:
            ext = '.ttf'  # 默认

        # 下载字体文件
        print(f"Downloading font from {url}...")
        font_path = os.path.join(temp_dir, f'font{ext}')
        urllib.request.urlretrieve(url, font_path)

        # 设置超时和重试
        import socket
        socket.setdefaulttimeout(30)

        if os.path.exists(font_path):
            print(f"Font downloaded successfully: {font_path}")
            print(f"File size: {os.path.getsize(font_path)} bytes")

            # 注册字体
            pdfmetrics.registerFont(TTFont(font_name, font_path))
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
