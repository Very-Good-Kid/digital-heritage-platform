# 🔧 手动安装字体指南 - Render Shell

## 📊 问题现状

从最新的部署日志看：

### ❌ 失败原因

1. **系统字体未安装**：`fonts-wqy-microhei` 没有成功安装
2. **所有下载链接失效**：
   - WQY MicroHei (GitHub raw): 404 Not Found
   - Noto Sans SC (GitHub raw): 404 Not Found

### 🔍 根本原因

- GitHub raw 链接可能被重定向或需要认证
- Render 的 apt-get 在 build 过程中可能没有正确安装字体包
- 自动下载方案不可靠

### ✅ 解决方案

**使用 Render Shell 手动安装字体**（最可靠的方法）

---

## 🚀 手动安装步骤

### 步骤 1：打开 Render Shell

1. 访问 [https://dashboard.render.com](https://dashboard.render.com)
2. 找到你的 Web Service：`digital-heritage-platform`
3. 点击进入服务详情页
4. 在右上角点击 **"Shell"** 按钮
5. 等待 Shell 连接成功

### 步骤 2：下载并运行安装脚本

在 Render Shell 中运行以下命令：

#### 方法 A：直接运行命令（推荐）

```bash
# 更新包列表
apt-get update

# 安装中文字体
apt-get install -y fonts-wqy-microhei fonts-wqy-zenhei

# 验证安装
ls -la /usr/share/fonts/truetype/wqy/

# 刷新字体缓存
fc-cache -fv

# 查看已安装的字体
fc-list | grep -i "wqy"
```

#### 方法 B：使用安装脚本

```bash
# 下载安装脚本
curl -o install_fonts.sh https://raw.githubusercontent.com/YOUR_USERNAME/digital-heritage-platform/main/install_fonts.sh

# 添加执行权限
chmod +x install_fonts.sh

# 运行安装脚本
./install_fonts.sh
```

**预期输出**：
```
=========================================
  中文字体安装脚本
=========================================

[1/4] 更新包列表...
...
[2/4] 安装中文字体...
Reading package lists... Done
...
[3/4] 验证字体安装...
✓ wqy-microhei 已安装
-rw-r--r-- 1 root root 4.2M /usr/share/fonts/truetype/wqy/wqy-microhei.ttc
✓ wqy-zenhei 已安装
-rw-r--r-- 1 root root 7.8M /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc
[4/4] 刷新字体缓存...
...
=========================================
  已安装的中文字体：
=========================================
/usr/share/fonts/truetype/wqy/wqy-microhei.ttc: WenQuanYi Micro Hei,文泉驿微米黑,文泉驛微米黑:style=Regular
/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc: WenQuanYi Zen Hei,文泉驿正黑,文泉驛正黑:style=Regular

=========================================
  安装完成！
=========================================
```

### 步骤 3：验证字体安装

在 Render Shell 中运行：

```bash
# 检查字体文件是否存在
ls -lh /usr/share/fonts/truetype/wqy/

# 查看字体列表
fc-list | grep -i "wqy"

# 测试 Python 字体加载
python3 << 'EOF'
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

font_path = '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc'
if os.path.exists(font_path):
    try:
        pdfmetrics.registerFont(TTFont('WQYMicroHei', font_path, subfontIndex=0))
        print("[OK] 字体加载成功！")
        print(f"字体路径: {font_path}")
    except Exception as e:
        print(f"[FAIL] 字体加载失败: {e}")
else:
    print(f"[FAIL] 字体文件不存在: {font_path}")
EOF
```

**预期输出**：
```
[OK] 字体加载成功！
字体路径: /usr/share/fonts/truetype/wqy/wqy-microhei.ttc
```

### 步骤 4：退出 Shell

```bash
exit
```

### 步骤 5：手动触发部署

1. 在 Render Dashboard 中
2. 找到你的 Web Service
3. 点击 **"Manual Deploy"** 按钮
4. 选择 **"Clear build cache & deploy"**
5. 等待部署完成（2-3 分钟）

### 步骤 6：验证修复

#### 查看 Runtime Logs

1. 在 Render Dashboard 中
2. 点击 **Logs** → **Runtime Logs**
3. 查找字体加载日志

**预期看到的日志**：
```
[OK] Successfully registered system font: /usr/share/fonts/truetype/wqy/wqy-microhei.ttc
```

#### 测试 PDF 生成

1. 访问你的应用：`https://digital-heritage-platform.onrender.com`
2. 登录账号
3. 创建一个包含中文的遗嘱
4. 点击"生成 PDF"按钮
5. 下载并打开 PDF 文件
6. **验证中文是否正确显示（无方框、无乱码）**

---

## 🐛 故障排除

### 问题 1：apt-get install 失败

**错误信息**：
```
E: Unable to locate package fonts-wqy-microhei
```

**解决方案**：

```bash
# 更新包列表
apt-get update

# 搜索可用的字体包
apt-cache search wqy

# 尝试安装其他中文字体包
apt-get install -y fonts-wqy-zenhei

# 或者安装完整的字体包
apt-get install -y fonts-wqy*
```

### 问题 2：字体文件存在但加载失败

**错误信息**：
```
[FAIL] Failed to register font: ...
```

**解决方案**：

```bash
# 检查字体文件权限
ls -la /usr/share/fonts/truetype/wqy/

# 如果权限不对，修复权限
chmod 644 /usr/share/fonts/truetype/wqy/*.ttc

# 刷新字体缓存
fc-cache -fv

# 重新测试
python3 << 'EOF'
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('WQYMicroHei', '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', subfontIndex=0))
print("[OK] 字体加载成功！")
EOF
```

### 问题 3：手动部署后字体仍然不可用

**原因**：Render 可能使用新的容器，Shell 中安装的字体没有持久化

**解决方案**：

#### 方案 A：修改 render.yaml（推荐）

在 Render Dashboard 中：

1. Web Service → Settings
2. 修改 Build Command 为：

```bash
apt-get update && apt-get install -y fonts-wqy-microhei fonts-wqy-zenhei && fc-cache -fv && pip install -r requirements.txt
```

3. 点击 **Save Changes**
4. 触发手动部署

#### 方案 B：使用持久化磁盘

如果你已经配置了磁盘存储（1GB），可以将字体安装到持久化目录：

```bash
# 在 Render Shell 中
mkdir -p /opt/render/project/data/fonts

# 复制字体到持久化目录
cp -r /usr/share/fonts/truetype/wqy /opt/render/project/data/fonts/

# 修改 fonts.py，从持久化目录加载字体
```

### 问题 4：找到字体但 PDF 中文仍显示为方框

**原因**：字体加载成功但 subfontIndex 不正确

**解决方案**：

测试不同的 subfontIndex：

```bash
python3 << 'EOF'
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

font_path = '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc'

# 尝试不同的 subfontIndex
for i in range(4):
    try:
        pdfmetrics.registerFont(TTFont(f'WQYMicroHei_{i}', font_path, subfontIndex=i))
        print(f"[OK] subfontIndex {i} 加载成功")
    except Exception as e:
        print(f"[FAIL] subfontIndex {i} 失败: {e}")
EOF
```

根据输出结果，修改 `utils/fonts.py` 中的 subfontIndex。

---

## 📝 验证清单

安装完成后，请验证：

- [ ] 字体文件已安装（`/usr/share/fonts/truetype/wqy/wqy-microhei.ttc`）
- [ ] 字体缓存已刷新（`fc-cache -fv`）
- [ ] Python 能成功加载字体
- [ ] Runtime Logs 显示字体加载成功
- [ ] PDF 生成功能正常
- [ ] PDF 中文正确显示（无方框、无乱码）

---

## 🎯 预期结果

完成以上步骤后，你应该能在 Runtime Logs 中看到：

```
[OK] Successfully registered system font: /usr/share/fonts/truetype/wqy/wqy-microhei.ttc
```

并且 PDF 文件中的中文能够正确显示。

---

## 📚 相关文档

- 📄 `FONT_FIX_GUIDE.md` - 字体修复指南
- 📄 `UPDATE_DEPLOYMENT_GUIDE.md` - 更新部署指南
- 📄 `install_fonts.sh` - 字体安装脚本

---

## 💡 重要提示

1. **Render Shell 是临时环境**：每次部署都会创建新的容器，Shell 中安装的字体不会持久化
2. **推荐修改 render.yaml**：在 Build Command 中添加字体安装命令
3. **使用 fc-cache -fv**：安装字体后必须刷新字体缓存
4. **测试多个 subfontIndex**：如果中文仍显示为方框，尝试不同的 subfontIndex

---

*最后更新：2026-02-14*
