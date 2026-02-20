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
    生成数字资产继承意愿声明书PDF

    Args:
        will: DigitalWill对象

    Returns:
        PDF文件路径
    """
    # 使用配置中的持久化目录
    from flask import current_app
    output_dir = os.path.join(current_app.config.get('DATA_DIR', 'temp_pdfs'), 'temp_pdfs')
    os.makedirs(output_dir, exist_ok=True)

    # 生成文件名
    filename = f'will_{will.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    filepath = os.path.join(output_dir, filename)

    # 创建PDF文档
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=60,
        leftMargin=60,
        topMargin=60,
        bottomMargin=60
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
        fontSize=20,
        spaceAfter=20,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName=bold_font,
        fontSize=13,
        spaceAfter=10,
        spaceBefore=15,
        textColor=colors.HexColor('#2c3e50')
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontName=normal_font,
        fontSize=11,
        spaceAfter=10,
        alignment=TA_JUSTIFY,
        leading=18
    )

    small_style = ParagraphStyle(
        'SmallBody',
        parent=styles['BodyText'],
        fontName=normal_font,
        fontSize=9,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        leading=14
    )

    warning_style = ParagraphStyle(
        'CustomWarning',
        parent=styles['BodyText'],
        fontName=normal_font,
        fontSize=10,
        textColor=colors.red,
        spaceAfter=15,
        alignment=TA_CENTER
    )

    # 构建内容
    story = []

    # 标题
    story.append(Paragraph("数字资产继承意愿声明书", title_style))
    story.append(Spacer(1, 0.15 * inch))

    # 声明人信息
    if will.assets_data:
        declarant_name = will.assets_data.get('declarant_name', '_____________')
        declarant_id = will.assets_data.get('declarant_id', '_____________')
        declarant_nation = will.assets_data.get('declarant_nation', '_____________')
    else:
        declarant_name = '_____________'
        declarant_id = '_____________'
        declarant_nation = '_____________'

    declarant_data = [
        ['声明人：' + declarant_name, '身份证号：' + declarant_id, '民族：' + declarant_nation]
    ]
    declarant_table = Table(declarant_data, colWidths=[2.2*inch, 2.5*inch, 1.8*inch])
    declarant_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), normal_font),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(declarant_table)
    story.append(Spacer(1, 0.2 * inch))

    # 授权声明
    story.append(Paragraph(
        "本人明确授权，在身故或丧失自主行为能力后，本人指定的联系人（继承人）可依据本声明书所载意愿，对以下各类数字资产进行处置：",
        body_style
    ))
    story.append(Spacer(1, 0.1 * inch))

    # 构建资产表格数据
    asset_table_data = [
        ['资产类别', '处置意愿']
    ]

    # 社交媒体
    social_actions = ''
    if will.assets_data and will.assets_data.get('social'):
        social_data = will.assets_data['social']
        actions = social_data.get('actions', [])
        if actions:
            social_actions = '\n'.join([a for a in actions])
            social_category = '社交媒体\n（微信、QQ等）'
            asset_table_data.append([social_category, social_actions])

    # 电子邮箱与云存储
    cloud_actions = ''
    if will.assets_data and will.assets_data.get('cloud'):
        cloud_data = will.assets_data['cloud']
        actions = cloud_data.get('actions', [])
        if actions:
            cloud_actions = '\n'.join([a for a in actions])
            cloud_category = '电子邮箱与云存储\n（iCloud、网盘等）'
            asset_table_data.append([cloud_category, cloud_actions])

    # 数字货币与金融App
    finance_actions = ''
    if will.assets_data and will.assets_data.get('finance'):
        finance_data = will.assets_data['finance']
        actions = finance_data.get('actions', [])
        if actions:
            finance_actions = '\n'.join([a for a in actions])
            finance_category = '数字货币与金融App\n（比特币、游戏账号等）'
            asset_table_data.append([finance_category, finance_actions])

    if len(asset_table_data) > 1:
        asset_table = Table(asset_table_data, colWidths=[2.2*inch, 3.2*inch], repeatRows=1)
    asset_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), bold_font),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffffff')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), normal_font),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('WORDWRAP', (0, 0), (-1, -1), True),
    ]))
    story.append(asset_table)
    story.append(Spacer(1, 0.25 * inch))

    # 执行人指定
    story.append(Paragraph("<b>执行人指定</b>", heading_style))

    # 主要联系人
    if will.assets_data:
        primary_name = will.assets_data.get('primary_name', '___________')
        primary_relation = will.assets_data.get('primary_relation', '___________')
        primary_phone = will.assets_data.get('primary_phone', '___________')
        backup_name = will.assets_data.get('backup_name', '___________')
        backup_relation = will.assets_data.get('backup_relation', '___________')
        backup_phone = will.assets_data.get('backup_phone', '___________')
    else:
        primary_name = primary_relation = primary_phone = '___________'
        backup_name = backup_relation = backup_phone = '___________'

    # 执行人表格
    executor_table_data = [
        ['联系人类型', '姓名', '关系', '电话'],
        ['主要联系人', primary_name, primary_relation, primary_phone],
        ['备用联系人', backup_name, backup_relation, backup_phone]
    ]
    executor_table = Table(executor_table_data, colWidths=[1.5*inch, 1.5*inch, 1.2*inch, 1.8*inch])
    executor_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), bold_font),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffffff')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), normal_font),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(executor_table)
    story.append(Spacer(1, 0.15 * inch))

    # 执行人说明文字
    executor_description = "本人特此指定以上人员为本声明之执行人。主要联系人将全权负责启动并主导本声明所涉的资产处置流程。仅当主要联系人无法履行职责时，备用联系人方可接替其职责。此指定仅为操作授权，并不涉及或改变任何法定继承人之实质财产继承权。"
    story.append(Paragraph(executor_description, body_style))
    story.append(Spacer(1, 0.2 * inch))

    # 固定法律效力声明
    story.append(Paragraph("<b>法律效力声明</b>", body_style))
    story.append(Paragraph(
        "本人确认，本声明书旨在清晰表达本人关于数字资产处置的最终意愿，并为继承人提供明确指引。本人理解，本声明书本身并非具有直接强制执行力的法律文件，数字资产的最终归属与处理须遵守《中华人民共和国民法典》等法律规定及各平台合约。本人建议，可将本声明书进行公证，或作为本人正式遗嘱之附件，以增强其法律参考效力。",
        body_style
    ))
    story.append(Spacer(1, 0.3 * inch))

    # 签署栏
    story.append(Paragraph("<b>签署栏</b>", heading_style))
    
    sign_data = [
        ['声明人（签名/指印）：________________________', ''],
        ['', '年      月      日']
    ]
    sign_table = Table(sign_data, colWidths=[4*inch, 2.5*inch])
    sign_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), normal_font),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 1), (1, 1), 'RIGHT'),
    ]))
    story.append(sign_table)
    story.append(Spacer(1, 0.2 * inch))

    # 法律提示
    story.append(Paragraph(
        "<b>重要法律提示</b>",
        heading_style
    ))
    story.append(Paragraph(
        "本文件可作为您意愿的强烈表达，协助继承人沟通，但不替代正式公证遗嘱。建议在制定此声明后，咨询专业律师，并考虑进行公证。",
        body_style
    ))
    story.append(Spacer(1, 0.2 * inch))



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
