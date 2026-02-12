# 后台管理系统设计文档

## 概述

本文档描述了数字遗产管理平台的后台管理系统的完整设计和实现方案。该系统采用模块化架构设计，具备完整的CRUD功能、基于角色的访问控制、数据统计可视化和RESTful API。

---

## 系统特点

### 1. 直观的用户界面
- 现代简约的设计风格
- 渐变色主题（紫色系）
- 响应式布局适配不同设备
- 直观的导航和操作流程
- 实时数据展示和可视化图表

### 2. 模块化架构设计
```
admin/
├── __init__.py          # 包初始化
├── decorators.py        # 权限装饰器
├── auth.py              # 认证和权限工具
├── views.py             # 视图和API路由
├── stats.py             # 数据统计模块
├── crud.py              # CRUD操作模块
├── api_format.py        # API响应格式
└── templates/           # 模板文件
    ├── base.html        # 基础模板
    ├── dashboard.html   # 仪表盘
    ├── users.html       # 用户管理
    ├── assets.html      # 资产管理
    ├── wills.html       # 遗嘱管理
    ├── policies.html    # 政策管理
    ├── faqs.html        # FAQ管理
    ├── stories.html     # 故事管理
    └── settings.html    # 系统设置
```

### 3. 完整的用户数据CRUD功能

#### 用户管理
- 创建用户
- 查看用户列表和详情
- 编辑用户信息
- 删除用户
- 启用/禁用用户
- 搜索和筛选

#### 数字资产管理
- 查看所有用户的数字资产
- 按平台、账号搜索
- 按分类筛选（社交、金融、记忆、虚拟财产）
- 删除资产
- 分页显示

#### 数字遗嘱管理
- 查看所有用户的数字遗嘱
- 按标题、描述搜索
- 按状态筛选（草稿、已确认、已归档）
- 删除遗嘱
- 分页显示

#### 内容管理
- 平台政策管理（增删改查）
- FAQ管理（增删改查）
- 故事管理（增删改查+审核）

### 4. 基于角色的访问控制

#### 权限级别
- **管理员**: 拥有所有权限
- **普通用户**: 只能访问自己的数据
- **访客**: 只能访问公开内容

#### 权限装饰器
```python
# 管理员权限
@admin_required
def admin_route():
    pass

# 基于角色的权限
@role_required('admin', 'editor')
def role_route():
    pass
```

#### 权限检查函数
```python
is_admin()                      # 是否为管理员
can_edit_user(user_id)          # 是否可以编辑用户
can_delete_user(user_id)        # 是否可以删除用户
can_view_user_data(user_id)     # 是否可以查看用户数据
```

### 5. 数据统计和可视化功能

#### 仪表盘统计
- 总用户数、活跃用户数、管理员数
- 新注册用户（7天内）
- 数字资产总数及分类统计
- 数字遗嘱总数及状态统计
- 内容统计（政策数、FAQ数、故事数）
- 待审核事项

#### 图表可视化
- 用户增长趋势图（折线图）
- 资产分类分布图（饼图）
- 系统活动统计图（柱状图）

#### 数据API
```python
GET /admin/api/stats                    # 获取统计数据
GET /admin/api/charts/growth?days=30    # 获取增长数据
GET /admin/api/charts/activity?days=7   # 获取活动数据
```

### 6. RESTful API设计规范

#### API设计原则
- 使用标准HTTP方法（GET、POST、PUT、DELETE）
- 统一的响应格式
- 语义化的URL路径
- 分页支持
- 搜索和筛选支持

#### API示例

**用户管理**
```http
GET    /admin/api/users              # 获取用户列表
GET    /admin/api/users/:id          # 获取用户详情
POST   /admin/api/users              # 创建用户
PUT    /admin/api/users/:id          # 更新用户
DELETE /admin/api/users/:id          # 删除用户
POST   /admin/api/users/:id/toggle-status  # 切换状态
```

**数字资产**
```http
GET    /admin/api/assets             # 获取资产列表
DELETE /admin/api/assets/:id         # 删除资产
```

