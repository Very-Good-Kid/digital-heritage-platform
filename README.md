# 数字遗产继承平台

## 项目简介

数字遗产继承平台是一个一站式数字遗产规划与继承服务平台，帮助用户在生前规划数字遗产，为继承人提供清晰的继承指引。平台聚焦社交账号（微信、QQ、抖音等）虚拟财产继承，为用户提供生前规划与身后继承的完整解决方案。

## 核心功能

### 1. 生前规划系统
- **数字遗产清单生成器**：系统盘点数字资产，支持分类填写（社交、金融、记忆、虚拟财产）
- **数字遗嘱生成器**：基于用户填写的清单，生成格式规范的《数字遗产意愿声明》PDF文档
- **数据加密存储**：用户敏感信息采用AES-256加密技术存储，确保信息安全

### 2. 身后继承系统
- **平台政策矩阵**：汇总主流平台（微信、QQ、抖音）关于数字资产继承的政策信息
- **数字资产继承导航**：情景化流程指引工具，根据不同情况生成专属路径图

### 3. 情感与社区支持
- **数字记忆故事墙**：分享情感故事、哲思文章、媒体报道
- **FAQ系统**：常见问题分类展示和解答

## 技术栈

- **后端框架**：Flask 3.0
- **数据库**：SQLite（可扩展至MySQL/PostgreSQL）
- **前端框架**：Bootstrap 5.3
- **加密技术**：cryptography (Fernet)
- **PDF生成**：reportlab
- **用户认证**：Flask-Login

## 安装和运行

### 1. 环境要求
- Python 3.8+
- pip

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 运行应用
```bash
python app.py
```

应用将在 `http://localhost:5000` 启动

### 4. 首次访问
- 访问首页：`http://localhost:5000`
- 注册账户：点击页面右上角的"注册"按钮
- 登录后即可开始使用各项功能

## 项目结构

```
demo/
├── app.py                      # 主应用文件
├── config.py                   # 配置文件
├── models.py                   # 数据库模型
├── requirements.txt            # Python依赖
├── utils/                      # 工具类目录
│   ├── __init__.py
│   ├── encryption.py          # 数据加密工具
│   └── pdf_generator.py       # PDF生成工具
├── templates/                  # HTML模板目录
│   ├── base.html              # 基础模板
│   ├── index.html             # 首页
│   ├── about.html             # 关于我们
│   ├── auth/                  # 认证相关模板
│   ├── dashboard/             # 仪表盘模板
│   ├── assets/                # 数字资产模板
│   ├── wills/                 # 数字遗嘱模板
│   ├── policies/              # 平台政策模板
│   ├── inheritance-guide/     # 继承导航模板
│   ├── stories/               # 故事墙模板
│   ├── faq/                   # FAQ模板
│   └── errors/                # 错误页面模板
├── static/                     # 静态文件目录
│   ├── css/
│   ├── js/
│   └── images/
└── README.md                   # 项目说明文档
```

## 数据库模型

### User（用户）
- id: 用户ID
- username: 用户名
- email: 邮箱
- password_hash: 密码哈希
- created_at: 创建时间
- updated_at: 更新时间

### DigitalAsset（数字资产）
- id: 资产ID
- user_id: 用户ID（外键）
- platform_name: 平台名称
- account: 账号
- encrypted_password: 加密密码
- category: 分类（社交、金融、记忆、虚拟财产）
- notes: 备注
- created_at: 创建时间
- updated_at: 更新时间

### DigitalWill（数字遗嘱）
- id: 遗嘱ID
- user_id: 用户ID（外键）
- title: 标题
- description: 描述
- assets_data: 资产处理选项（JSON）
- status: 状态（draft、confirmed、archived）
- created_at: 创建时间
- updated_at: 更新时间

### PlatformPolicy（平台政策）
- id: 政策ID
- platform_name: 平台名称
- policy_content: 政策内容
- attitude: 平台态度（明确禁止、态度模糊、有限支持、主动服务）
- inherit_possibility: 继承可能性（低、中、高）
- legal_basis: 法律依据
- customer_service: 客服联系方式
- risk_warning: 风险提示
- created_at: 创建时间
- updated_at: 更新时间

### Story（故事）
- id: 故事ID
- title: 标题
- content: 内容
- author: 作者
- category: 分类（情感故事、哲思文章、媒体报道）
- image_url: 图片URL
- status: 状态（pending、approved、rejected）
- created_at: 创建时间
- updated_at: 更新时间

### FAQ（常见问题）
- id: 问题ID
- question: 问题
- answer: 答案
- category: 分类
- order: 排序
- created_at: 创建时间
- updated_at: 更新时间

## 安全特性

1. **数据加密**：用户密码和敏感信息使用AES-256加密存储
2. **密码哈希**：用户密码使用Werkzeug的安全哈希算法
3. **会话管理**：使用Flask-Login进行安全的用户会话管理
4. **CSRF保护**：Flask-WTF提供CSRF保护
5. **输入验证**：所有用户输入都经过验证和清理

## 开发计划

### 第一阶段（MVP版本）
- [x] 平台政策矩阵（微信、QQ、抖音）
- [x] 数字遗产清单生成器
- [x] 数字遗嘱生成器（基础版）
- [x] 继承导航（核心情景）

### 第二阶段
- [ ] 继承导航完整情景
- [ ] 故事墙内容系统完善
- [ ] FAQ系统完善
- [ ] 用户注册邮箱验证
- [ ] 密码重置功能

### 第三阶段
- [ ] 问答社区功能
- [ ] 数据统计分析后台
- [ ] API接口开发
- [ ] 小程序/APP开发

## 法律声明

本平台提供的信息和工具仅供参考，不构成法律建议。数字遗产的继承需遵循相关法律法规。建议用户在制定数字遗嘱时咨询专业律师。

## 联系方式

- 邮箱：contact@digitalheritage.com
- 电话：400-888-8888
- 地址：北京市朝阳区

## 许可证

本项目仅供学习和研究使用。

## 致谢

感谢所有为本项目做出贡献的开发者和用户。
