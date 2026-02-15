with open(r'c:\Users\admin\Desktop\demo - codebuddy\templates\assets\index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到JavaScript代码的位置
# 第548-607行是需要替换的JavaScript代码
new_js = '''  <script>
  // 密码显示/隐藏切换（添加资产表单）
  document.getElementById('togglePassword').addEventListener('click', function() {
      const passwordInput = document.getElementById('password');
      const icon = this.querySelector('i');
  
      if (passwordInput.type === 'password') {
          passwordInput.type = 'text';
          icon.classList.remove('bi-eye');
          icon.classList.add('bi-eye-slash');
      } else {
          passwordInput.type = 'password';
          icon.classList.remove('bi-eye-slash');
          icon.classList.add('bi-eye');
      }
  });
  
  // 模态框密码显示/隐藏切换
  document.getElementById('toggleModalPassword').addEventListener('click', function() {
      const passwordInput = document.getElementById('decryptedPassword');
      const icon = this.querySelector('i');
  
      if (passwordInput.type === 'password') {
          passwordInput.type = 'text';
          icon.classList.remove('bi-eye');
          icon.classList.add('bi-eye-slash');
      } else {
          passwordInput.type = 'password';
          icon.classList.remove('bi-eye-slash');
          icon.classList.add('bi-eye');
      }
  });
  
  // 模态框实例
  let passwordModalInstance = null;
  
  // 解密密码按钮
  document.querySelectorAll('.decrypt-btn').forEach(function(button) {
      button.addEventListener('click', function() {
          const assetId = this.getAttribute('data-asset-id');
          const csrfToken = document.querySelector('input[name="csrf_token"]').value;
  
          fetch(`/assets/${assetId}/decrypt`, {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
                  'X-CSRFToken': csrfToken
              }
          })
          .then(response => response.json())
          .then(data => {
              if (data.success) {
                  const passwordInput = document.getElementById('decryptedPassword');
                  passwordInput.value = data.password;
                  passwordInput.type = 'password';  // 默认隐藏密码
                  
                  // 重置切换按钮图标
                  const toggleBtn = document.getElementById('toggleModalPassword');
                  const icon = toggleBtn.querySelector('i');
                  icon.classList.remove('bi-eye-slash');
                  icon.classList.add('bi-eye');
                  
                  // 显示模态框
                  const modalEl = document.getElementById('passwordModal');
                  if (passwordModalInstance) {
                      passwordModalInstance.dispose();
                  }
                  passwordModalInstance = new bootstrap.Modal(modalEl);
                  passwordModalInstance.show();
              } else {
                  alert('解密失败：' + data.message);
              }
          })
          .catch(error => {
              console.error('解密错误:', error);
              alert('解密失败，请重试');
          });
      });
  });
  
  // 模态框关闭后清理
  document.getElementById('passwordModal').addEventListener('hidden.bs.modal', function() {
      document.getElementById('decryptedPassword').value = '';
      document.getElementById('decryptedPassword').type = 'password';
      const toggleBtn = document.getElementById('toggleModalPassword');
      const icon = toggleBtn.querySelector('i');
      icon.classList.remove('bi-eye-slash');
      icon.classList.add('bi-eye');
  });
  
  // 复制密码
  document.getElementById('copyPassword').addEventListener('click', function() {
      const passwordInput = document.getElementById('decryptedPassword');
      navigator.clipboard.writeText(passwordInput.value).then(function() {
          const originalText = document.getElementById('copyPassword').innerHTML;
          document.getElementById('copyPassword').innerHTML = '<i class="bi bi-check"></i> 已复制';
          setTimeout(() => {
              document.getElementById('copyPassword').innerHTML = originalText;
          }, 2000);
      }).catch(function(err) {
          // 降级方案
          passwordInput.select();
          document.execCommand('copy');
          const originalText = document.getElementById('copyPassword').innerHTML;
          document.getElementById('copyPassword').innerHTML = '<i class="bi bi-check"></i> 已复制';
          setTimeout(() => {
              document.getElementById('copyPassword').innerHTML = originalText;
          }, 2000);
      });
  });
  
'''

# 找到<script>标签的位置
start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if '{% block extra_js %}' in line:
        start_idx = i + 1  # <script>在下一行
    if start_idx and '// 遗嘱表单相关' in line:
        end_idx = i - 1  // 复制密码代码结束
        break

if start_idx and end_idx:
    # 替换JavaScript代码
    lines = lines[:start_idx] + [new_js] + lines[end_idx + 1:]
    print(f'JavaScript已替换 (行 {start_idx+1} 到 {end_idx+1})')
else:
    print(f'未找到JavaScript位置: start={start_idx}, end={end_idx}')

with open(r'c:\Users\admin\Desktop\demo - codebuddy\templates\assets\index.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)
