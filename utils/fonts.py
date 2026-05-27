"""
字体管理模块 - 处理PDF生成中的中文字体问题
字体优先级：文泉驿微米黑 > NotoSansSC > 阿里妈妈东方大楷 > 系统字体
符号回退：UniFont（覆盖全部Unicode BMP，用于渲染☑☐等特殊符号）
"""
import os
import sys
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

fonts_registered = False
normal_font_name = 'Helvetica'
bold_font_name = 'Helvetica-Bold'

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

_SEARCH_DIRS = [
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'fonts'),
    os.path.join(os.getcwd(), 'static', 'fonts'),
    '/app/static/fonts',
    '/opt/render/project/src/static/fonts',
]

_BUILTIN = [
    ('UniFont', ['unifont-15.0.01.ttf'], False),
    ('WQYMicroHei', ['WenQuanWeiMiHei-1.ttf', 'wqy-microhei.ttc'], True),
    ('NotoSansSC', ['NotoSansSC-Regular.ttf'], True),
    ('AlimamaDongFangDaKai', ['AlimamaDongFangDaKai-Regular.ttf'], False),
]

_SYSTEM = [
    ('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 'WQYMicroHei', 0),
    ('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 'WQYZenHei', 0),
    ('C:\\Windows\\Fonts\\msyh.ttc', 'MicrosoftYaHei', 0),
    ('C:\\Windows\\Fonts\\simhei.ttf', 'SimHei', 0),
    ('C:\\Windows\\Fonts\\simsun.ttc', 'SimSun', 0),
    ('/System/Library/Fonts/PingFang.ttc', 'PingFang', 1),
]


def _is_true_type(path):
    try:
        with open(path, 'rb') as f:
            tag = f.read(4)
        return tag in (b'\x00\x01\x00\x00', b'ttcf') or tag not in (b'OTTO', b'\x4F\x54\x54\x4F')
    except Exception:
        return False


def _find_builtin(name, filenames):
    for d in _SEARCH_DIRS:
        for fn in filenames:
            p = os.path.join(d, fn)
            if os.path.exists(p) and _is_true_type(p):
                return p
    return None


def _try_register(name, path, subfont=0, need_cjk=False):
    try:
        pdfmetrics.registerFont(TTFont(name, path, subfontIndex=subfont))
        if need_cjk:
            font = pdfmetrics.getFont(name)
            if 0x4E2D not in font.face.charToGlyph:
                return False
        print(f"[OK] Registered {name}: {path}")
        return True
    except Exception as e:
        print(f"[FAIL] {name} {path}: {e}")
        return False


def register_chinese_font():
    global fonts_registered, normal_font_name, bold_font_name
    if fonts_registered:
        return True

    try:
        for name, filenames, need_cjk in _BUILTIN:
            path = _find_builtin(name, filenames)
            if path and _try_register(name, path, subfont=0, need_cjk=need_cjk):
                if name != 'UniFont':
                    normal_font_name = name
                    bold_font_name = name
                    fonts_registered = True
                    return True

        for path, name, subfont in _SYSTEM:
            if os.path.exists(path) and _try_register(name, path, subfont=subfont):
                normal_font_name = name
                bold_font_name = name
                fonts_registered = True
                return True

        print("[WARN] No Chinese font available, using Helvetica fallback")
        normal_font_name = 'Helvetica'
        bold_font_name = 'Helvetica-Bold'
        fonts_registered = True
        return False

    except Exception as e:
        print(f"[ERROR] Font registration: {e}")
        normal_font_name = 'Helvetica'
        bold_font_name = 'Helvetica-Bold'
        fonts_registered = True
        return False


def get_chinese_font_name():
    if not fonts_registered:
        register_chinese_font()
    return normal_font_name


def get_chinese_bold_font_name():
    if not fonts_registered:
        register_chinese_font()
    return bold_font_name


if not fonts_registered:
    register_chinese_font()
