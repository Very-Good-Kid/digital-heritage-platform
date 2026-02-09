#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
阿里云OSS上传脚本
需要安装: pip install oss2
"""

import oss2
import os

# 阿里云OSS配置
OSS_ACCESS_KEY_ID = 'your-access-key-id'  # 替换为你的AccessKey ID
OSS_ACCESS_KEY_SECRET = 'your-access-key-secret'  # 替换为你的AccessKey Secret
OSS_ENDPOINT = 'https://oss-cn-hangzhou.aliyuncs.com'  # 替换为你的Endpoint
OSS_BUCKET_NAME = 'your-bucket-name'  # 替换为你的Bucket名称

def upload_to_oss(local_path, remote_path=None):
    """上传文件到OSS"""
    # 创建OSS客户端
    auth = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
    bucket = oss2.Bucket(auth, OSS_ENDPOINT, OSS_BUCKET_NAME)

    # 设置远程路径
    if remote_path is None:
        remote_path = os.path.basename(local_path)

    try:
        # 上传文件
        bucket.put_object_from_file(remote_path, local_path)
        print(f"✓ 上传成功: {local_path} -> {remote_path}")
        return True
    except Exception as e:
        print(f"✗ 上传失败: {local_path} - {e}")
        return False

def upload_directory(local_dir, remote_dir=''):
    """上传目录到OSS"""
    for root, dirs, files in os.walk(local_dir):
        for file in files:
            local_path = os.path.join(root, file)
            # 计算相对路径
            relative_path = os.path.relpath(local_path, local_dir)
            remote_path = os.path.join(remote_dir, relative_path).replace('\\', '/')
            upload_to_oss(local_path, remote_path)

def main():
    print("阿里云OSS上传工具")
    print("=" * 40)

    print("\n请先配置OSS凭证:")
    print("1. 编辑此文件")
    print("2. 替换 OSS_ACCESS_KEY_ID")
    print("3. 替换 OSS_ACCESS_KEY_SECRET")
    print("4. 替换 OSS_ENDPOINT")
    print("5. 替换 OSS_BUCKET_NAME")

    print("\n配置完成后，选择上传模式:")
    print("1. 上传整个dist目录")
    print("2. 上传单个文件")

    choice = input("\n请输入选择 (1/2): ")

    if choice == '1':
        print("\n开始上传dist目录...")
        upload_directory('dist', '')
        print("\n上传完成！")
    elif choice == '2':
        file_path = input("请输入文件路径: ")
        if os.path.exists(file_path):
            upload_to_oss(file_path)
        else:
            print("文件不存在！")
    else:
        print("无效的选择！")

if __name__ == '__main__':
    main()
