# 🔧 字体加载问题修复指南

## 📊 问题分析

从部署日志中发现的问题：

### ❌ 字体加载失败的原因

1. **系统字体未找到**：
   - `fonts-noto-cjk` 没有成功安装
   - 可能包名不正确或包不存在

2. **下载备用字体失败**：
   - **Source Han Sans (OTF)**：ReportLab 不支持 OTF 格式
     ```
     Failed to download font: TTF file "/tmp/tmp8ns91jmj/font.otf": postscript outlines are not supported
     ```

   - **Noto CJK (ZIP)**：下载链接失效
     ```
     Failed to download font from zip: HTTP Error 404: Not Found
     ```

3. **最终结果**：使用默认字体，中文会显示为方框

### 🔍 根本原因

1. `fonts-noto-cjk` 包可能在 Render 环境中不存在
2. OTF 格式不被 ReportLab 支持（只支持 TTF/TTC）
3. GitHub 字体下载链接可能失效或需要重定向

---

## ✅ 修复方案

### 修复 1：优化 render.yaml

**修改内容**：
- 移除 `fonts-noto-cjk`（可能不存在）
- 只保留可靠的 `fonts-wqy-microhei` 和 `fonts-wqy-zenhei`

**修改后的 render.yaml**：
```yaml
buildCommand: apt-get update && apt-get install -y fonts-wqy-microhei fonts-wqy-zenhei && pip install -r requirements.txt
```

### 修复 2：优化 fonts.py

**修改内容**：
1. **调整字体优先级**：文泉驿优先（更可靠）
2. **移除 OTF 格式下载**：只支持 TTF/TTC
3. **更新下载链接**：使用更可靠的源
4. **改进错误处理**：更详细的日志

**关键改进**：
- 优先使用系统已安装的文泉驿字体
- 如果系统字体不可用，尝试下载 TTF 版本
- 移除所有 OTF 格式下载
- 添加文件大小验证

---

## 🚀 部署修复步骤

### 步骤 1：推送修复代码

```bash
# 进入项目目录
cd "c:\Users\admin\Desktop\demo - codebuddy"

# 查看状态
git status

# 如果有未推送的提交，先推送
git push origin main
```

**如果推送失败（网络问题）**：
- 检查网络连接
- 尝试使用 VPN
- 或稍后重试

### 步骤 2：等待自动部署

推送成功后，Render 会自动检测并开始部署。

### 步骤 3：监控部署日志

**查看 Build Logs**：
1. 访问 [https://dashboard.render.com](https://dashboard.render.com)
2. 找到你的 Web Service
3. 点击 **Logs** → **Build Logs**

**预期看到的日志**：
```
✓ Installing fonts-wqy-microhei...
✓ Installing fonts-wqy-zenhei...
✓ Installing Python dependencies...
✓ Build completed successfully
```

**查看 Runtime Logs**：
1. 选择 **Runtime Logs**
2. 查找字体加载日志

**预期成功的日志**：
```
[OK] Successfully registered system font: /usr/share/fonts/truetype/wqy/wqy-microhei.ttc
```

**如果仍然失败**：
```
[WARN] No system Chinese font found, attempting to download open-source font...
Downloading font from https://github.com/googlefonts/wqy-microhei/raw/master/wqy-microhei.ttc...
Font downloaded successfully: /tmp/xxx/font.ttc
File size: 12345678 bytes
[OK] Successfully downloaded and registered font: WQYMicroHei
```

---

## 🔍 验证修复

### 验证清单

部署完成后，请验证：

1. **Render Dashboard 检查**：
   - [ ] 部署状态为 `Live`
   - [ ] Health Check 通过
   - [ ] Build Logs 无错误
   - [ ] Runtime Logs 看到字体加载成功的日志

2. **应用功能检查**：
   - [ ] 首页正常加载
   - [ ] 用户登录功能正常
   - [ ] 创建遗嘱功能正常

3. **PDF 中文显示检查（重点）**：
   - [ ] 创建包含中文的遗嘱
   - [ ] 生成 PDF 文件
   - [ ] 下载并打开 PDF
   - [ ] **验证中文正确显示（无方框、无乱码）**

---

## 🐛 如果问题仍然存在

### 方案 A：手动安装字体

1. 在 Render Dashboard 打开 Shell：
   - Web Service → Shell

2. 运行以下命令：

```bash
# 更新包列表
apt-get update

# 安装文泉驿字体
apt-get install -y fonts-wqy-microhei fonts-wqy-zenhei

# 验证字体已安装
fc-list | grep -i "wqy"

# 刷新字体缓存
fc-cache -fv

# 查看字体文件
ls -la /usr/share/fonts/truetype/wqy/

# 退出 Shell
exit
```

3. 在 Render Dashboard 触发手动部署：
   - Web Service → Manual Deploy → Clear build cache & deploy

### 方案 B：检查 Render 构建配置

1. 在 Render Dashboard：
   - Web Service → Settings

2. 检查 Build Command：
   ```
   apt-get update && apt-get install -y fonts-wqy-microhei fonts-wqy-zenhei && pip install -r requirements.txt
   ```

3. 如果不正确，修改后点击 **Save Changes**

4. 触发手动部署

### 方案 C：使用 Render Shell 手动测试字体

1. 打开 Render Shell

2. 运行 Python 测试：

```python
# 创建测试脚本
cat > test_font.py << 'EOF'
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# 测试字体路径
font_paths = [
    '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
    '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
]

for path in font_paths:
    if os.path.exists(path):
        try:
            pdfmetrics.registerFont(TTFont('TestFont', path, subfontIndex=0))
            print(f"[OK] Font loaded: {path}")
        except Exception as e:
            print(f"[FAIL] Failed to load {path}: {e}")
    else:
        print(f"[NOT FOUND] {path}")

# 列出所有字体
print("\nAll WQY fonts:")
import subprocess
result = subprocess.run(['fc-list', ':family', '|', 'grep', '-i', 'wqy'],
                       shell=True, capture_output=True, text=True)
print(result.stdout)
EOF

# 运行测试
python test_font.py
```

---

## 📝 修复总结

### 修改的文件

| 文件 | 修改内容 |
|------|---------|
| `render.yaml` | 移除 `fonts-noto-cjk`，只保留文泉驿字体 |
| `utils/fonts.py` | 优化字体加载逻辑，移除 OTF 支持，更新下载链接 |

### 预期效果

✅ 字体安装成功率提高（使用可靠的文泉驿）
✅ 字体下载成功率提高（使用 TTF/TTC 格式）
✅ PDF 中文应该能正确显示
✅ 更详细的错误日志便于调试

### 如果修复成功

你会在 Runtime Logs 中看到：
```
[OK] Successfully registered system font: /usr/share/fonts/truetype/wqy/wqy-microhei.ttc
```

然后尝试生成 PDF，中文应该能正确显示。

---

## 🎯 下一步

1. **推送修复代码**到 GitHub
2. **等待自动部署**完成
3. **查看部署日志**确认字体加载成功
4. **测试 PDF 生成**验证中文显示

如果问题仍然存在，请：
- 查看 Runtime Logs 的详细错误信息
- 使用 Render Shell 手动安装字体
- 参考"如果问题仍然存在"部分的解决方案

---

*最后更新：2026-02-14*
