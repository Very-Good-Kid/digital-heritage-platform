# CSRF错误修复补丁

## 问题描述
Render生产环境登录失败,错误信息:
```
AttributeError: 'CustomCSRFProtect' object has no attribute 'app'
```

## 修复方法

### 方法1: 在Render Shell中修改(最快)

1. 登录Render控制台
2. 进入您的服务 `digital-heritage-platform`
3. 点击"Shell"按钮
4. 执行以下命令:

```bash
cd /opt/render/project/src
sed -i 's/if endpoint:/if endpoint and hasattr(self, '"'"'app'"'"') and self.app:/g' app.py
```

5. 重启服务:
```bash
exit
```

然后点击"Manual Deploy" → "Restart"

### 方法2: 推送代码到GitHub(推荐)

在本地执行:
```bash
git push
```

Render会自动检测到更新并重新部署。

### 方法3: 手动编辑文件

1. 在Render Shell中:
```bash
cd /opt/render/project/src
nano app.py
```

2. 找到第23行,将:
```python
if endpoint:
```

改为:
```python
if endpoint and hasattr(self, 'app') and self.app:
```

3. 按 `Ctrl+X`, `Y`, `Enter` 保存

4. 重启服务

## 验证修复

修复后,访问 https://digital-heritage-platform.onrender.com/login
尝试登录,应该可以正常登录。

## 修复说明

这个修复添加了安全检查,确保 `self.app` 属性存在后再访问它,避免AttributeError。

修改位置: `app.py` 第23行
