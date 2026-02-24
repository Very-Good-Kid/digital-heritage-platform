# 配置本地连接Neon数据库指南

## 概述

本指南将帮助您配置本地开发环境直接连接到Neon PostgreSQL数据库,实现本地开发与生产环境的数据库同步。

## 前置条件

1. 已有Neon数据库账户
2. 已创建Neon PostgreSQL数据库实例
3. Python环境已配置

## 配置步骤

### 步骤1: 获取Neon数据库连接字符串

1. 登录 [Neon控制台](https://console.neon.tech)
2. 选择您的项目
3. 点击"Connection Details"或"Connection String"
4. 复制连接字符串,格式如下:
   ```
   postgres://username:password@ep-xxx.region.aws.neon.tech/database_name?sslmode=require
   ```

### 步骤2: 配置环境变量

1. 打开项目根目录下的 `.env` 文件
2. 将您的Neon连接字符串粘贴到 `DATABASE_URL` 后面:
   ```bash
   DATABASE_URL=postgres://username:password@ep-xxx.region.aws.neon.tech/database_name?sslmode=require
   SECRET_KEY=your-secret-key-change-this-in-production
   FLASK_ENV=development
   ```
3. 保存文件

**注意**: 请将 `username`, `password`, `ep-xxx.region.aws.neon.tech`, `database_name` 替换为您实际的连接信息。

### 步骤3: 测试数据库连接

运行测试脚本验证连接是否成功:

```bash
python test_neon_connection.py
```

如果连接成功,您将看到类似以下输出:
```
✅ 连接成功!
- PostgreSQL版本: PostgreSQL 15.x on x86_64...
- 现有数据表: X 个
```

如果连接失败,请检查:
- DATABASE_URL格式是否正确
- 网络连接是否正常
- Neon数据库凭证是否正确

### 步骤4: 初始化Neon数据库结构

如果Neon数据库是全新的,需要先初始化数据库表结构:

```bash
python init_db.py
```

这将创建所有必要的数据表并初始化基础数据。

### 步骤5: 同步本地数据到Neon

将本地SQLite数据库中的数据同步到Neon数据库:

```bash
python sync_to_neon.py
```

此脚本将同步以下数据:
- 用户数据 (User)
- FAQ数据
- 资产分类 (AssetCategory)
- 平台政策 (PlatformPolicy)

同步完成后,您将看到每个数据表的同步统计信息。

### 步骤6: 启动应用

现在您可以启动应用,它将使用Neon数据库:

```bash
python app.py
```

访问 `http://localhost:5000` 验证应用是否正常运行。

## 常用命令

### 测试连接
```bash
python test_neon_connection.py
```

### 初始化数据库
```bash
python init_db.py
```

### 同步数据
```bash
python sync_to_neon.py
```

### 导出FAQ数据
```bash
python sync_faq.py
```

### 检查本地数据库
```bash
python check_database.py
```

## 数据同步策略

### 开发流程

1. **本地开发**: 直接操作Neon数据库
2. **实时同步**: 所有更改立即反映到Neon数据库
3. **生产部署**: 生产环境使用同一个Neon数据库

### 数据一致性

- 本地和生产环境使用同一个Neon数据库
- 无需手动同步,数据自动保持一致
- 建议定期备份Neon数据库

## 故障排除

### 问题1: 连接超时

**错误信息**: `could not connect to server: Connection timed out`

**解决方案**:
- 检查网络连接
- 确认Neon数据库是否在线
- 检查防火墙设置

### 问题2: SSL连接错误

**错误信息**: `SSL connection has been closed unexpectedly`

**解决方案**:
- 确保DATABASE_URL包含 `?sslmode=require`
- 检查config.py中的SSL配置

### 问题3: 认证失败

**错误信息**: `password authentication failed`

**解决方案**:
- 检查DATABASE_URL中的用户名和密码是否正确
- 在Neon控制台重置数据库密码

### 问题4: 表不存在

**错误信息**: `relation "table_name" does not exist`

**解决方案**:
- 运行 `python init_db.py` 初始化数据库表结构

## 安全建议

1. **不要提交.env文件到Git仓库**
   - .env文件已在.gitignore中
   - 确保不要意外提交敏感信息

2. **使用强密码**
   - Neon数据库密码应足够复杂
   - 定期更换密码

3. **限制访问权限**
   - 在Neon控制台配置IP白名单(可选)
   - 使用最小权限原则

4. **定期备份**
   - Neon提供自动备份功能
   - 建议定期导出重要数据

## 下一步

配置完成后,您可以:

1. 开始使用Neon数据库进行开发
2. 享受实时数据同步的便利
3. 部署到生产环境时无需额外配置

## 相关文档

- [Neon官方文档](https://neon.tech/docs)
- [项目部署指南](DEPLOYMENT_GUIDE.md)
- [数据同步指南](SYNC_GUIDE.md)

## 技术支持

如遇问题,请检查:
1. 本指南的故障排除部分
2. 项目README.md
3. Neon官方文档
