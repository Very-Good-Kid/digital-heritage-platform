
import pymupdf

doc = pymupdf.open('c:/Users/admin/Desktop/demo - codebuddy/static/templates/数字遗产意愿声明模板.pdf')
for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text()
    # 写入文件
    with open(f'pdf_page_{page_num + 1}.txt', 'w', encoding='utf-8') as f:
        f.write(text)
    print(f'Page {page_num + 1} saved to pdf_page_{page_num + 1}.txt')
