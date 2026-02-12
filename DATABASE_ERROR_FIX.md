# 数据库错误修复指南

## 错误信息
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) unable to open database file
```

## 错误原因
开发环境下，`instance` 目录在配置加载时不存在，导致数据库路径指向不存在的目录。

## 已修复
✅ 已修改 `config.py`，在开发环境配置中也添加了目录创建逻辑。

## 立即解决步骤

### 方法1：重启应用（推荐）

```bash
# 停止当前运行的应用 (Ctrl+C)

# 重新启动
python app.py
```

### 方法2：手动创建目录

```bash
# 确保instance目录存在
cd "c:\Users\admin\Desktop\demo - codebuddy"
if not exist instance mkdir instance
```

### 方法3：检查数据库文件

```bash
# 查看数据库文件是否存在
dir "c:\Users\admin\Desktop\demo - codebuddy\instance\digital_heritage.db"
```

## 验证修复

1. 启动应用
2. 访问 `http://localhost:5000`
3. ✅ 应用应该正常运行
4. ✅ 数据库应该正常连接

## 技术说明

### 修复前的问题
```python
class DevelopmentConfig(Config):
    DEBUG = True
    # ❌ 使用了基类的DATA_DIR，但基类没有创建目录
    db_path = os.path.join(Config.DATA_DIR, 'digital_heritage.db')
```

### 修复后的代码
```python
class DevelopmentConfig(Config):
    DEBUG = True

    # ✅ 在子类中定义DATA_DIR
    DATA_DIR = 'instance'

    # ✅ 确保目录存在
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)

    # ✅ 使用子类的DATA_DIR
    db_path = os.path.join(DATA_DIR, 'digital_heritage.db')
```

## 环境说明

### 开发环境
- **目录**: `instance/`
- **数据库**: `instance/digital_heritage.db`
- **自动创建**: ✅ 是

### 生产环境 (Render)
- **目录**: `/opt/render/project/data/`
- **数据库**: `/opt/render/project/data/digital_heritage.db`
- **自动创建**: ✅ 是

## 常见问题

### Q1: 为什么会出现这个错误？
A: 在配置类加载时，Python会立即执行类级别的代码。如果目录不存在，数据库路径就会指向不存在的路径。

### Q2: 修复后数据会丢失吗？
A: 不会。数据库文件仍然在 `instance/digital_heritage.db`，只是配置现在能正确找到它了。

### Q3: 需要重新初始化数据库吗？
A: 不需要。数据库文件已经存在，修复后可以直接使用。

## 部署到Render

修复后的代码已经准备好部署到Render：

```bash
cd "c:\Users\admin\Desktop\demo - codebuddy"
git add .
git commit -m "Fix: Database path issue in development environment"
git push origin main
```

---

**修复完成！** 🎉

现在应用应该可以正常启动了。
