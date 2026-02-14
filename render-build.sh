#!/bin/bash
set -e  # 遇到错误立即退出

echo "Starting build process..."

# 只安装Python依赖
echo "Installing Python dependencies..."
pip install -r requirements.txt || {
    echo "Failed to install Python dependencies"
    exit 1
}

echo "Build process completed successfully!"
echo "Note: Chinese fonts will be installed at runtime"