**内容管理**
```http
GET    /admin/api/content/policies   # 获取政策列表
POST   /admin/api/content/policies   # 创建政策
PUT    /admin/api/content/policies/:id    # 更新政策
DELETE /admin/api/content/policies/:id    # 删除政策

GET    /admin/api/content/faqs       # 获取FAQ列表
POST   /admin/api/content/faqs       # 创建FAQ
PUT    /admin/api/content/faqs/:id   # 更新FAQ
DELETE /admin/api/content/faqs/:id   # 删除FAQ

GET    /admin/api/content/stories    # 获取故事列表
POST   /admin/api/content/stories/:id/approve  # 审核通过
POST   /admin/api/content/stories/:id/reject   # 审核拒绝
DELETE /admin/api/content/stories/:id          # 删除故事
```

#### 统一响应格式
```json
{
  "success": true,
  "message": "操作成功",
  "data": { ... }
}
```

### 7. 系统安全性和数据隐私保护

#### 安全措施

1. **认证和授权**
   - Flask-Login会话管理
   - 密码加密存储（bcrypt）
   - CSRF保护（Flask-WTF）
   - 基于角色的访问控制

2. **数据加密**
   - 用户密码使用werkzeug.security加密
   - 数字资产密码使用AES加密（cryptography库）

3. **输入验证**
   - 表单数据验证
   - SQL注入防护（ORM参数化查询）
   - XSS防护（模板自动转义）

4. **会话安全**
   - 安全的密钥配置
   - 会话超时设置
   - HTTPS支持（生产环境）

5. **权限控制**
   - 装饰器权限检查
   - 用户级别数据隔离
   - 操作日志记录（可扩展）

6. **数据隐私**
   - 敏感信息加密存储
   - 密码字段掩码显示
   - 个人信息访问控制

---

## 技术栈

### 后端
- Flask 3.0.0 - Web框架
- Flask-SQLAlchemy 3.1.1 - ORM
- Flask-Login 0.6.3 - 用户认证
- Flask-WTF 1.2.1 - 表单处理和CSRF
- Werkzeug 3.0.1 - 密码加密
- cryptography 41.0.0 - 数据加密

### 前端
- Bootstrap 5.3.0 - UI框架
- Chart.js 4.4.0 - 数据可视化
- Bootstrap Icons - 图标库

### 数据库
- SQLite - 开发环境
- PostgreSQL - 生产环境（通过Render）

---

## 部署指南

### 1. 本地部署

#### 步骤1: 安装依赖
```bash
pip install -r requirements.txt
```

#### 步骤2: 创建管理员账户
```bash
python create_admin.py
```

#### 步骤3: 启动应用
```bash
python app.py
```

#### 步骤4: 访问后台
```
http://localhost:5000/admin
```

### 2. 生产部署（Render）

#### 更新requirements.txt
```bash
git add requirements.txt
git commit -m "Add backend management system"
git push
```

#### 创建管理员
在Render Shell中执行:
```bash
python create_admin.py
```

#### 访问后台
```
https://your-app.onrender.com/admin
```

---

## 使用指南

### 管理员登录
1. 访问后台地址
2. 使用管理员账户登录
3. 进入仪表盘

### 用户管理
1. 查看用户列表
2. 点击"添加用户"创建新用户
3. 点击操作按钮编辑或删除用户
4. 使用搜索和筛选功能查找用户

### 数据统计
1. 查看仪表盘概览
2. 查看增长趋势图表
3. 查看资产分类分布
4. 查看系统活动统计

### 内容管理
1. 管理平台政策
2. 管理FAQ
3. 审核用户故事

---

## 扩展功能建议

### 短期扩展
- [ ] 操作日志记录
- [ ] 数据导出功能
- [ ] 批量操作
- [ ] 高级搜索

### 中期扩展
- [ ] 审计日志
- [ ] 数据备份和恢复
- [ ] 系统监控和告警
- [ ] 性能分析工具

### 长期扩展
- [ ] 多租户支持
- [ ] API密钥管理
- [ ] 第三方集成
- [ ] 自动化任务

---

## API文档

完整的API文档请参考: `ADMIN_API_DOCUMENTATION.md`

---

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0.0 | 2026-02-11 | 初始版本 |
| | - 用户管理 | |
| | - 数字资产管理 | |
| | - 数字遗嘱管理 | |
| | - 内容管理 | |
| | - 数据统计可视化 | |
| | - RESTful API | |

---

## 联系方式

如有问题或建议，请联系开发团队。
