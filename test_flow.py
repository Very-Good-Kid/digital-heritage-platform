"""完整测试登录和API流程"""
from app import app
import json
import re

# 模拟完整的登录和API调用流程
with app.test_client() as client:
    # 1. 获取登录页面
    login_page = client.get('/login')
    
    # 2. 提取CSRF token
    match = re.search(b'name="csrf_token" value="([^"]+)"', login_page.data)
    csrf_token = match.group(1).decode('utf-8') if match else ''
    
    # 3. 登录
    login_resp = client.post('/login', data={
        'username': 'admin',
        'password': 'admin123',
        'csrf_token': csrf_token
    }, follow_redirects=False)
    
    print('=== 登录结果 ===')
    print(f'状态码: {login_resp.status_code}')
    location = login_resp.headers.get('Location', '无')
    print(f'重定向到: {location}')
    
    # 4. 访问后台仪表盘页面
    dashboard_resp = client.get('/admin/', follow_redirects=False)
    print(f'\n=== 后台仪表盘页面 ===')
    print(f'状态码: {dashboard_resp.status_code}')
    
    # 5. 调用API
    api_resp = client.get('/admin/api/stats')
    print(f'\n=== API调用 ===')
    print(f'状态码: {api_resp.status_code}')
    print(f'Content-Type: {api_resp.content_type}')
    
    if api_resp.status_code == 200:
        data = json.loads(api_resp.data)
        users = data.get('users', {})
        total = users.get('total', 'N/A')
        print(f'成功! 用户数: {total}')
    else:
        print(f'响应: {api_resp.data[:200]}')
