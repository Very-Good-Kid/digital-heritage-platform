#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
知识库同步脚本 - 将本地SQLite的知识库数据同步到云端Neon PostgreSQL

使用方法:
    python scripts/sync_knowledge_to_neon.py              # 同步所有知识库文件
    python scripts/sync_knowledge_to_neon.py --dry-run    # 仅预览，不实际写入
    python scripts/sync_knowledge_to_neon.py --re-vectorize  # 强制云端重新向量化

工作流程:
    1. 读取本地SQLite中的 knowledge_files + knowledge_chunks
    2. 连接云端Neon PostgreSQL
    3. 比对本地与云端差异（按filename判断）
    4. 新增文件：推送原文(file_data) + 分块内容(chunk.content)到云端
    5. 云端自动用智谱AI embedding-3 重新向量化（因为Ollama和智谱的向量不兼容）
    6. 已删除文件：从云端删除对应记录
    7. 已存在文件：跳过（除非 --re-vectorize）

前置条件:
    - .env 中 NEON_DATABASE_URL 已配置
    - 本地SQLite中有知识库数据
    - 云端同步时需要智谱AI API密钥（用于向量化）
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv(override=True)

from app import app
from models import db as local_db, KnowledgeFile as LocalKnowledgeFile, KnowledgeChunk as LocalKnowledgeChunk
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


def get_neon_engine():
    """获取Neon PostgreSQL连接引擎"""
    neon_url = os.environ.get('NEON_DATABASE_URL')
    if not neon_url:
        print("错误: 未设置 NEON_DATABASE_URL 环境变量")
        print("请在 .env 中添加:")
        print("  NEON_DATABASE_URL=postgresql://...")
        sys.exit(1)
    
    return create_engine(neon_url, pool_pre_ping=True, pool_recycle=180)


