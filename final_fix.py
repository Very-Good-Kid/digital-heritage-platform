# -*- coding: utf-8 -*-
"""最终修复所有缩进问题"""

# 读取文件
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 查找assets函数的结束行(return render_template)
assets_end_line = None
for i, line in enumerate(lines):
    if "return render_template('assets/index.html', assets=assets, categories=categories, wills=wills)" in line:
        assets_end_line = i
        break

if assets_end_line is not None:
    # 在assets函数结束后添加空行
    lines.insert(assets_end_line + 1, '\n')
    print(f'在第{assets_end_line + 2}行添加空行')

    # 修复download_template路由的缩进(现在应该在assets函数外部)
    for i in range(assets_end_line + 3, len(lines)):
        if '@app.route' in lines[i] or 'def download_template' in lines[i]:
            # 这些行应该有2个空格缩进
            lines[i] = '  ' + lines[i].lstrip()
            print(f'修复第{i+1}行缩进为2个空格')
        elif i > assets_end_line + 3 and lines[i].strip() and not lines[i].strip().startswith('@') and not lines[i].strip().startswith('def '):
            # 函数内部应该有4个空格缩进
            lines[i] = '    ' + lines[i].lstrip()
            print(f'修复第{i+1}行缩进为4个空格')

# 写入文件
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('修复完成')
