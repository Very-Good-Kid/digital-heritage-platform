#!/bin/bash

# 字体安装脚本 - 用于 Render Shell
# 手动安装中文字体以支持 PDF 生成

echo "========================================="
echo "  中文字体安装脚本"
echo "========================================="
echo ""

# 更新包列表
echo "[1/4] 更新包列表..."
apt-get update

# 安装中文字体
echo ""
echo "[2/4] 安装中文字体..."
apt-get install -y fonts-wqy-microhei fonts-wqy-zenhei fonts-wqy-microhei-hei

# 验证安装
echo ""
echo "[3/4] 验证字体安装..."
if [ -f "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc" ]; then
    echo "✓ wqy-microhei 已安装"
    ls -lh /usr/share/fonts/truetype/wqy/wqy-microhei.ttc
else
    echo "✗ wqy-microhei 未找到"
fi

if [ -f "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc" ]; then
    echo "✓ wqy-zenhei 已安装"
    ls -lh /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc
else
    echo "✗ wqy-zenhei 未找到"
fi

# 刷新字体缓存
echo ""
echo "[4/4] 刷新字体缓存..."
fc-cache -fv

# 列出所有中文字体
echo ""
echo "========================================="
echo "  已安装的中文字体："
echo "========================================="
fc-list | grep -i "wqy\|noto\|chinese"

echo ""
echo "========================================="
echo "  安装完成！"
echo "========================================="
echo ""
echo "下一步："
echo "1. 退出 Render Shell"
echo "2. 在 Render Dashboard 触发手动部署"
echo "   - Manual Deploy → Clear build cache & deploy"
echo ""
