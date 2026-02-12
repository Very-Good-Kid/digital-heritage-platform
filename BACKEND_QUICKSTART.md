# 后台管理系统 - 快速开始指南

## 概述

数字遗产管理平台的后台管理系统已完成开发，提供了完整的用户数据管理、内容管理、数据统计和可视化功能。

---

## 快速开始

### 1. 安装依赖

```bash
cd C:\Users\admin\Desktop\demo
pip install -r requirements.txt
```

### 2. 创建管理员账户

```bash
python create_admin.py
```

按照提示输入管理员信息：

```
请输入管理员用户名 [默认: admin]: admin
请输入管理员邮箱 [默认: admin@digitalheritage.com]: admin@example.com
请输入管理员密码: [输入密码]
请再次输入密码确认: [再次输入密码]
```

### 3. 启动应用

```bash
python app.py
```

### 4. 访问后台

打开浏览器访问：
```
http://localhost:5000/admin
```

使用创建的管理员账户登录。

---

## 系统功能

### 仪表盘
- 实时统计数据（用户、资产、遗嘱、内容）
- 用户增长趋势图
- 资产分类分布图
- 系统活动统计
- 待处理事项提醒

### 用户管理
- 查看用户列表
- 创建新用户
- 编辑用户信息
- 删除用户
- 启用/禁用用户
- 搜索和筛选

### 数字资产管理
- 查看所有用户的数字资产
- 按平台或账号搜索
- 按分类筛选
- 删除资产

### 数字遗嘱管理
- 查看所有用户的数字遗嘱
- 按标题或描述搜索
- 按状态筛选（草稿、已确认、已归档）
- 删除遗嘱

### 内容管理

#### 平台政策
- 查看平台政策列表
- 添加新政策
- 编辑政策
- 删除政策

#### FAQ管理
- 查看FAQ列表
- 添加新FAQ
- 编辑FAQ
- 删除FAQ

#### 故事管理
- 查看用户故事
- 审核故事（通过/拒绝）
- 删除故事

### 系统设置
- 查看系统信息
- 查看快速统计
- 查看系统健康状态
- 管理操作入口

---

## API接口

后台管理系统提供RESTful API接口，详细文档请参考 `ADMIN_API_DOCUMENTATION.md`

### 常用API示例

```bash
# 获取统计数据
curl http://localhost:5000/admin/api/stats

# 获取用户列表
curl http://localhost:5000/admin/api/users?page=1&per_page=20

# 获取用户详情
curl http://localhost:5000/admin/api/users/1

# 获取用户增长图表数据
curl http://localhost:5000/admin/api/charts/growth?days=30
```

---

## 目录结构

```
demo/
├── admin/                           # 后台管理模块
│   ├── __init__.py
│   ├── decorators.py                # 权限装饰器
│   ├── auth.py                      # 认证和权限工具
│   ├── views.py                     # 视图和API路由
│   ├── stats.py                     # 数据统计模块
│   ├── crud.py                      # CRUD操作
│   ├── api_format.py                # API响应格式
│   └── templates/                   # 前端模板
│       ├── base.html                # 基础模板
│       ├── dashboard.html           # 仪表盘
│       ├── users.html               # 用户管理
│       ├── assets.html              # 资产管理
│       ├── wills.html               # 遗嘱管理
│       ├── policies.html            # 政策管理
│       ├── faqs.html                # FAQ管理
│       ├── stories.html             # 故事管理
│       └── settings.html            # 系统设置
├── app.py                           # 主应用（已集成后台）
├── models.py                        # 数据模型
├── config.py                        # 配置文件
├── create_admin.py                  # 管理员创建脚本
├── requirements.txt                 # 依赖列表
├── ADMIN_API_DOCUMENTATION.md       # API文档
└── BACKEND_SYSTEM_DESIGN.md         # 系统设计文档
```

---

## 权限说明

### 管理员
- 访问后台管理系统
- 管理所有用户
- 管理所有内容
- 查看统计数据
- 系统配置

### 普通用户
- 只能访问前台用户界面
- 只能管理自己的数据
- 无法访问后台

---

## 安全特性

1. **认证和授权**
   - Flask-Login会话管理
   - 密码加密存储
   - CSRF保护
   - 基于角色的访问控制

2. **数据安全**
   - 密码使用bcrypt加密
   - 敏感数据使用AES加密
   - SQL注入防护
   - XSS防护

3. **会话安全**
   - 安全的密钥配置
   - 会话超时设置
   - HTTPS支持（生产环境）

---

## 常见问题

### Q: 忘记管理员密码怎么办？
A: 可以运行 `create_admin.py` 创建新的管理员账户，然后删除旧账户。

### Q: 如何查看所有管理员？
A: 运行 `python create_admin.py --list` 或 `python create_admin.py -l`

### Q: 如何重置用户状态？
A: 在用户管理页面点击操作按钮，或使用API接口 `POST /admin/api/users/:id/toggle-status`

### Q: 系统支持哪些数据可视化？
A: 支持折线图、饼图、柱状图，使用Chart.js实现

### Q: 如何导出数据？
A: 目前支持通过API获取JSON格式数据，可以后续扩展CSV/Excel导出功能

---

## 技术支持

- API文档: `ADMIN_API_DOCUMENTATION.md`
- 系统设计: `BACKEND_SYSTEM_DESIGN.md`
- 项目文档: `README.md`

---

## 更新日志

### v1.0.0 (2026-02-11)
- ✅ 完成后台管理系统开发
- ✅ 用户管理模块
- ✅ 数字资产管理模块
- ✅ 数字遗嘱管理模块
- ✅ 内容管理模块
- ✅ 数据统计和可视化
- ✅ RESTful API
- ✅ 权限控制系统
- ✅ 响应式前端界面

---

## 许可证

本系统为数字遗产管理平台的一部分，遵循相同的许可证。
