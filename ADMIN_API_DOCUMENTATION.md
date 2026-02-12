# 后台管理系统 API 文档

## 基础信息

- **Base URL**: `/api/admin` (前端接口)
- **认证方式**: Session-based (通过Flask-Login)
- **数据格式**: JSON

## 统一响应格式

### 成功响应
```json
{
  "success": true,
  "message": "操作成功",
  "data": { ... }
}
```

### 分页响应
```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "total": 100,
    "page": 1,
    "per_page": 20,
    "pages": 5
  }
}
```

### 错误响应
```json
{
  "success": false,
  "message": "错误描述"
}
```

---

## API 端点

### 1. 统计数据

#### 1.1 获取仪表盘统计
```
GET /admin/api/stats
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "users": {
      "total": 150,
      "active": 145,
      "admin": 3,
      "new_week": 12,
      "active_week": 48
    },
    "assets": {
      "total": 450,
      "by_category": {
        "社交": 180,
        "金融": 120,
        "记忆": 90,
        "虚拟财产": 60
      }
    },
    "wills": {
      "total": 85,
      "by_status": {
        "draft": 65,
        "confirmed": 18,
        "archived": 2
      }
    },
    "content": {
      "policies": 15,
      "faqs": 25,
      "stories": 40,
      "pending_stories": 5
    }
  }
}
```

#### 1.2 获取用户增长图表数据
```
GET /admin/api/charts/growth?days=30
```

**参数**:
- `days` (int): 天数，默认30

**响应示例**:
```json
{
  "success": true,
  "data": {
    "dates": ["2026-01-12", "2026-01-13", ...],
    "counts": [5, 8, 3, ...]
  }
}
```

#### 1.3 获取用户活动图表数据
```
GET /admin/api/charts/activity?days=7
```

**参数**:
- `days` (int): 天数，默认7

**响应示例**:
```json
{
  "success": true,
  "data": {
    "dates": ["01-05", "01-06", ...],
    "user_registrations": [5, 8, ...],
    "asset_created": [20, 15, ...],
    "will_created": [2, 3, ...]
  }
}
```

---

### 2. 用户管理

#### 2.1 获取用户列表
```
GET /admin/api/users?page=1&per_page=20&search=xxx&status=all
```

**参数**:
- `page` (int): 页码，默认1
- `per_page` (int): 每页数量，默认20
- `search` (string): 搜索关键词（用户名或邮箱）
- `status` (string): 状态筛选 (all|active|inactive|admin)

**响应示例**:
```json
{
  "success": true,
  "users": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "is_admin": true,
      "is_active": true,
      "created_at": "2026-01-01 10:00",
      "assets_count": 5,
      "wills_count": 2
    }
  ],
  "total": 150,
  "pages": 8,
  "current_page": 1
}
```

#### 2.2 获取用户详情
```
GET /admin/api/users/<user_id>
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "is_admin": true,
    "is_active": true,
    "created_at": "2026-01-01 10:00:00",
    "updated_at": "2026-01-15 14:30:00",
    "assets_count": 5,
    "wills_count": 2,
    "assets": [...],
    "wills": [...]
  }
}
```

#### 2.3 创建用户
```
POST /admin/api/users
Content-Type: application/json

{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "securepassword",
  "is_admin": false,
  "is_active": true
}
```

#### 2.4 更新用户
```
PUT /admin/api/users/<user_id>
Content-Type: application/json

{
  "username": "updated_user",
  "email": "updated@example.com",
  "password": "newpassword",
  "is_admin": false,
  "is_active": true
}
```

**说明**: 所有字段都是可选的，只更新提供的字段

#### 2.5 切换用户状态
```
POST /admin/api/users/<user_id>/toggle-status
```

**响应示例**:
```json
{
  "success": true,
  "message": "用户状态已更新为 禁用",
  "is_active": false
}
```

#### 2.6 删除用户
```
DELETE /admin/api/users/<user_id>
```

**注意**: 删除用户会同时删除其关联的数字资产和遗嘱

---

### 3. 数字资产管理

#### 3.1 获取资产列表
```
GET /admin/api/assets?page=1&per_page=20&search=xxx&category=all
```

**参数**:
- `page` (int): 页码，默认1
- `per_page` (int): 每页数量，默认20
- `search` (string): 搜索关键词（平台名称或账号）
- `category` (string): 分类筛选 (all|社交|金融|记忆|虚拟财产)

**响应示例**:
```json
{
  "success": true,
  "assets": [
    {
      "id": 1,
      "user_id": 5,
      "username": "user5",
      "platform_name": "微信",
      "account": "13800138000",
      "category": "社交",
      "notes": "主要社交账号",
      "created_at": "2026-01-10"
    }
  ],
  "total": 450,
  "pages": 23,
  "current_page": 1
}
```

