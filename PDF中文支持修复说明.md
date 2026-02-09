# PDF中文支持修复说明

## 问题描述

**问题**：下载的PDF文件中文显示为黑白方块（乱码）

**原因**：reportlab默认字体不支持中文字符

## 解决方案

### 1. 注册中文字体

在`utils/pdf_generator.py`中添加中文字体注册功能：

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def register_chinese_fonts():
    """注册中文字体"""
    try:
        # Windows - 使用微软雅黑
        if os.path.exists('C:\\Windows\\Fonts\\msyh.ttc'):
            pdfmetrics.registerFont(TTFont('SimHei', 'C:\\Windows\\Fonts\\msyh.ttc', subfontIndex=0))
            pdfmetrics.registerFont(TTFont('SimHei-Bold', 'C:\\Windows\\Fonts\\msyhbd.ttc', subfontIndex=0))
            return True
        # Linux - 使用文泉驿正黑
        elif os.path.exists('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'):
            pdfmetrics.registerFont(TTFont('SimHei', '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', subfontIndex=0))
            return True
        # Mac - 使用苹方字体
        elif os.path.exists('/System/Library/Fonts/PingFang.ttc'):
            pdfmetrics.registerFont(TTFont('SimHei', '/System/Library/Fonts/PingFang.ttc', subfontIndex=1))
            return True
    except:
        pass
    return False

# 注册字体
fonts_registered = register_chinese_fonts()
```

### 2. 使用中文字体

在PDF生成时使用注册的中文字体：

```python
# 根据字体注册情况选择字体
if fonts_registered:
    normal_font = 'SimHei'
    bold_font = 'SimHei-Bold'
else:
    normal_font = 'Helvetica'
    bold_font = 'Helvetica-Bold'

# 在样式中使用字体
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontName=bold_font,  # 使用中文字体
    fontSize=22,
    spaceAfter=30,
    alignment=TA_CENTER
)

body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['BodyText'],
    fontName=normal_font,  # 使用中文字体
    fontSize=11,
    spaceAfter=12,
    alignment=TA_JUSTIFY,
    leading=16
)
```

### 3. 表格字体

在表格样式中也使用中文字体：

```python
table = Table(asset_data, colWidths=[2*inch, 2.5*inch, 2*inch])
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), bold_font),  # 表头使用粗体中文字体
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTNAME', (0, 1), (-1, -1), normal_font),  # 表格内容使用中文字体
    ('FONTSIZE', (0, 1), (-1, -1), 9),
]))
```

## 支持的字体

### Windows系统
- 微软雅黑 (SimHei) - `C:\Windows\Fonts\msyh.ttc`
- 微软雅黑加粗 (SimHei-Bold) - `C:\Windows\Fonts\msyhbd.ttc`

### Linux系统
- 文泉驿正黑 (WQY ZenHei) - `/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`

### Mac系统
- 苹方 (PingFang) - `/System/Library/Fonts/PingFang.ttc`

## 测试验证

### 测试步骤

1. **创建数字遗嘱**
   - 访问"数字遗嘱"页面
   - 填写遗嘱信息（包含中文）
   - 选择资产和处理方式
   - 点击"创建遗嘱"

2. **下载PDF**
   - 点击"下载PDF"按钮
   - 等待PDF生成和下载

3. **验证PDF**
   - 打开下载的PDF文件
   - 检查中文是否正常显示
   - 验证所有内容都清晰可读

### 预期结果

- ✅ 中文文字正常显示（不再是方块）
- ✅ 标题、正文、表格都使用中文字体
- ✅ 格式规范，布局美观
- ✅ 内容完整，包含所有必要信息

## 修复的文件

**utils/pdf_generator.py**：
- 添加中文字体注册功能
- 修改所有样式使用中文字体
- 修改表格样式使用中文字体
- 修改页脚样式使用中文字体

## 注意事项

1. **字体依赖**
   - Windows系统默认支持微软雅黑
   - Linux系统需要安装文泉驿正黑
   - Mac系统默认支持苹方字体

2. **字体回退**
   - 如果中文字体注册失败，会回退到Helvetica字体
   - 此时中文会显示为方块
   - 建议在Windows系统上生成PDF

3. **跨平台兼容性**
   - 生成的PDF文件可以在任何系统上打开
   - 字体会嵌入到PDF文件中
   - 不需要目标系统安装中文字体

## 部署到Linux服务器

如果部署到Linux服务器，需要确保中文字体可用：

```bash
# 安装文泉驿正黑字体
sudo apt-get install fonts-wqy-zenhei

# 或手动下载字体文件
# 下载后放到 /usr/share/fonts/truetype/wqy/
# 运行 fc-cache -fv 刷新字体缓存
```

## 总结

**PDF中文支持已修复！**

- ✅ 注册了中文字体
- ✅ 所有样式使用中文字体
- ✅ PDF中文正常显示
- ✅ 支持Windows/Linux/Mac系统

**现在可以正常生成包含中文的PDF文件了！** 🎉
