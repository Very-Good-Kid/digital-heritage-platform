# Render 休眠和 PDF 中文显示的免费解决方案

## 问题 1：Render 休眠后实例销毁，需要重新注册账号

### 问题说明
Render 免费版有以下限制：
- 应用 15 分钟无访问后自动休眠
- 休眠后冷启动需要 30-60 秒
- **重要**：休眠不会导致数据库数据丢失
- **重要**：不需要重新注册账号

### 误解澄清
**休眠 ≠ 数据丢失**
- 休眠只是暂停应用运行
- 数据库文件持久化存储
- 用户账号信息保存在数据库中
- 重新唤醒后所有数据都在

### 为什么会出现"需要重新注册"的现象？

可能的原因：
1. **应用正在冷启动** - 访问时显示错误，等待 30-60 秒后刷新即可
2. **浏览器缓存问题** - 清除浏览器缓存或使用隐私模式
3. **URL 输入错误** - 确认访问的是正确的网址
4. **临时服务器错误** - 稍后重试

### ✅ 免费解决方案

#### 方案 1：使用 Keep-Alive 服务（推荐）

使用第三方 Keep-Alive 服务定期访问您的应用，防止休眠：

**免费 Keep-Alive 服务**：
1. **UptimeRobot** (https://uptimerobot.com)
   - 完全免费
   - 每 5 分钟访问一次
   - 支持通知功能
   - 设置步骤：
     1. 注册账号
     2. 添加新监控
     3. 选择 Monitor Type: HTTPS
     4. 输入您的网址：https://digital-heritage-platform.onrender.com
     5. 设置 Interval: 5 minutes
     6. 保存

2. **Pingdom** (https://pingdom.com)
   - 免费版支持 1 个监控
   - 每 1 分钟访问一次
   - 提供性能报告

3. **StatusCake** (https://statuscake.com)
   - 免费版支持 10 个监控
   - 每 1 分钟访问一次
   - 支持多种监控类型

#### 方案 2：使用浏览器扩展

安装 Keep-Alive 浏览器扩展：
- **Keep Alive for Render** - Chrome 扩展
- **Render Keep-Alive** - Firefox 扩展
- 自动在后台定期访问应用

#### 方案 3：使用 Cron Job（如果有服务器）

如果有其他服务器，可以设置 Cron Job：
```bash
# 每 5 分钟访问一次
*/5 * * * * curl https://digital-heritage-platform.onrender.com
```

#### 方案 4：接受休眠（最简单）

如果应用使用频率不高，可以接受休眠：
- 用户首次访问需要等待 30-60 秒
- 之后 15 分钟内访问都是秒开
- 完全免费，无需额外配置

### 数据持久化保证

**Render 免费版数据持久化**：
- ✅ 数据库文件持久化存储
- ✅ 用户账号信息不会丢失
- ✅ 数字资产数据不会丢失
- ✅ 数字遗嘱数据不会丢失
- ✅ 所有用户数据都会保留

**配置持久化**：
```yaml
# render.yaml
disk:
  name: data
  mountPath: /opt/render/project/data
  sizeGB: 1
```

### 验证数据是否丢失

在 Render Shell（如果可用）中检查：
```bash
# 查看数据库文件
ls -lh /opt/render/project/data/

# 查看数据库内容
sqlite3 /opt/render/project/data/digital_heritage.db
SELECT * FROM users;
SELECT * FROM digital_assets;
SELECT * FROM digital_wills;
```

或者在应用中：
1. 访问 https://digital-heritage-platform.onrender.com
2. 尝试登录之前的账号
3. 检查数字资产和遗嘱是否还在

---

## 问题 2：PDF 中文显示为方框

### 问题说明
Render 免费环境没有中文字体，导致生成的 PDF 中中文字符显示为方框。

### ✅ 免费解决方案

#### 方案 1：优先使用 Excel 模板（推荐）

**优势**：
- ✅ 完全支持中文
- ✅ 格式规范美观
- ✅ 用户可以编辑
- ✅ 兼容性好
- ✅ 无需额外配置

**实现方式**：
1. 在 PDF 下载按钮旁边添加提示：
```html
<div class="alert alert-warning">
  <i class="bi bi-exclamation-triangle"></i>
  注意：由于部署环境限制，PDF 中的中文可能无法正确显示。
  建议使用 Excel 模板（完全支持中文）。
</div>
```

2. 优先推荐 Excel 模板：
```html
<div class="d-flex gap-2">
  <a href="{{ url_for('download_template', format='excel') }}" class="btn btn-success">
    <i class="bi bi-file-earmark-excel"></i> Excel模板（推荐）
  </a>
  <a href="{{ url_for('static', filename='templates/数字资产清单模板.pdf') }}" class="btn btn-outline-danger">
    <i class="bi bi-file-earmark-pdf"></i> PDF模板
  </a>
</div>
```

#### 方案 2：使用客户端生成 PDF

使用浏览器打印功能生成 PDF：

**实现方式**：
```html
<button onclick="window.print()" class="btn btn-primary">
  <i class="bi bi-printer"></i> 打印/保存为 PDF
</button>
```

**优势**：
- ✅ 完全支持中文
- ✅ 使用系统字体
- ✅ 用户可控
- ✅ 无需服务器字体

#### 方案 3：使用在线 PDF 生成服务

使用第三方 API 生成 PDF：

**免费服务**：
1. **HTML to PDF API** - 每月免费额度
2. **PDFMonkey** - 免费计划
3. **APITemplate.io** - 免费额度

**缺点**：
- 有使用限制
- 需要网络请求
- 可能有延迟

#### 方案 4：使用图片代替文字（部分场景）

对于标题和重要文字，使用图片：

**实现方式**：
```python
from PIL import Image, ImageDraw, ImageFont
import io

def create_text_image(text):
    # 创建图片
    img = Image.new('RGB', (400, 50), color='white')
    draw = ImageDraw.Draw(img)
    
    # 使用系统字体
    try:
        font = ImageFont.truetype('arial.ttf', 30)
    except:
        font = ImageFont.load_default()
    
    # 绘制文字
    draw.text((10, 10), text, fill='black', font=font)
    
    # 保存为图片
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io
```

**缺点**：
- 不适合长文本
- 图片文件较大
- 不能选择和复制

#### 方案 5：使用纯英文 PDF（临时方案）

生成英文版 PDF，提供中文说明：

**实现方式**：
```html
<div class="alert alert-info">
  <h6><i class="bi bi-info-circle"></i> PDF 说明</h6>
  <p>当前 PDF 为英文版本，中文内容请参考以下说明：</p>
  <ul>
    <li>Platform Name = 平台名称</li>
    <li>Account = 账号</li>
    <li>Password = 密码</li>
    <li>Category = 分类</li>
  </ul>
</div>
```

#### 方案 6：使用 HTML 预览代替 PDF

生成 HTML 页面供用户查看和打印：

**实现方式**：
```python
@app.route('/wills/<int:will_id>/preview')
@login_required
def preview_will(will_id):
    will = DigitalWill.query.get_or_404(will_id)
    return render_template('wills/preview.html', will=will)
```

**模板**：
```html
<div class="container" style="max-width: 800px; padding: 40px;">
  <h1 style="text-align: center;">数字遗产意愿声明</h1>
  <hr>
  <h2>基本信息</h2>
  <p><strong>标题：</strong>{{ will.title }}</p>
  <p><strong>创建时间：</strong>{{ will.created_at.strftime('%Y年%m月%d日') }}</p>
  <hr>
  <h2>总体意愿说明</h2>
  <p>{{ will.description }}</p>
  <hr>
  <div class="text-center mt-4">
    <button onclick="window.print()" class="btn btn-primary btn-lg">
      <i class="bi bi-printer"></i> 打印 / 保存为 PDF
    </button>
  </div>
</div>
```

**优势**：
- ✅ 完全支持中文
- ✅ 格式灵活
- ✅ 用户可控
- ✅ 可以打印

---

## 推荐组合方案

### 方案 A：Excel + HTML 预览（最推荐）

**配置**：
1. 默认提供 Excel 模板下载
2. 提供 HTML 预览页面
3. HTML 页面提供打印功能
4. PDF 模钮保留，但添加警告提示

**实现**：
```html
<div class="d-flex gap-2 mb-3">
  <a href="{{ url_for('download_template', format='excel') }}" class="btn btn-success">
    <i class="bi bi-file-earmark-excel"></i> Excel 模板（推荐）
  </a>
  <a href="{{ url_for('preview_will', will_id=will.id) }}" class="btn btn-primary">
    <i class="bi bi-eye"></i> 预览并打印
  </a>
</div>

<div class="alert alert-warning">
  <i class="bi bi-exclamation-triangle"></i>
  PDF 功能因部署环境限制，中文可能显示不正确。
  建议使用 Excel 模板或打印功能。
</div>
```

### 方案 B：Keep-Alive + Excel（简单有效）

**配置**：
1. 使用 UptimeRobot 保持应用活跃
2. 优先推荐 Excel 模板
3. 添加清晰的说明文档

---

## 总结

### Render 休眠问题
- ✅ 使用 UptimeRobot 免费 Keep-Alive 服务
- ✅ 或接受休眠，用户首次访问等待 30-60 秒
- ✅ 数据不会丢失，无需重新注册

### PDF 中文显示问题
- ✅ 优先使用 Excel 模板（完全支持中文）
- ✅ 提供打印功能（使用系统字体）
- ✅ 添加清晰的提示说明
- ✅ 接受免费部署的限制

### 免费方案对比

| 方案 | Render 休眠 | PDF 中文 | 复杂度 | 推荐度 |
|------|------------|---------|--------|--------|
| UptimeRobot | ✅ 解决 | - | 低 | ⭐⭐⭐⭐⭐ |
| Excel 模板 | - | ✅ 解决 | 低 | ⭐⭐⭐⭐⭐ |
| 打印功能 | - | ✅ 解决 | 低 | ⭐⭐⭐⭐⭐ |
| Keep-Alive 扩展 | ✅ 解决 | - | 低 | ⭐⭐⭐⭐ |
| 接受限制 | - | - | 最低 | ⭐⭐⭐ |

---

## 快速实施步骤

### 1. 设置 UptimeRobot（5 分钟）

1. 访问 https://uptimerobot.com
2. 注册账号
3. 添加新监控
4. 输入：https://digital-heritage-platform.onrender.com
5. 设置间隔：5 分钟
6. 保存

### 2. 更新提示信息（10 分钟）

在模板中添加提示：
```html
<div class="alert alert-info">
  <h6><i class="bi bi-info-circle"></i> 功能说明</h6>
  <ul>
    <li><strong>Excel 模板</strong>：完全支持中文，推荐使用</li>
    <li><strong>PDF 模板</strong>：中文可能显示不正确</li>
    <li><strong>打印功能</strong>：使用系统字体，完全支持中文</li>
  </ul>
</div>
```

### 3. 测试验证（5 分钟）

1. 测试 Excel 下载
2. 测试打印功能
3. 检查 UptimeRobot 状态
4. 等待 15 分钟后测试是否休眠

---

**文档日期**：2026-02-10
**版本**：V1.0
**状态**：✅ 完整方案
