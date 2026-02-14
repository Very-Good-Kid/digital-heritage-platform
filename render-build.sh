#!/bin/bash
# Render 构建脚本 - 免费版优化（不需要root权限）

echo "Starting build process..."

# 只安装Python依赖
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Build process completed successfully!"
echo "Note: Chinese fonts will be installed at runtime"
