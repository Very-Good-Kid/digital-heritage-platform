"""
测试遗嘱状态修改API
"""
import requests
import json

# 测试URL
base_url = 'http://localhost:5000'
test_url = f'{base_url}/wills/1/status'

# 测试数据
test_data = {
    'status': 'confirmed'
}

print(f"测试URL: {test_url}")
print(f"测试数据: {test_data}")
print()

try:
    response = requests.post(test_url, json=test_data)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    print()
    
    if response.status_code == 200:
        result = response.json()
        print(f"解析结果: {result}")
    else:
        print(f"请求失败")
        
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