#### 3.2 删除资产
```
DELETE /admin/api/assets/<asset_id>
```

---

### 4. 数字遗嘱管理

#### 4.1 获取遗嘱列表
```
GET /admin/api/wills?page=1&per_page=20&search=xxx&status=all
```

**参数**:
- `page` (int): 页码，默认1
- `per_page` (int): 每页数量，默认20
- `search` (string): 搜索关键词（标题或描述）
- `status` (string): 状态筛选 (all|draft|confirmed|archived)

**响应示例**:
```json
{
  "success": true,
  "wills": [
    {
      "id": 1,
      "user_id": 5,
      "username": "user5",
      "title": "我的数字遗产处理意愿",
      "description": "这是我的数字遗嘱描述...",
      "status": "draft",
      "created_at": "2026-01-10"
    }
  ],
  "total": 85,
  "pages": 5,
  "current_page": 1
}
```

#### 4.2 删除遗嘱
```
DELETE /admin/api/wills/<will_id>
```

---

### 5. 内容管理

#### 5.1 平台政策

##### 获取政策列表
```
GET /admin/api/content/policies
```

##### 创建政策
```
POST /admin/api/content/policies
Content-Type: application/json

{
  "platform_name": "微信",
  "policy_content": "微信账户不支持继承",
  "attitude": "明确禁止",
  "inherit_possibility": "低",
  "legal_basis": "根据服务协议",
  "customer_service": "400-670-0700",
  "risk_warning": "账户余额可能无法提取"
}
```

##### 更新政策
```
PUT /admin/api/content/policies/<policy_id>
Content-Type: application/json

{
  "platform_name": "微信",
  "policy_content": "更新后的内容",
  ...
}
```

##### 删除政策
```
DELETE /admin/api/content/policies/<policy_id>
```

#### 5.2 FAQ管理

##### 获取FAQ列表
```
GET /admin/api/content/faqs
```

##### 创建FAQ
```
POST /admin/api/content/faqs
Content-Type: application/json

{
  "question": "什么是数字遗产？",
  "answer": "数字遗产是指...",
  "category": "基础概念",
  "order": 1
}
```

##### 更新FAQ
```
PUT /admin/api/content/faqs/<faq_id>
Content-Type: application/json

{
  "question": "更新的问题",
  "answer": "更新的答案",
  "category": "基础概念",
  "order": 1
}
```

##### 删除FAQ
```
DELETE /admin/api/content/faqs/<faq_id>
```

#### 5.3 故事管理

##### 获取故事列表
```
GET /admin/api/content/stories?page=1&per_page=20&status=all
```

**参数**:
- `page` (int): 页码，默认1
- `per_page` (int): 每页数量，默认20
- `status` (string): 状态筛选 (all|pending|approved|rejected)

##### 审核通过故事
```
POST /admin/api/content/stories/<story_id>/approve
```

##### 审核拒绝故事
```
POST /admin/api/content/stories/<story_id>/reject
```

##### 删除故事
```
DELETE /admin/api/content/stories/<story_id>
```

---

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未登录或权限不足 |
| 403 | 无权限访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 安全特性

1. **CSRF保护**: 所有POST请求需要CSRF令牌
2. **身份验证**: 所有API需要管理员权限
3. **数据加密**: 密码使用bcrypt加密
4. **SQL注入防护**: 使用ORM，参数化查询

---

## 使用示例

### JavaScript (Fetch API)

```javascript
// 获取用户列表
fetch('/admin/api/users?page=1&per_page=20', {
  headers: {
    'Content-Type': 'application/json'
  }
})
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log('用户列表:', data.users);
    }
  });

// 创建用户
fetch('/admin/api/users', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCookie('csrf_token')
  },
  body: JSON.stringify({
    username: 'newuser',
    email: 'newuser@example.com',
    password: 'securepassword'
  })
})
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log('创建成功:', data.message);
    }
  });
```

### Axios

```javascript
// 获取统计数据
axios.get('/admin/api/stats')
  .then(response => {
    if (response.data.success) {
      console.log('统计数据:', response.data.data);
    }
  });

// 更新用户
axios.put(`/admin/api/users/${userId}`, {
  username: 'updated_user',
  is_active: false
}, {
  headers: {
    'X-CSRFToken': getCookie('csrf_token')
  }
})
  .then(response => {
    if (response.data.success) {
      console.log('更新成功');
    }
  });
```

---

## 版本历史

- **v1.0** (2026-02-11): 初始版本
  - 用户管理API
  - 资产管理API
  - 遗嘱管理API
  - 内容管理API
  - 统计数据API
