# Render 数据持久化保证

## ✅ 数据不会丢失

### 重要澄清

**Render 休眠 ≠ 数据丢失**

Render 免费版的数据持久化机制：
- ✅ 数据库文件持久化存储在磁盘上
- ✅ 用户账号信息永久保存
- ✅ 数字资产数据永久保存
- ✅ 数字遗嘱数据永久保存
- ✅ 所有用户数据都会保留

---

## 📋 数据持久化配置

### 1. 数据库存储位置

**SQLite 数据库路径**：
```python
# config.py
SQLALCHEMY_DATABASE_URI = 'sqlite:////opt/render/project/data/digital_heritage.db'
```

**数据目录配置**：
```yaml
# render.yaml
disk:
  name: data
  mountPath: /opt/render/project/data
  sizeGB: 1
```

### 2. 自动初始化

应用启动时自动初始化数据库：
```python
@app.before_request
def initialize_database():
    """初始化数据库"""
    if not hasattr(initialize_database, 'initialized'):
        try:
            with app.app_context():
                # 确保数据目录存在
                db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
                db_dir = os.path.dirname(db_path)

                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir, exist_ok=True)

                # 创建所有表
                db.create_all()

                # 初始化示例数据
                initialize_sample_data()

            initialize_database.initialized = True
        except Exception as e:
            print(f"Database initialization error: {e}")
            initialize_database.initialized = True
```

---

## 🔍 验证数据持久化

### 方法 1：通过应用验证

1. **注册账号并添加数据**
   ```
   - 注册一个测试账号
   - 添加几个数字资产
   - 创建数字遗嘱
   ```

2. **等待休眠**
   ```
   - 等待 15 分钟不访问应用
   - 应用会自动休眠
   ```

3. **重新访问**
   ```
   - 访问网站
   - 等待 30-60 秒冷启动
   - 使用之前的账号登录
   - 检查数据是否还在
   ```

4. **预期结果**
   ```
   ✅ 账号可以登录
   ✅ 数字资产都在
   ✅ 数字遗嘱都在
   ✅ 所有数据完整
   ```

### 方法 2：通过数据库验证

如果有 Shell 访问权限（付费计划）：

```bash
# 查看数据库文件
ls -lh /opt/render/project/data/digital_heritage.db

# 查看数据库内容
sqlite3 /opt/render/project/data/digital_heritage.db

# 查询用户表
SELECT * FROM users;

# 查询数字资产表
SELECT * FROM digital_assets;

# 查询数字遗嘱表
SELECT * FROM digital_wills;
```

### 方法 3：使用测试脚本

运行 `test_database.py`：

```bash
cd C:\Users\admin\Desktop\demo
python test_database.py
```

**预期输出**：
```
[OK] User                 - 记录数: X
[OK] DigitalAsset         - 记录数: X
[OK] DigitalWill          - 记录数: X
[OK] PlatformPolicy       - 记录数: 3
[OK] Story                - 记录数: 2
[OK] FAQ                  - 记录数: 12
```

---

## 💾 数据持久化原理

### Render 免费版存储

**持久化磁盘**：
- ✅ 1GB 持久化磁盘
- ✅ 数据在休眠期间保留
- ✅ 数据在重新部署时保留
- ✅ 除非手动删除，否则永久保留

**临时存储**：
- ❌ 内存中的数据（会丢失）
- ❌ 临时文件（会丢失）
- ❌ 未持久化到磁盘的数据（会丢失）

### SQLite 数据库

**特点**：
- ✅ 文件型数据库
- ✅ 所有数据存储在单个文件中
- ✅ 文件持久化到磁盘
- ✅ 休眠不影响数据
- ✅ 重新部署不影响数据

**配置**：
```python
# 使用绝对路径确保持久化
SQLALCHEMY_DATABASE_URI = 'sqlite:////opt/render/project/data/digital_heritage.db'
```

---

## 🛡️ 数据保护措施

### 1. 定期备份（推荐）

**本地备份**：
```bash
# 在 Render Shell 中（如果有权限）
cp /opt/render/project/data/digital_heritage.db /opt/render/project/data/backup_$(date +%Y%m%d).db
```

