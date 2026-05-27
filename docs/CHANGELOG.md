# 更新日志

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。

---

## [1.2.0] - 2026-05-15

### 新增
- **双后端AI方案**：智谱AI(对话+视觉) + SiliconFlow(免费Embedding+备选对话)
  - Embedding默认用SiliconFlow bge-large-zh-v1.5（免费，中文专用）
  - 对话主用智谱AI glm-4-flash，429排队时自动切换SiliconFlow Qwen2.5-7B
  - 视觉问答仍用智谱AI glm-4.6v-flash（SiliconFlow无免费视觉模型）
- **对话历史与切换**：左侧会话列表，点击切换历史对话，支持删除会话
- **每日对话次数限制**：每用户默认5次/天，管理员可在后台单独设置
  - 设为0=禁止使用，-1=不限制
  - 顶部徽章显示剩余次数
- **数据库自动迁移**：新增字段时自动ALTER TABLE，无需手动操作或删库

### 变更
- 移除Ollama/DeepSeek代码路径，统一为智谱AI+SiliconFlow双后端
- 项目结构整理：scripts/(运维脚本) + docs/(文档) + deploy/(部署配置)
- 管理员后台用户表格新增"每日对话"列

### 修复
- `daily_chat_limit=0` 被falsy回退为5（改为`is not None`判断）
- 管理后台设置对话次数415错误（apiCall的JSON序列化问题）

---

## [1.1.0] - 2026-05-11

### 新增
- **AI智能对话功能**：完整RAG对话系统
  - 流式SSE输出（逐字显示AI回答）
  - 多模态视觉问答（用户上传图片提问）
  - 网络搜索补充（Tavily API，可选）
  - 统一使用智谱AI API（glm-4-flash + glm-4.6v-flash + embedding-3）
- **AI知识库管理**：后台管理员上传文档构建知识库
  - 支持 PDF/TXT/Markdown/DOCX 格式
  - 自动解析→分块(500字/块)→向量化→入库
- **环境变量自动加载**：`app.py`启动时调用`load_dotenv()`读取`.env`

### 修复
- `.env`未加载、知识库JS block名不匹配、SSE上下文丢失
- SQLAlchemy legacy warning、CSRF豁免方式、视觉模型参数兼容
- 图片>2MB自动压缩、Neon休眠重试、AI错误提示友好化

---

## [1.0.0] - 2026-02-25

### 新增
- 用户认证系统（注册、登录、登出）
- 数字资产管理（社交、金融、记忆、虚拟财产）
- 数字资产处置意愿声明书创建和管理
- 平台政策矩阵展示
- 数字资产继承导航
- 故事墙功能
- 常见问题解答（FAQ）
- 后台管理系统
- Render云服务部署支持
- Neon PostgreSQL数据库支持

### 修复
- GitGuardian检测到数据库密码泄露
- SSL连接错误（Neon休眠）
- SQLite URI格式修复
- CSRF错误修复
- 管理员后台Internal Server Error修复
