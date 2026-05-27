# AI 对话功能配置指南

本文档说明"故里"平台 AI 对话功能的配置方法。采用**双后端**方案：智谱AI(对话+视觉) + SiliconFlow(免费Embedding+备选对话)。

---

## 一、功能架构概览

```
用户提问 → RAG检索(知识库向量) → [可选]网络搜索(Tavily) → 组装Prompt → LLM生成回答 → SSE流式输出
                               ↑
                     管理员上传文档 → 解析 → 分块 → 向量化 → 存入数据库
```

### 核心模块

| 模块 | 文件 | 功能 |
|------|------|------|
| 文档解析 | `ai/document_parser.py` | 支持 PDF/TXT/MD/DOCX |
| 文本分块 | `ai/chunker.py` | 500字/块，50字重叠 |
| 向量化 | `ai/embedding.py` | SiliconFlow bge-large-zh-v1.5(免费,默认) / 智谱AI embedding-3(备选) |
| 大语言模型 | `ai/llm.py` | 智谱AI(主)+SiliconFlow(备选)，流式+非流式+视觉问答 |
| RAG核心 | `ai/rag.py` | 检索+增强+生成完整流程 |
| 网络搜索 | `ai/search.py` | Tavily API（可选） |

### 模型一览

| 用途 | 主模型 | 备选模型 | 说明 |
|------|--------|----------|------|
| 文本对话 | 智谱AI glm-4-flash | SiliconFlow Qwen2.5-7B | 429排队时自动切换 |
| 视觉问答 | 智谱AI glm-4.6v-flash | glm-4.1v-thinking-flash / glm-4v-flash | SiliconFlow无免费视觉模型 |
| 文本向量化 | SiliconFlow bge-large-zh-v1.5 | 智谱AI embedding-3 | 默认用SiliconFlow(免费)，中文专用 |

### 平台对比

