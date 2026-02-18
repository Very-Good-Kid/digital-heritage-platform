#!/usr/bin/env python3
"""
运行时字体安装脚本 - Render 免费版专用
在应用运行时安装中文字体，避免构建阶段的权限限制
"""
import os
import sys
import subprocess
import tempfile
import requests
from pathlib import Path

def install_system_fonts():
    """尝试安装系统字体（需要root权限）"""
    try:
        print("[INFO] Attempting to install system fonts...")
        result = subprocess.run(
            ['apt-get', 'update'],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            print("[OK] apt-get update successful")

            result = subprocess.run(
                ['apt-get', 'install', '-y', 'fonts-wqy-microhei', 'fonts-wqy-zenhei'],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                print("[OK] System fonts installed successfully")

                # 更新字体缓存
                subprocess.run(['fc-cache', '-fv'], capture_output=True, timeout=60)
                print("[OK] Font cache updated")
                return True

        print("[WARN] System font installation failed (expected on Render free tier)")
        return False

    except PermissionError:
        print("[WARN] No root permissions, skipping system font installation")
        return False
    except Exception as e:
        print(f"[WARN] System font installation error: {e}")
        return False


def download_font_to_temp():
    """下载字体到临时目录"""
    try:
        print("[INFO] Downloading Chinese font to temporary directory...")

        # 创建临时字体目录
        font_dir = Path(tempfile.gettempdir()) / 'fonts'
        font_dir.mkdir(exist_ok=True)

        # 使用 Google Fonts 的可靠 CDN
        font_url = "https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/OTF/SimplifiedChinese/NotoSansSC-Regular.otf"
        font_path = font_dir / 'NotoSansSC.otf'

        # 如果文件已存在且大小合理，直接使用
        if font_path.exists() and font_path.stat().st_size > 100000:
            print(f"[OK] Font already exists: {font_path}")
            return str(font_path)

        # 下载字体
        print(f"[INFO] Downloading from: {font_url}")
        response = requests.get(font_url, timeout=60)
        response.raise_for_status()

        # 保存字体
        font_path.write_bytes(response.content)
        file_size = font_path.stat().st_size

        print(f"[OK] Font downloaded: {font_path} ({file_size} bytes)")

        if file_size < 100000:
            print("[WARN] Downloaded font file seems too small")
            return None

        return str(font_path)

    except Exception as e:
        print(f"[ERROR] Font download failed: {e}")
        return None


def setup_font_environment():
    """设置字体环境"""
    print("[INFO] Setting up font environment...")

    # 1. 尝试安装系统字体
    system_fonts_installed = install_system_fonts()

    if system_fonts_installed:
        print("[OK] Using system fonts")
        return True

    # 2. 下载字体到临时目录
    font_path = download_font_to_temp()

    if font_path:
        print(f"[OK] Using downloaded font: {font_path}")
        # 设置环境变量，让其他模块知道字体位置
        os.environ['DOWNLOADED_FONT_PATH'] = font_path
        return True

    print("[WARN] No font available, will use fallback")
    return False


def verify_font_availability():
    """验证字体是否可用"""
    font_paths = [
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        os.environ.get('DOWNLOADED_FONT_PATH', '')
    ]

    for path in font_paths:
        if path and os.path.exists(path):
            print(f"[OK] Font available: {path}")
            return True

    print("[WARN] No Chinese font available")
    return False


if __name__ == '__main__':
    print("=" * 60)
    print("Font Setup for Render Free Tier")
    print("=" * 60)

    # 设置字体环境
    success = setup_font_environment()

    # 验证字体
    verify_font_availability()

    print("=" * 60)
    if success:
        print("Font setup completed successfully")
    else:
        print("Font setup completed with warnings (using fallback fonts)")
    print("=" * 60)

    sys.exit(0 if success else 1)
