# 部署问题排查指南

## 常见部署错误及解决方案

### 错误 1: Getting requirements to build wheel: finished with status 'error'

**错误信息：**
```
Getting requirements to build wheel: finished with status 'error'
error: subprocess-exited-with-error
note: This error originates from a subprocess, and is likely not a problem with pip.
```

**原因分析：**
- 某些依赖包需要编译 C 扩展
- 缺少构建工具或依赖
- Python 版本不兼容

**解决方案：**

1. **已修复：更新了 requirements.txt**
   - 添加了构建依赖（setuptools、wheel）
   - 使用更灵活的版本号（>= 而不是 ==）
   - 添加了注释说明每个包的用途

2. **如果问题仍然存在，尝试以下方法：**

   **方法一：清理缓存重新部署**
   ```bash
   # 在 Render 控制台中
   # 1. 进入 Web Service 设置
   # 2. 点击 "Manual Deploy"
   # 3. 选择 "Clear build cache & deploy"
   ```

   **方法二：检查 Python 版本**
   - 确保 render.yaml 中的 Python 版本正确
   - 推荐使用 Python 3.9 或 3.10

   **方法三：简化依赖**
   - 如果某些包不是必需的，可以暂时移除
   - 优先部署核心功能

### 错误 2: ModuleNotFoundError: No module named 'xxx'

**错误信息：**
```
ModuleNotFoundError: No module named 'cryptography'
```

**解决方案：**

1. **检查 requirements.txt**
   - 确保所有必需的包都已列出
   - 版本号格式正确

2. **重新部署**
   ```bash
   # 推送更新到 GitHub
   git add requirements.txt
   git commit -m "Fix dependencies"
   git push
   ```

3. **查看构建日志**
   - 在 Render 控制台查看详细的安装日志
   - 确认哪个包安装失败

### 错误 3: Database connection error

**错误信息：**
```
sqlite3.OperationalError: unable to open database file
```

**解决方案：**

1. **确保已运行初始化脚本**
   ```bash
   # 在 Render Shell 中执行
   python init_db.py
   ```

2. **检查数据库路径**
   - 确认 DATABASE_URL 环境变量正确
   - 应该是：`sqlite:////opt/render/project/data/digital_heritage.db`

3. **检查数据目录权限**
   ```bash
   # 在 Render Shell 中
   ls -la /opt/render/project/data/
   ```

### 错误 4: Application not responding / 502 Bad Gateway

**原因分析：**
- 应用正在启动中（冷启动）
- 应用崩溃
- 端口配置错误

**解决方案：**

1. **等待冷启动完成**
   - 免费计划的冷启动需要 30-60 秒
   - 这是正常现象，请耐心等待

2. **查看应用日志**
   ```bash
   # 在 Render 控制台查看 Logs
   # 检查是否有错误信息
   ```

3. **检查端口配置**
   - 确保应用监听在正确的端口
   - Render 会自动设置 PORT 环境变量

### 错误 5: Static files not loading (404)

**错误信息：**
静态文件（CSS、JS）返回 404 错误

**解决方案：**

1. **检查 static 目录结构**
   ```bash
   # 确保目录存在
   ls -la static/
   ls -la static/css/
   ls -la static/js/
   ```

2. **检查模板中的路径**
   - 确保 URL 路径使用 `url_for()` 或正确的相对路径

3. **清除浏览器缓存**
   - 按 Ctrl+Shift+R 强制刷新

### 错误 6: Permission denied

**错误信息：**
```
PermissionError: [Errno 13] Permission denied: '/opt/render/project/data'
```

**解决方案：**

1. **检查目录权限**
   ```bash
   # 在 Render Shell 中
   chmod 755 /opt/render/project/data
   ```

2. **确保目录由应用创建**
   - 让应用在启动时自动创建目录
   - 不要手动创建

## 部署检查清单

在部署前，请确认以下项目：

### 代码检查
- [ ] 所有文件已提交到 Git
- [ ] .gitignore 文件已配置
- [ ] 没有提交敏感信息（密码、密钥）
- [ ] requirements.txt 已更新

### 配置检查
- [ ] render.yaml 配置正确
- [ ] Procfile 存在且正确
- [ ] config.py 生产环境配置正确
- [ ] 环境变量已设置

### 数据库检查
- [ ] init_db.py 存在
- [ ] 数据库路径配置正确
- [ ] 持久化磁盘已配置

### 测试检查
- [ ] 本地测试通过
- [ ] 所有依赖可以正常安装
- [ ] 应用可以正常启动
- [ ] 核心功能正常工作

## 性能优化建议

### 1. 减少启动时间
- 使用更少的依赖包
- 优化数据库查询
- 延迟加载非必需模块

### 2. 减少内存使用
- 使用生成器而不是列表
- 及时释放大对象
- 优化图片处理

### 3. 避免休眠
- 使用 UptimeRobot 定期访问
- 设置 cron 任务保持活跃
- 升级到付费计划（如需要）

## 获取帮助

### 1. 查看日志
```bash
# Render 控制台
# Logs 标签页
```

### 2. 进入 Shell
```bash
# Render 控制台
# Shell 标签页
# 可以执行命令排查问题
```

### 3. 常用调试命令
```bash
# 检查 Python 版本
python --version

# 检查已安装的包
pip list

# 检查数据库
ls -la /opt/render/project/data/

# 测试应用启动
python app.py

# 检查环境变量
env | grep FLASK
env | grep DATABASE
```

### 4. 联系支持
- Render 文档：https://render.com/docs
- Render 状态：https://status.render.com
- Render 支持：support@render.com

## 成功部署的标志

当您看到以下情况时，说明部署成功：

1. ✅ Web Service 状态显示为 "Live"
2. ✅ 可以访问网站 URL
3. ✅ 首页正常加载
4. ✅ 可以注册和登录
5. ✅ 核心功能正常工作
6. ✅ 没有错误日志

## 常见问题 FAQ

### Q1: 为什么应用总是休眠？
A: 这是免费计划的正常行为。15 分钟无访问后会自动休眠。可以使用 UptimeRobot 保持活跃。

### Q2: 数据会丢失吗？
A: 不会。数据库存储在持久化磁盘中，数据会保留。

### Q3: 可以升级到付费计划吗？
A: 可以。在 Render 控制台可以随时升级。

### Q4: 支持自定义域名吗？
A: 支持。在 Settings 中添加自定义域名即可。

### Q5: 如何备份数据？
A: 可以在 Shell 中手动备份数据库文件，或使用 Render 的自动备份功能（付费计划）。

---

**最后更新**：2026年
**适用版本**：V1.0
