# Render 部署配置说明

## 重要：不要使用 render-build.sh

由于Render免费版的限制，请直接在Render Dashboard中配置以下命令：

### Build Command
```
pip install -r requirements.txt
```

### Start Command
```
gunicorn app:app --bind 0.0.0.0:$PORT --workers 1
```

## 工作原理

1. **构建阶段**：只安装Python依赖，不需要root权限
2. **启动阶段**：应用自动下载和安装中文字体
3. **PDF生成**：使用运行时下载的中文字体

## 字体安装机制

应用会在首次启动时自动：
1. 尝试安装系统字体（会失败，但没关系）
2. 从Google Fonts下载Noto Sans SC字体到临时目录
3. 设置环境变量供PDF生成模块使用
4. 如果所有方法都失败，使用默认字体（会显示警告）

## 文件说明

- `install_fonts_runtime.py` - 运行时字体安装脚本
- `utils/fonts.py` - 字体管理模块（已更新）
- `app.py` - 已集成自动字体安装

## 部署步骤

1. 在Render Dashboard中设置Build Command和Start Command（如上所示）
2. 提交代码并推送
3. 等待部署完成
4. 查看日志确认字体安装成功

## 预期日志输出

```
[INFO] Setting up fonts for PDF generation...
[INFO] Attempting to install system fonts...
[WARN] No root permissions, skipping system font installation
[INFO] Downloading Chinese font to temporary directory...
[OK] Font downloaded: /tmp/fonts/NotoSansSC.woff2
[OK] Font setup completed successfully
```

## 故障排除

### 如果看到 "No Chinese font available" 警告
这是正常的，应用会继续运行，但中文可能显示为方框。

### 如果构建失败
1. 检查requirements.txt中的依赖是否都可用
2. 确保Python版本兼容（推荐3.11+）
3. 查看完整的错误日志

### 如果字体下载失败
1. 检查网络连接
2. Google Fonts CDN可能暂时不可用
3. 应用会自动重试

## 注意事项

- 字体文件约200KB，下载很快
- 字体缓存在临时目录，重启后需要重新下载
- 不需要任何系统权限
- 完全兼容Render免费版
