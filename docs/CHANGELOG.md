# 更新日志

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。

---

## [1.3.1] - 2026-07-24

### 安全加固（Security Hardening）

#### 高危修复
- **外部知识库 API 密钥明文存储（H3）** `models.py`
  - `ExternalKnowledge.get_config` / `set_config` 对 `api_key`/`app_secret`/`token`/`access_token`/`secret`/`password`/`app_key` 及以 `_key`/`_secret`… 结尾的敏感字段自动加解密；解密失败向后兼容返回原文

#### 中危修复
- **SSRF 防护（M2）** `ai/knowledge_providers.py`
  - 新增 `validate_fetch_url()` / `_is_ip_safe()` / `_resolve_and_check_host()`：解析目标 IP 并拒绝回环/私有/链路本地（含 `169.254.169.254` 云元数据）段，禁止 URL userinfo，抓取 `allow_redirects=False`
- **对话配额限流绕过 + 竞态（H2）** `app.py`
  - 非流式 `/chat/api/message` 与流式 `/chat/api/stream` 均调用 `_increment_chat_usage`
  - 改为原子 `UPDATE chat_usage SET count = count + 1 ...` + 首条 `INSERT`，消除 TOCTOU；生成器中断（异常分支）也落库
- **SQLite 并发锁（M9）** `app.py`
  - 启用 WAL（`PRAGMA journal_mode=WAL`）+ `busy_timeout=5000`，降低 `database is locked`
- **异常信息泄露（M4）** `app.py`
  - 3 处异常对用户泛化为通用提示（`AI服务暂时不可用，请稍后重试` / `PDF生成失败，请稍后重试`），内部错误仅记日志
- **后台创建用户无密码强度（M12）** `admin/crud.py`
  - `create_user` 增加密码策略：≥8 位且字母数字混合，与注册页一致
- **FAQ XSS 转义遗漏（M3 补充）** `templates/care/index.html`
  - 关怀页 FAQ 答案同步先转义 `&` 再转义 `<>`（FAQ 页已在 1.3.0 修复）
- **上传目录创建失败被静默吞掉（M10）** `config.py`
  - 改为 `except Exception as e` + `logging.warning(..., exc_info=True)`，启动期可排查

#### 低危修复
- **"双层加密"为假设计（F6）** `utils/encryption.py`
  - 移除误导的模块级 `fernet = Fernet(ENCRYPTION_KEY)` 变量；`ENCRYPTION_KEY` 仅做启动期格式校验与 fail-fast，实际加解密由 `ENCRYPTION_PASSWORD` 经 PBKDF2 派生密钥完成

#### 部署配置
- `deploy/Procfile`：补 `FLASK_ENV=production`，防止 gunicorn 落入 `DevelopmentConfig`（`DEBUG=True`）
- `deploy/render.yaml`：新增 `ENCRYPTION_KEY` / `ENCRYPTION_PASSWORD` 环境变量（`sync: false`，由部署平台注入）

---

## [1.3.0] - 2026-07-23

### 安全加固（Security Hardening）

#### 高危修复
- **凭据加密重构** `utils/encryption.py`
  - 移除硬编码默认密码（`digital_heritage_default_password_2026`），密钥/密码缺失时 fail-fast 拒绝启动
  - 去除全局固定盐，改用每条记录独立随机盐（`salt_b64:cipher_b64` 格式存储）
  - PBKDF2 迭代次数 100K → 600K
  - 错误处理从静默返回 `None` 改为明确抛出 `ValueError`
- **聊天 XSS 防护**：前端引入 DOMPurify（CDN 锁定 `dompurify@3.1.6`）双重净化，禁止 `style/iframe/onerror` 等危险标签属性；服务端同步引入 bleach 净化
- **CSRF 边界收紧** `admin/views.py` / `app.py`
  - 移除 25 个后台状态变更 API 的 `@csrf_exempt` 装饰器（用户/资产/遗嘱/政策/FAQ/故事审核/外部知识库等）
  - 移除 `upload_knowledge`/`delete_knowledge`/`delete_session` 的 CSRF 豁免
- **调试边界防护** `app.py` / `deploy/Dockerfile`
  - 生产环境通过 `ALLOW_DEBUG` 开关控制，默认关闭且仅绑定 `127.0.0.1`
  - Dockerfile 新增非 root 用户 `appuser`，CMD 改为 gunicorn（移除 debug 模式），pip 源改回官方 PyPI

#### 中危修复
- `config.py`：`SECRET_KEY` 缺失即拒绝启动，`SESSION_COOKIE_SECURE=True` 强制启用，新增 `SESSION_IDLE_TIMEOUT=30min`
- 开放重定向防护：登录 `next` 参数使用 `url_parse` 校验，仅允许相对路径
- 登录限流：会话级失败计数，≥10 次触发 15 分钟冷却
- 注册密码策略：≥8 位且字母数字混合，统一模糊错误提示（防用户枚举）
- RAG 提示注入防护 `ai/rag.py`：检索内容用 `<untrusted_reference>` 边界标记，明确"不可当作指令执行"；入库前调用 `sanitize_llm_content()` 净化
- FAQ XSS 防护：`templates/faq/index.html` 答案改为 HTML 实体转义后再 `safe`
- 知识库配额限制：单用户 50 文件 + 100MB 上限
- `admin/crud.py`：`update_user()` 显式 `pop('is_admin')` 阻断提权，新增 `set_admin_privilege()` 专用接口需二次校验

#### 低危修复
- 异常信息净化：`admin/crud.py` 6 处异常从 `f'Create failed: {str(e)}'` 改为通用中文提示，避免敏感信息泄露

#### 依赖与配置
- `requirements.txt` 升级：Flask≥3.0.3、Werkzeug≥3.0.3、cryptography≥42.0.5，新增 `bleach>=6.1.0`
- 新增 `.dockerignore`（排除 `.env`/`instance/`/`*.db`/`uploads/`/`temp_pdfs/`/`.git`）
- `.env` 完善：补充 `ENCRYPTION_KEY` / `ENCRYPTION_PASSWORD`，`SECRET_KEY` 替换为强随机值

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
