from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import datetime

# 导入字体管理模块
from utils.fonts import register_chinese_font, get_chinese_font_name, get_chinese_bold_font_name

# 注册中文字体
fonts_registered = register_chinese_font()

def generate_will_pdf(will):
    """
    生成数字遗嘱PDF

    Args:
        will: DigitalWill对象

    Returns:
        PDF文件路径
    """
    # 创建输出目录
    output_dir = 'temp_pdfs'
    os.makedirs(output_dir, exist_ok=True)

    # 生成文件名
    filename = f'will_{will.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    filepath = os.path.join(output_dir, filename)

    # 创建PDF文档
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    # 创建样式
    styles = getSampleStyleSheet()

    # 使用字体管理模块获取字体名称
    normal_font = get_chinese_font_name()
    bold_font = get_chinese_bold_font_name()

    # 自定义样式
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=bold_font,
        fontSize=22,
        spaceAfter=30,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName=bold_font,
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontName=normal_font,
        fontSize=11,
        spaceAfter=12,
        alignment=TA_JUSTIFY,
        leading=16
    )

    warning_style = ParagraphStyle(
        'CustomWarning',
        parent=styles['BodyText'],
        fontName=normal_font,
        fontSize=10,
        textColor=colors.red,
        spaceAfter=20,
        alignment=TA_CENTER
    )

    # 构建内容
    story = []

    # 标题
    story.append(Paragraph("数字遗产意愿声明", title_style))
    story.append(Spacer(1, 0.3 * inch))

    # 基本信息
    story.append(Paragraph("<b>一、基本信息</b>", heading_style))
    story.append(Paragraph("<b>声明标题：</b>", body_style))
    story.append(Paragraph(will.title, body_style))
    story.append(Spacer(1, 0.1 * inch))

    story.append(Paragraph("<b>声明日期：</b>", body_style))
    story.append(Paragraph(will.created_at.strftime('%Y年%m月%d日'), body_style))
    story.append(Spacer(1, 0.2 * inch))

    # 总体意愿说明
    if will.description:
        story.append(Paragraph("<b>总体意愿说明：</b>", body_style))
        story.append(Paragraph(will.description, body_style))
        story.append(Spacer(1, 0.2 * inch))

    # 继承人信息
    if will.assets_data and will.assets_data.get('heir_info'):
        story.append(Paragraph("<b>指定继承人信息：</b>", body_style))
        story.append(Paragraph(will.assets_data['heir_info'], body_style))
        story.append(Spacer(1, 0.2 * inch))

    # 特别说明
    if will.assets_data and will.assets_data.get('special_notes'):
        story.append(Paragraph("<b>特别说明：</b>", body_style))
        story.append(Paragraph(will.assets_data['special_notes'], body_style))
        story.append(Spacer(1, 0.3 * inch))

    # 资产处理选项
    if will.assets_data:
        story.append(Paragraph("<b>二、数字资产处理意愿</b>", heading_style))

        # 创建资产表格
        asset_data = [['平台名称', '账号', '处理方式']]
        asset_count = 0
        for asset_id, asset_info in will.assets_data.items():
            if asset_id not in ['heir_info', 'special_notes']:
                platform = asset_info.get('platform_name', '未知')
                account = asset_info.get('account', '未知')
                action = asset_info.get('action', '未指定')
                asset_data.append([platform, account, action])
                asset_count += 1

        if asset_count > 0:
            table = Table(asset_data, colWidths=[2*inch, 2.5*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), bold_font),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), normal_font),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            story.append(table)
        else:
            story.append(Paragraph("未选择任何数字资产", body_style))

        story.append(Spacer(1, 0.3 * inch))

    # 处理方式说明
    story.append(Paragraph("<b>三、处理方式说明</b>", heading_style))
    story.append(Paragraph(
        "<b>1. 指定继承人：</b>将数字资产转移给指定的继承人，需要提供继承人的联系信息。",
        body_style
    ))
    story.append(Paragraph(
        "<b>2. 转为纪念模式：</b>保持账户活跃状态，保留聊天记录和分享内容，但不进行登录操作。",
        body_style
    ))
    story.append(Paragraph(
        "<b>3. 委托删除：</b>授权平台或继承人删除账户，清除所有个人数据。",
        body_style
    ))
    story.append(Paragraph(
        "<b>4. 其他处理方式：</b>根据具体情况自定义处理方式，需要详细说明处理流程。",
        body_style
    ))
    story.append(Spacer(1, 0.3 * inch))

    # 平台政策参考
    story.append(Paragraph("<b>四、平台政策参考</b>", heading_style))
    story.append(Paragraph(
        "请注意，各数字平台对账户继承有不同的政策规定。在执行本声明时，"
        "建议继承人提前了解相关平台的具体政策，并准备必要的法律文件。",
        body_style
    ))
    story.append(Spacer(1, 0.1 * inch))

    story.append(Paragraph(
        "<b>微信：</b>账户所有权归腾讯公司所有，继承需要提供相关证明材料。账户长期不使用会被冻结。",
        body_style
    ))
    story.append(Paragraph(
        "<b>QQ：</b>可以申请继承，需要提供死亡证明、亲属关系证明等材料。需要提供完整的法律文件。",
        body_style
    ))
    story.append(Paragraph(
        "<b>抖音：</b>继承政策相对严格，需要提供法律文件和身份证明。继承成功率较低，建议提前做好数据备份。",
        body_style
    ))
    story.append(Spacer(1, 0.3 * inch))

    # 法律提示
    story.append(Paragraph(
        "<b>五、重要法律提示</b>",
        heading_style
    ))
    story.append(Paragraph(
        "<b>本文件可作为您意愿的强烈表达，协助继承人沟通，但不替代正式公证遗嘱。</b>"
        "建议在制定此声明后，咨询专业律师，并考虑进行公证。",
        warning_style
    ))
    story.append(Spacer(1, 0.3 * inch))

    # 免责声明
    story.append(Paragraph(
        "<b>六、免责声明</b>",
        heading_style
    ))
    story.append(Paragraph(
        "本平台仅提供信息参考和工具服务，不构成法律建议。本声明的执行情况"
        "取决于各平台的具体政策、相关法律法规以及继承人的实际操作。"
        "因执行本声明而产生的任何法律纠纷，本平台不承担任何责任。",
        body_style
    ))
    story.append(Spacer(1, 0.5 * inch))

    # 页脚
    story.append(Paragraph(
        f"生成日期：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')} | "
        f"本文件由数字遗产继承平台生成",
        ParagraphStyle(
            'Footer',
            parent=styles['BodyText'],
            fontName=normal_font,
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
    ))

    # 生成PDF
    try:
        doc.build(story)
        # 验证文件是否生成成功
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"PDF generated successfully: {filepath} (Size: {file_size} bytes)")
            return filepath
        else:
            raise Exception("PDF file was not created")
    except Exception as e:
        print(f"PDF generation error: {e}")
        import traceback
        traceback.print_exc()
        raise