def ensure_neon_tables(neon_session):
    """确保云端Neon中存在知识库表"""
    create_sql = """
    CREATE TABLE IF NOT EXISTS knowledge_files (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        filename VARCHAR(256) NOT NULL,
        file_type VARCHAR(32) NOT NULL,
        file_data BYTEA,
        chunk_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS knowledge_chunks (
        id SERIAL PRIMARY KEY,
        file_id INTEGER NOT NULL REFERENCES knowledge_files(id) ON DELETE CASCADE,
        chunk_index INTEGER NOT NULL,
        content TEXT NOT NULL,
        embedding JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    try:
        neon_session.execute(text(create_sql))
        neon_session.commit()
        print("  云端表结构检查完成")
    except Exception as e:
        neon_session.rollback()
        print(f"  创建表失败: {e}")
        sys.exit(1)


def get_local_files():
    """获取本地SQLite中的所有知识库文件"""
    with app.app_context():
        files = local_db.session.query(LocalKnowledgeFile).all()
        result = []
        for f in files:
            chunks = local_db.session.query(LocalKnowledgeChunk).filter_by(file_id=f.id).all()
            result.append({
                'id': f.id,
                'filename': f.filename,
                'file_type': f.file_type,
                'file_data': f.file_data,
                'chunk_count': f.chunk_count,
                'created_at': f.created_at,
                'chunks': [{
                    'chunk_index': c.chunk_index,
                    'content': c.content,
                } for c in chunks]
            })
        return result


def get_neon_files(neon_session):
    """获取云端Neon中的所有知识库文件"""
    result = neon_session.execute(text("SELECT id, filename, chunk_count FROM knowledge_files"))
    return {row[1]: {'id': row[0], 'filename': row[1], 'chunk_count': row[2]} for row in result}


def zhipu_embed_texts(texts, api_key):
    """用智谱AI embedding-3 对文本列表向量化（云端专用）"""
    url = "https://open.bigmodel.cn/api/paas/v4/embeddings"
    headers = {"Authorization": f"Bearer {api_key}"}
    all_embeddings = []
    
    for i in range(0, len(texts), 16):
        batch = texts[i:i+16]
        data = {"model": "embedding-3", "input": batch}
        resp = __import__('requests').post(url, headers=headers, json=data, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        sorted_data = sorted(result['data'], key=lambda x: x['index'])
        all_embeddings.extend([d['embedding'] for d in sorted_data])
        if i + 16 < len(texts):
            time.sleep(0.5)
    
    return all_embeddings


def siliconflow_embed_texts(texts, api_key):
    """用SiliconFlow BAAI/bge-large-zh-v1.5 对文本列表向量化（云端专用，免费）"""
    url = "https://api.siliconflow.cn/v1/embeddings"
    headers = {"Authorization": f"Bearer {api_key}"}
    all_embeddings = []
    
    for i in range(0, len(texts), 32):
        batch = texts[i:i+32]
        data = {"model": "BAAI/bge-large-zh-v1.5", "input": batch, "encoding_format": "float"}
        resp = __import__('requests').post(url, headers=headers, json=data, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        sorted_data = sorted(result['data'], key=lambda x: x['index'])
        all_embeddings.extend([d['embedding'] for d in sorted_data])
        if i + 32 < len(texts):
            time.sleep(0.5)
    
    return all_embeddings


def sync_to_neon(dry_run=False, re_vectorize=False):
    """执行同步"""
    print("\n" + "=" * 60)
    print("       知识库同步: 本地SQLite → 云端Neon PostgreSQL")
    print("=" * 60)
    
    # 1. 获取本地文件
    print("\n[1/4] 读取本地知识库...")
    local_files = get_local_files()
    local_names = {f['filename'] for f in local_files}
    print(f"  本地共 {len(local_files)} 个文件: {', '.join(local_names) or '(空)'}")
    
    if not local_files:
        print("\n本地知识库为空，无需同步。")
        return
    
    # 2. 连接云端Neon
    print("\n[2/4] 连接云端Neon PostgreSQL...")
    engine = get_neon_engine()
    NeonSession = sessionmaker(bind=engine)
    neon_session = NeonSession()
    
    try:
        ensure_neon_tables(neon_session)
    except Exception as e:
        print(f"  连接失败: {e}")
        return
    
    # 3. 比对差异
    print("\n[3/4] 比对本地与云端差异...")
    neon_files = get_neon_files(neon_session)
    neon_names = set(neon_files.keys())
    
    to_add = local_names - neon_names
    to_delete = neon_names - local_names
    to_update = local_names & neon_names if re_vectorize else set()
    to_skip = (local_names & neon_names) - to_update
    
    print(f"  需要新增: {len(to_add)} 个 → {', '.join(to_add) or '无'}")
    print(f"  需要删除: {len(to_delete)} 个 → {', '.join(to_delete) or '无'}")
    if re_vectorize:
        print(f"  需要更新: {len(to_update)} 个（强制重新向量化）")
    print(f"  跳过(已存在): {len(to_skip)} 个 → {', '.join(to_skip) or '无'}")
    
    if dry_run:
        print("\n[DRY RUN] 仅预览，不实际写入。")
        print(f"  将新增 {len(to_add)} 个文件，删除 {len(to_delete)} 个文件")
        if re_vectorize:
            print(f"  将更新 {len(to_update)} 个文件")
        neon_session.close()
        return
    
    # 4. 执行同步
    print("\n[4/4] 执行同步...")
    
    # 4a. 删除云端多余文件
    for name in to_delete:
        try:
            neon_file_id = neon_files[name]['id']
            neon_session.execute(text("DELETE FROM knowledge_chunks WHERE file_id = :fid"), {"fid": neon_file_id})
            neon_session.execute(text("DELETE FROM knowledge_files WHERE id = :fid"), {"fid": neon_file_id})
            neon_session.commit()
            print(f"  已删除: {name}")
        except Exception as e:
            neon_session.rollback()
            print(f"  删除失败 {name}: {e}")
    
    # 4b. 检查Embedding API密钥（向量化需要）
    embed_provider = os.environ.get('EMBEDDING_PROVIDER', 'siliconflow').lower()
    if embed_provider == 'siliconflow':
        embed_key = os.environ.get('SILICONFLOW_API_KEY')
        embed_fn = siliconflow_embed_texts
        embed_name = 'SiliconFlow bge-large-zh-v1.5(免费)'
    else:
        embed_key = os.environ.get('ZHIPU_API_KEY')
        embed_fn = zhipu_embed_texts
        embed_name = '智谱AI embedding-3'
    
    if not embed_key:
        print(f"\n  警告: 未设置 {'SILICONFLOW_API_KEY' if embed_provider == 'siliconflow' else 'ZHIPU_API_KEY'}，无法在云端向量化！")
        print("  将只推送原文，云端知识库检索将不可用。")
    else:
        print(f"\n  Embedding提供者: {embed_name}")
    
    # 4c. 新增文件 + 向量化
    for local_file in local_files:
        fname = local_file['filename']
        if fname not in to_add and fname not in to_update:
            continue
        
        # 如果是更新，先删除旧记录
        if fname in to_update:
            old_id = neon_files[fname]['id']
            neon_session.execute(text("DELETE FROM knowledge_chunks WHERE file_id = :fid"), {"fid": old_id})
            neon_session.execute(text("DELETE FROM knowledge_files WHERE id = :fid"), {"fid": old_id})
            neon_session.commit()
        
        try:
            # 插入文件记录（需要找一个admin用户的user_id）
            admin_row = neon_session.execute(text("SELECT id FROM \"user\" WHERE is_admin = true LIMIT 1")).first()
            admin_id = admin_row[0] if admin_row else 1
            
            neon_session.execute(text("""
                INSERT INTO knowledge_files (user_id, filename, file_type, file_data, chunk_count, created_at)
                VALUES (:uid, :fname, :ftype, :fdata, :ccount, :ctime)
            """), {
                "uid": admin_id,
                "fname": fname,
                "ftype": local_file['file_type'],
                "fdata": local_file['file_data'],
                "ccount": local_file['chunk_count'],
                "ctime": local_file['created_at']
            })
            neon_session.commit()
            
            # 获取刚插入的文件ID
            neon_file = neon_session.execute(
                text("SELECT id FROM knowledge_files WHERE filename = :fname ORDER BY id DESC LIMIT 1"),
                {"fname": fname}
            ).first()
            neon_file_id = neon_file[0]
            
            # 向量化chunk并插入
            chunks = local_file['chunks']
            if embed_key and chunks:
                print(f"  向量化 {fname} ({len(chunks)}个片段)...")
                chunk_texts = [c['content'] for c in chunks]
                embeddings = embed_fn(chunk_texts, embed_key)
                
                for chunk, embedding in zip(chunks, embeddings):
                    neon_session.execute(text("""
                        INSERT INTO knowledge_chunks (file_id, chunk_index, content, embedding, created_at)
                        VALUES (:fid, :cidx, :content, :emb, CURRENT_TIMESTAMP)
                    """), {
                        "fid": neon_file_id,
                        "cidx": chunk['chunk_index'],
                        "content": chunk['content'],
                        "emb": json.dumps(embedding, ensure_ascii=False)
                    })
            else:
                # 无API密钥，只推原文不推向量
                for chunk in chunks:
                    neon_session.execute(text("""
                        INSERT INTO knowledge_chunks (file_id, chunk_index, content, created_at)
                        VALUES (:fid, :cidx, :content, CURRENT_TIMESTAMP)
                    """), {
                        "fid": neon_file_id,
                        "cidx": chunk['chunk_index'],
                        "content": chunk['content']
                    })
            
            neon_session.commit()
            action = "更新" if fname in to_update else "新增"
            print(f"  已{action}: {fname} ({len(chunks)}个片段)")
            
        except Exception as e:
            neon_session.rollback()
            print(f"  同步失败 {fname}: {e}")
    
    neon_session.close()
    print("\n" + "=" * 60)
    print("  同步完成!")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    args = sys.argv[1:]
    dry_run = '--dry-run' in args
    re_vectorize = '--re-vectorize' in args
    
    if '--help' in args or '-h' in args:
        print(__doc__)
        sys.exit(0)
    
    sync_to_neon(dry_run=dry_run, re_vectorize=re_vectorize)