| 平台 | 免费模型 | Embedding免费 | 视觉模型免费 | 注册 |
|------|----------|---------------|-------------|------|
| **智谱AI** | glm-4-flash, glm-4.6v-flash | embedding-3 (收费) | glm-4.6v-flash | [open.bigmodel.cn](https://open.bigmodel.cn/) |
| **SiliconFlow** | Qwen2.5-7B, DeepSeek等 | bge-large-zh-v1.5 (免费!) | 无 | [cloud.siliconflow.cn](https://cloud.siliconflow.cn/) |

---

## 二、本地开发配置

### 前置条件

1. 注册 [智谱AI](https://open.bigmodel.cn/) → 创建API密钥（对话+视觉，必需）
2. 注册 [SiliconFlow](https://cloud.siliconflow.cn/) → 创建API密钥 → **实名认证**（Embedding免费，强烈推荐）

### .env 配置

```env
# ===== 数据库：本地使用SQLite，无需Neon连接 =====
# DATABASE_URL 不要设置！本地用 instance/digital_heritage.db
# Neon连接串仅同步脚本使用
NEON_DATABASE_URL=postgresql://neondb_owner:xxx@ep-xxx.neon.tech/neondb?sslmode=require

SECRET_KEY=your-secret-key-change-this-in-production
FLASK_ENV=development

# ===== AI 配置 =====
# 智谱AI (必需 - 对话+视觉)
ZHIPU_API_KEY=你的智谱AI密钥

# SiliconFlow (强烈推荐 - 免费Embedding+备选对话)
SILICONFLOW_API_KEY=你的SiliconFlow密钥

# Embedding提供者: siliconflow(默认,免费) | zhipu(备选)
# EMBEDDING_PROVIDER=siliconflow

# 可选：网络搜索（不设置则禁用）
# TAVILY_API_KEY=你的Tavily密钥
```

### 启动

```bash
python app.py
```

### 验证

- 访问 http://localhost:5000/chat 测试AI对话
- 以管理员登录后台，访问"AI功能 → 知识库管理"上传文件
- 在对话中上传图片测试视觉问答
- 后台健康检查会显示两个平台配置状态

---

## 三、线上部署配置（Render）

### Render 环境变量配置

在 Render Dashboard → Environment 中设置：

```env
# ===== 必需 =====
FLASK_ENV=production
SECRET_KEY=<你的随机密钥，建议32位以上>
DATABASE_URL=postgresql://<Neon连接字符串>

# ===== AI核心配置 =====
ZHIPU_API_KEY=<你的智谱API密钥>
SILICONFLOW_API_KEY=<你的SiliconFlow密钥>

# ===== 可选 =====
# EMBEDDING_PROVIDER=siliconflow    # 默认siliconflow，也可改为zhipu
# TAVILY_API_KEY=<你的Tavily密钥>

# ===== RAG参数调优 =====
RAG_TOP_K=5                     # 检索返回的最大文本块数
RAG_SIMILARITY_THRESHOLD=0.3    # 相似度阈值，越高越严格
```

---

## 四、数据库注意事项

### 本地开发

**必须删除 `.env` 中的 `DATABASE_URL`**，否则 Flask 会尝试连接 Neon PostgreSQL，而 Neon 免费版会休眠导致连接失败。

本地使用 SQLite，数据库文件位于 `instance/digital_heritage.db`。

### 线上部署（Neon PostgreSQL）

- Neon 免费版 5分钟无活动后休眠，首次请求会有冷启动延迟（约2-5秒）
- 已配置连接池优化（pool_pre_ping, pool_recycle=180s）
- AI知识库上传已添加数据库重试逻辑（最多3次）

### 本地与云端数据库分离

```
本地开发 (SQLite)                    云端生产 (Neon)
┌──────────────────┐               ┌──────────────────┐
│ 智谱AI+SiliconFlow│               │ 智谱AI+SiliconFlow│
│ SQLite 数据库     │ ──同步脚本─>  │ Neon PostgreSQL  │
│ 知识库上传管理    │               │ 知识库检索服务    │
└──────────────────┘               └──────────────────┘
```

**同步脚本用法**：

```bash
# 预览差异（不实际写入）
python scripts/sync_knowledge_to_neon.py --dry-run

# 执行同步
python scripts/sync_knowledge_to_neon.py

# 强制重新向量化所有文件
python scripts/sync_knowledge_to_neon.py --re-vectorize
```

> **重要**：不同embedding模型的向量不兼容（SiliconFlow bge 1024维 vs 智谱 embedding-3 2048维），切换 `EMBEDDING_PROVIDER` 后需要重新向量化（删除旧chunks重新上传，或用 `--re-vectorize`）。

### 新表说明

| 表名 | 用途 | 自动创建 |
|------|------|----------|
| knowledge_files | 知识库源文件（含二进制数据） | 是(db.create_all) |
| knowledge_chunks | 文本块+向量(JSON) | 是(db.create_all) |
| chat_messages | 对话记录 | 是(db.create_all) |

---

## 五、知识库管理

### 使用方式

1. 以管理员身份登录后台
2. 进入"AI功能 → 知识库管理"
3. 点击"上传知识库文件"，支持 PDF/TXT/MD/DOCX
4. 上传后文件会自动：解析 → 分块(500字/块) → 向量化 → 存入数据库
5. 所有用户的AI对话都会自动检索知识库内容

### 注意事项

- 单文件大小限制：10MB
- 向量化使用SiliconFlow免费模型，不产生费用
- 上传进度条会显示文件上传进度
- 普通用户无法上传知识库文件，仅管理员可管理
- 删除文件会级联删除所有关联的知识片段

---

## 六、视觉问答（图片理解）

智谱AI glm-4.6v-flash 模型支持图片理解，免费使用。

- 图片超过2MB会自动压缩
- 视觉问答时不发送历史对话
- 429排队时会自动切换备选视觉模型

---

## 七、故障排查

| 症状 | 原因 | 解决方法 |
|------|------|----------|
| AI对话无响应 | API密钥未设置 | 检查.env中ZHIPU_API_KEY |
| 对话切换到SiliconFlow | 智谱AI 429排队 | 正常现象，自动切换，不影响使用 |
| 知识库上传失败 | 数据库连接断开 | 刷新重试，或本地删除DATABASE_URL |
| Embedding报错 | SILICONFLOW_API_KEY未配置 | 配置密钥或改EMBEDDING_PROVIDER=zhipu |
| 向量化后检索不准 | 切换了embedding模型 | 需重新向量化(删除旧chunks重新上传) |
| 视觉问答429 | 免费额度排队 | 等待几秒重试，代码自动切换备选 |

---

## 八、环境变量速查表

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `ZHIPU_API_KEY` | 是 | - | 智谱AI密钥（对话+视觉） |
| `SILICONFLOW_API_KEY` | 推荐 | - | SiliconFlow密钥（免费Embedding+备选对话） |
| `EMBEDDING_PROVIDER` | 否 | siliconflow | Embedding提供者: siliconflow / zhipu |
| `TAVILY_API_KEY` | 否 | - | Tavily搜索密钥(不设则禁用搜索) |
| `RAG_TOP_K` | 否 | 5 | 检索返回最大块数 |
| `RAG_SIMILARITY_THRESHOLD` | 否 | 0.3 | 相似度阈值 |
| `DATABASE_URL` | 线上 | SQLite | 数据库连接串(本地开发建议删除) |
