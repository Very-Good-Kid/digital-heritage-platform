# 删除前3个重复的update_will_status函数定义
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到4个函数定义的位置
def find_function_starts():
    starts = []
    for i, line in enumerate(lines):
        if '@app.route(\'/wills/<int:will_id>/status\', methods=[\'POST\'])' in line:
            starts.append(i)
    return starts

starts = find_function_starts()
print(f'找到 {len(starts)} 个函数定义，位置: {starts}')

# 如果有4个函数，删除前3个
if len(starts) >= 4:
    # 找到第4个函数之前的所有内容
    end_of_third_function = starts[3]  # 第4个函数的开始位置
    # 保留第4个函数之后的所有内容
    new_content = ''.join(lines[:starts[0]]) + '\n' + ''.join(lines[starts[3]:])

    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(new_content)

    print('删除前3个重复函数完成')
else:
    print(f'只找到 {len(starts)} 个函数，删除操作取消')