**自动备份脚本**：
```python
# backup.py
import shutil
from datetime import datetime

def backup_database():
    source = '/opt/render/project/data/digital_heritage.db'
    backup_dir = '/opt/render/project/data/backups'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'{backup_dir}/backup_{timestamp}.db'

    shutil.copy2(source, backup_file)
    print(f'Backup created: {backup_file}')
```

### 2. 数据导出

**导出为 SQL**：
```bash
sqlite3 /opt/render/project/data/digital_heritage.db .dump > backup.sql
```

**导出为 Excel**：
```python
# 在应用中添加导出功能
@app.route('/export/data')
@login_required
def export_data():
    # 导出所有数据为 Excel
    # ...
```

### 3. 监控数据大小

```python
import os

def check_database_size():
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    size = os.path.getsize(db_path)
    size_mb = size / (1024 * 1024)
    print(f'Database size: {size_mb:.2f} MB')
```

---

## ❌ 常见误解澄清

### 误解 1：休眠会删除数据

**真相**：
- ❌ 休眠不会删除数据
- ✅ 数据永久存储在磁盘上
- ✅ 休眠只是暂停应用运行

### 误解 2：需要重新注册账号

**真相**：
- ❌ 不需要重新注册账号
- ✅ 账号信息保存在数据库中
- ✅ 使用之前的账号密码即可登录

### 误解 3：冷启动会清空数据

**真相**：
- ❌ 冷启动不会清空数据
- ✅ 只是重新启动应用进程
- ✅ 数据库文件不受影响

### 误解 4：15 分钟后数据会丢失

**真相**：
- ❌ 15 分钟后数据不会丢失
- ✅ 只是应用进入休眠状态
- ✅ 数据永久保留

---

## 📊 数据持久化测试

### 测试步骤

1. **初始状态**
   ```
   - 访问网站
   - 注册账号：testuser
   - 添加 3 个数字资产
   - 创建 2 个数字遗嘱
   ```

2. **等待休眠**
   ```
   - 等待 15 分钟
   - 确认应用已休眠
   ```

3. **唤醒应用**
   ```
   - 访问网站
   - 等待冷启动完成（30-60 秒）
   ```

4. **验证数据**
   ```
   - 使用 testuser 登录
   - 检查数字资产数量（应该是 3）
   - 检查数字遗嘱数量（应该是 2）
   ```

5. **预期结果**
   ```
   ✅ 可以成功登录
   ✅ 数字资产数量正确
   ✅ 数字遗嘱数量正确
   ✅ 所有数据完整无误
   ```

---

## 🎯 总结

### 数据持久化保证

| 项目 | 状态 | 说明 |
|------|------|------|
| 用户账号 | ✅ 永久保存 | 存储在数据库中 |
| 数字资产 | ✅ 永久保存 | 存储在数据库中 |
| 数字遗嘱 | ✅ 永久保存 | 存储在数据库中 |
| 平台政策 | ✅ 永久保存 | 存储在数据库中 |
| FAQ 数据 | ✅ 永久保存 | 存储在数据库中 |

### 数据持久化机制

1. **持久化磁盘** - Render 提供 1GB 持久化存储
2. **SQLite 数据库** - 文件型数据库，数据保存在单个文件中
3. **自动初始化** - 应用启动时自动创建和初始化数据库
4. **数据备份** - 建议定期备份数据库文件

### 最佳实践

1. ✅ 定期测试数据持久化
2. ✅ 定期备份数据库文件
3. ✅ 使用 UptimeRobot 防止频繁休眠
4. ✅ 监控数据库大小
5. ✅ 记录重要数据

---

## 📞 如果数据真的丢失了

虽然理论上不会丢失，但如果遇到意外：

1. **检查 Render 日志** - 查看是否有错误
2. **检查磁盘空间** - 确认磁盘未满
3. **检查数据库文件** - 确认文件存在
4. **联系 Render 支持** - 寻求技术帮助
5. **使用备份恢复** - 如果有备份文件

---

**文档日期**：2026-02-10
**版本**：V1.0
**状态**：✅ 数据持久化有保证
