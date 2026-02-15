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
        spaceBefore=20,
        textColor=colors.HexColor('#2c3e50')
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

    small_style = ParagraphStyle(
        'SmallBody',
        parent=styles['BodyText'],
        fontName=normal_font,
        fontSize=9,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        leading=14
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
    story.append(Spacer(1, 0.2 * inch))

    # 副标题
    story.append(Paragraph(f"<b>{will.title}</b>", ParagraphStyle(
        'SubTitle',
        parent=styles['Heading2'],
        fontName=bold_font,
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=20
    )))

    story.append(Paragraph(f"创建日期：{will.created_at.strftime('%Y年%m月%d日')}", ParagraphStyle(
        'Date',
        parent=styles['BodyText'],
        fontName=normal_font,
        fontSize=10,
        alignment=TA_CENTER,
        spaceAfter=30
    )))

    # 第一部分：数字资产类型与处理意愿
    story.append(Paragraph("一、数字资产类型与处理意愿", heading_style))

    if will.assets_data:
        # 创建资产表格
        asset_data = [['平台名称', '资产类别', '账号', '指定联系人/继承人', '处理方式']]
        asset_count = 0
        for asset_id, asset_info in will.assets_data.items():
            if asset_id not in ['heir_info', 'special_notes', 'heir_name', 'heir_relation', 'heir_phone', 'heir_email', 'heir_notes', 'backup_name', 'backup_relation', 'backup_phone', 'backup_email', 'backup_notes']:
                platform = asset_info.get('platform_name', '未知')
                category = asset_info.get('category', '其他')
                account = asset_info.get('account', '未知')
                heir = asset_info.get('heir', '-')
                action = asset_info.get('action', '未指定')
                asset_data.append([platform, category, account, heir, action])
                asset_count += 1

        if asset_count > 0:
            table = Table(asset_data, colWidths=[1.3*inch, 0.9*inch, 1.5*inch, 1.3*inch, 1.2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), bold_font),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTNAME', (0, 1), (-1, -1), normal_font),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(table)
        else:
            story.append(Paragraph("未选择任何数字资产", body_style))
    else:
        story.append(Paragraph("未选择任何数字资产", body_style))

    story.append(Spacer(1, 0.3 * inch))

    # 第二部分：指定联系人/继承人详细信息
    story.append(Paragraph("二、指定联系人/继承人详细信息", heading_style))

    if will.assets_data:
        heir_name = will.assets_data.get('heir_name', '-')
        heir_relation = will.assets_data.get('heir_relation', '-')
        heir_phone = will.assets_data.get('heir_phone', '-')
        heir_email = will.assets_data.get('heir_email', '-')
        heir_notes = will.assets_data.get('heir_notes', '')

        heir_data = [
            ['姓名', heir_name, '与声明人关系', heir_relation],
            ['联系电话', heir_phone, '电子邮箱', heir_email]
        ]

        heir_table = Table(heir_data, colWidths=[1*inch, 2*inch, 1.2*inch, 2*inch])
        heir_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e9ecef')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#e9ecef')),
            ('FONTNAME', (0, 0), (0, -1), bold_font),
            ('FONTNAME', (2, 0), (2, -1), bold_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (1, 0), (1, -1), normal_font),
            ('FONTNAME', (3, 0), (3, -1), normal_font),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(heir_table)

        if heir_notes:
            story.append(Spacer(1, 0.1 * inch))
            story.append(Paragraph("<b>特别说明：</b>", body_style))
            story.append(Paragraph(heir_notes, body_style))
    else:
        story.append(Paragraph("未填写继承人信息", body_style))

    story.append(Spacer(1, 0.3 * inch))

    # 第三部分：附加声明
    story.append(Paragraph("三、附加声明", heading_style))

    if will.description:
        story.append(Paragraph("<b>总体意愿说明：</b>", body_style))
        story.append(Paragraph(will.description, body_style))
        story.append(Spacer(1, 0.1 * inch))

    if will.assets_data and will.assets_data.get('special_notes'):
        story.append(Paragraph("<b>其他特别说明：</b>", body_style))
        story.append(Paragraph(will.assets_data['special_notes'], body_style))
        story.append(Spacer(1, 0.2 * inch))

    # 风险评估提示
    story.append(Paragraph("<b>【风险评估提示】</b>", body_style))
    story.append(Paragraph(
        "社交媒体平台：部分平台支持「纪念账户」设置，但不支持账户密码移交；微信通常不支持账号过户，直系亲属可凭相关证明申请账号内财产处理或注销。",
        small_style
    ))
    story.append(Paragraph(
        "电子邮件与云存储：多数平台不允许继承，但可凭法律文件（如遗嘱、公证）注销账户，且可能永久删除长期未活跃账户。",
        small_style
    ))
    story.append(Paragraph(
        "数字货币与虚拟资产：私钥/助记词遗失将导致资产永久丢失；部分交易平台可能冻结未经验证的继承人申请。",
        small_style
    ))
    story.append(Spacer(1, 0.1 * inch))

    story.append(Paragraph("<b>【重要建议】</b>", body_style))
    story.append(Paragraph(
        "• 将账户信息、密码及私钥等托管于可信第三方或物理备份",
        small_style
    ))
    story.append(Paragraph(
        "• 本声明将定期变更，以反映资产变化及平台政策变动",
        small_style
    ))
    story.append(Paragraph(
        "• 如需法律效力，请咨询专业律师订立遗嘱或公证文件",
        small_style
    ))
    story.append(Spacer(1, 0.3 * inch))

    # 确认声明
    story.append(Paragraph("<b>本人确认，此文件仅为表达本人关于数字资产处置的个人意愿，并非一份具有法律强制效力的遗嘱或文件。本人知悉，数字资产的最终处置将受到各互联网平台政策、服务协议及相关法律法规的约束。</b>", body_style))
    story.append(Spacer(1, 0.4 * inch))

    # 签名区域（留空）
    sign_data = [
        ['声明人：________________________', '日期（年/月/日）：________________________']
    ]
    sign_table = Table(sign_data, colWidths=[3*inch, 3.2*inch])
    sign_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), normal_font),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(sign_table)
    story.append(Spacer(1, 0.4 * inch))

    # 法律提示
    story.append(Paragraph(
        "<b>重要法律提示</b>",
        heading_style
    ))
    story.append(Paragraph(
        "本文件可作为您意愿的强烈表达，协助继承人沟通，但不替代正式公证遗嘱。"
        "建议在制定此声明后，咨询专业律师，并考虑进行公证。",
        warning_style
    ))
    story.append(Spacer(1, 0.2 * inch))

    # 免责声明
    story.append(Paragraph(
        "<b>免责声明</b>",
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
