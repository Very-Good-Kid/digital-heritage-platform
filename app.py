from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
import os
from models import db, User, DigitalAsset, DigitalWill, PlatformPolicy, Story, FAQ
from utils.encryption import encrypt_data, decrypt_data
from utils.pdf_generator import generate_will_pdf
from config import config

# 注册后台管理蓝图
from admin import admin_bp

# 辅助函数
def get_china_time():
    """获取中国时区的当前时间"""
    utc_now = datetime.now(timezone.utc)
    china_tz = timezone(timedelta(hours=8))
    return utc_now.astimezone(china_tz)

# 初始化Flask应用
app = Flask(__name__)
app.config.from_object(config['default'])

# 确保数据目录存在（在应用启动前）
data_dir = app.config.get('DATA_DIR', 'instance')
if not os.path.exists(data_dir):
    try:
        os.makedirs(data_dir, exist_ok=True)
        print(f"Created data directory: {data_dir}")
    except Exception as e:
        print(f"Warning: Could not create data directory {data_dir}: {e}")

# 运行时字体安装（Render 免费版优化）
def setup_fonts_on_startup():
    """在应用启动时设置字体"""
    try:
        print("[INFO] Setting up fonts for PDF generation...")
        import subprocess
        import sys

        # 运行字体安装脚本
        script_path = os.path.join(os.path.dirname(__file__), 'install_fonts_runtime.py')
        if os.path.exists(script_path):
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=300
            )
            print(result.stdout)
            if result.stderr:
                print("[WARN]", result.stderr)
        else:
            print("[WARN] Font installation script not found, skipping...")

    except Exception as e:
        print(f"[WARN] Font setup failed: {e}")
        print("[INFO] Application will continue with default fonts")

# 初始化CSRF保护
csrf = CSRFProtect(app)

# 初始化扩展
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '请先登录访问此页面'

# 注册蓝图
app.register_blueprint(admin_bp)

# 创建必要的目录
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/uploads', exist_ok=True)
os.makedirs('temp_pdfs', exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 路由：首页
@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

# 路由：用户认证
@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not all([username, email, password, confirm_password]):
            flash('请填写所有字段', 'error')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('两次输入的密码不一致', 'error')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'error')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册', 'error')
            return redirect(url_for('register'))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )

        try:
            db.session.add(user)
            db.session.commit()
            flash('注册成功，请登录', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('注册失败，请重试', 'error')
            return redirect(url_for('register'))

    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')

            # 如果指定了next页面，跳转到next页面
            if next_page:
                return redirect(next_page)

            # 管理员跳转到后台，普通用户跳转到用户仪表盘
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('用户名或密码错误', 'error')

    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    """用户登出"""
    logout_user()
    flash('已成功登出', 'success')
    return redirect(url_for('index'))

# 路由：用户仪表盘
@app.route('/dashboard')
@login_required
def dashboard():
    """用户仪表盘"""
    # 应用多租户数据隔离
    assets = DigitalAsset.query
    wills = DigitalWill.query

    # 管理员可以看所有数据，普通用户只能看自己的数据
    if not current_user.is_admin:
        assets = assets.filter_by(user_id=current_user.id)
        wills = wills.filter_by(user_id=current_user.id)

    assets = assets.order_by(DigitalAsset.created_at.desc()).all()
    wills = wills.order_by(DigitalWill.created_at.desc()).all()
    return render_template('dashboard/index.html', assets=assets, wills=wills)

# 路由：数字资产清单
@app.route('/assets', methods=['GET', 'POST'])
@login_required
def assets():
    """数字资产清单"""
    if request.method == 'POST':
        platform_name = request.form.get('platform_name')
        account = request.form.get('account')
        password = request.form.get('password')
        category = request.form.get('category')
        notes = request.form.get('notes')

        encrypted_password = encrypt_data(password) if password else None

        asset = DigitalAsset(
            user_id=current_user.id,
            platform_name=platform_name,
            account=account,
            encrypted_password=encrypted_password,
            category=category,
            notes=notes
        )

        try:
            db.session.add(asset)
            db.session.commit()
            flash('数字资产添加成功', 'success')
        except Exception as e:
            db.session.rollback()
            flash('添加失败，请重试', 'error')

        return redirect(url_for('assets'))

    # 应用多租户数据隔离
    assets_query = DigitalAsset.query
    if not current_user.is_admin:
        assets_query = assets_query.filter_by(user_id=current_user.id)

    assets = assets_query.order_by(DigitalAsset.created_at.desc()).all()
    categories = ['社交', '金融', '记忆', '虚拟财产']
    return render_template('assets/index.html', assets=assets, categories=categories)

@app.route('/assets/download-template/<format>')
@login_required
def download_template(format):
    """下载数字资产模板"""
    if format == 'excel':
        return generate_excel_template()
    elif format == 'pdf':
        return generate_pdf_template()
    else:
        flash('不支持的模板格式', 'error')
        return redirect(url_for('assets'))

def generate_excel_template():
    """生成Excel模板"""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

        wb = Workbook()
        ws = wb.active
        ws.title = "数字资产清单"

        # 设置列宽
        ws.column_dimensions['A'].width = 20
        ws.column_dimensions['B'].width = 25
        ws.column_dimensions['C'].width = 20
        ws.column_dimensions['D'].width = 15
        ws.column_dimensions['E'].width = 40

        # 定义样式
        header_font = Font(name='微软雅黑', size=12, bold=True, color='FFFFFF')
        header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
        header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        # 表头
        headers = ['平台名称', '账号', '密码（可选）', '分类', '备注说明']
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = border

        # 添加示例数据
        sample_data = [
            ['微信', '13800138000', '', '社交', '主要社交账号'],
            ['QQ', '123456789', '', '社交', '工作用QQ'],
            ['支付宝', '13800138000', 'password123', '金融', '主要支付账户'],
            ['百度网盘', 'user@example.com', 'pwd123', '记忆', '存储重要文件'],
            ['王者荣耀', 'game_user', 'gamepass', '虚拟财产', '游戏账号']
        ]

        for row_idx, row_data in enumerate(sample_data, start=2):
            for col_idx, value in enumerate(row_data, start=1):
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                cell.border = border

        # 添加说明
        ws.append([])
        ws.append(['填写说明：'])
        ws.append(['1. 平台名称：填写数字资产所属平台（如微信、QQ、抖音等）'])
        ws.append(['2. 账号：填写您的账号信息（手机号、邮箱、用户名等）'])
        ws.append(['3. 密码：选填，密码将加密存储'])
        ws.append(['4. 分类：选择资产分类（社交、金融、记忆、虚拟财产）'])
        ws.append(['5. 备注：填写任何有用的补充信息'])

        # 保存到内存
        from io import BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='数字资产清单模板.xlsx'
        )
    except ImportError:
        flash('Excel模板生成功能需要安装openpyxl库', 'error')
        return redirect(url_for('assets'))
    except Exception as e:
        flash(f'模板生成失败：{str(e)}', 'error')
        return redirect(url_for('assets'))

def generate_pdf_template():
    """生成PDF模板"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from io import BytesIO

        output = BytesIO()
        doc = SimpleDocTemplate(output, pagesize=A4)

        # 创建样式
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            spaceAfter=12,
            spaceBefore=15
        )

        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontName='Helvetica',
            fontSize=10,
            spaceAfter=10,
            leading=14
        )

        story = []

        # 标题
        story.append(Paragraph("数字资产清单模板", title_style))
        story.append(Spacer(1, 0.2 * inch))

        # 说明
        story.append(Paragraph("<b>填写说明：</b>", heading_style))
        story.append(Paragraph(
            "请按照以下格式填写您的数字资产信息。填写完成后，可以将此表格作为参考，"
            "在网站中添加您的数字资产。",
            body_style
        ))
        story.append(Spacer(1, 0.3 * inch))

        # 表格
        table_data = [
            ['平台名称', '账号', '密码（可选）', '分类', '备注说明'],
            ['微信', '13800138000', '', '社交', '主要社交账号'],
            ['QQ', '123456789', '', '社交', '工作用QQ'],
            ['支付宝', '13800138000', '', '金融', '主要支付账户'],
            ['百度网盘', 'user@example.com', '', '记忆', '存储重要文件'],
            ['王者荣耀', 'game_user', '', '虚拟财产', '游戏账号'],
            ['', '', '', '', ''],
            ['', '', '', '', ''],
            ['', '', '', '', ''],
            ['', '', '', '', ''],
        ]

        table = Table(table_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 1*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))

        story.append(table)
        story.append(Spacer(1, 0.3 * inch))

        # 详细说明
        story.append(Paragraph("<b>字段说明：</b>", heading_style))
        story.append(Paragraph(
            "<b>1. 平台名称：</b>填写数字资产所属平台（如微信、QQ、抖音、支付宝等）",
            body_style
        ))
        story.append(Paragraph(
            "<b>2. 账号：</b>填写您的账号信息（手机号、邮箱、用户名等）",
            body_style
        ))
        story.append(Paragraph(
            "<b>3. 密码：</b>选填，密码将加密存储，请妥善保管",
            body_style
        ))
        story.append(Paragraph(
            "<b>4. 分类：</b>选择资产分类（社交、金融、记忆、虚拟财产）",
            body_style
        ))
        story.append(Paragraph(
            "<b>5. 备注：</b>填写任何有用的补充信息",
            body_style
        ))
        story.append(Spacer(1, 0.3 * inch))

        # 分类说明
        story.append(Paragraph("<b>资产分类说明：</b>", heading_style))
        story.append(Paragraph(
            "<b>社交：</b>社交媒体账号（微信、QQ、微博、抖音等）",
            body_style
        ))
        story.append(Paragraph(
            "<b>金融：</b>金融账户（支付宝、微信支付、银行网银、投资理财等）",
            body_style
        ))
        story.append(Paragraph(
            "<b>记忆：</b>记忆存储（云存储、相册、文档、笔记等）",
            body_style
        ))
        story.append(Paragraph(
            "<b>虚拟财产：</b>虚拟资产（游戏账号、虚拟货币、其他虚拟物品）",
            body_style
        ))

        # 生成PDF
        doc.build(story)
        output.seek(0)

        return send_file(
            output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='数字资产清单模板.pdf'
        )
    except Exception as e:
        flash(f'PDF模板生成失败：{str(e)}', 'error')
        return redirect(url_for('assets'))

@app.route('/assets/<int:asset_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_asset(asset_id):
    """编辑数字资产"""
    asset = DigitalAsset.query.get_or_404(asset_id)

    if asset.user_id != current_user.id:
        flash('无权访问此资产', 'error')
        return redirect(url_for('assets'))

    if request.method == 'POST':
        asset.platform_name = request.form.get('platform_name')
        asset.account = request.form.get('account')
        password = request.form.get('password')
        asset.category = request.form.get('category')
        asset.notes = request.form.get('notes')

        if password:
            asset.encrypted_password = encrypt_data(password)

        asset.updated_at = get_china_time()

        try:
            db.session.commit()
            flash('资产更新成功', 'success')
            return redirect(url_for('assets'))
        except Exception as e:
            db.session.rollback()
            flash('更新失败，请重试', 'error')

    categories = ['社交', '金融', '记忆', '虚拟财产']
    return render_template('assets/edit.html', asset=asset, categories=categories)

@app.route('/assets/<int:asset_id>/delete', methods=['POST'])
@login_required
def delete_asset(asset_id):
    """删除数字资产"""
    asset = DigitalAsset.query.get_or_404(asset_id)

    if asset.user_id != current_user.id:
        flash('无权访问此资产', 'error')
        return redirect(url_for('assets'))

    try:
        db.session.delete(asset)
        db.session.commit()
        flash('资产删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash('删除失败，请重试', 'error')

    return redirect(url_for('assets'))

@app.route('/assets/<int:asset_id>/decrypt', methods=['POST'])
@login_required
def decrypt_asset(asset_id):
    """解密资产密码"""
    asset = DigitalAsset.query.get_or_404(asset_id)

    if asset.user_id != current_user.id:
        flash('无权访问此资产', 'error')
        return redirect(url_for('assets'))

    if asset.encrypted_password:
        try:
            decrypted_password = decrypt_data(asset.encrypted_password)
            return jsonify({'success': True, 'password': decrypted_password})
        except Exception as e:
            return jsonify({'success': False, 'message': '解密失败'})
    else:
        return jsonify({'success': False, 'message': '无密码信息'})

# 路由：数字遗嘱
@app.route('/wills', methods=['GET', 'POST'])
@login_required
def wills():
    """数字遗嘱列表"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        heir_info = request.form.get('heir_info', '')
        special_notes = request.form.get('special_notes', '')
        assets_data = request.form.get('assets_data', '{}')

        try:
            assets_data_json = __import__('json').loads(assets_data)
        except:
            assets_data_json = {}

        # 将新字段合并到assets_data中
        if heir_info:
            assets_data_json['heir_info'] = heir_info
        if special_notes:
            assets_data_json['special_notes'] = special_notes

        will = DigitalWill(
            user_id=current_user.id,
            title=title,
            description=description,
            assets_data=assets_data_json,
            status='draft'
        )

        try:
            db.session.add(will)
            db.session.commit()
            flash('数字遗嘱创建成功', 'success')
            return redirect(url_for('wills'))
        except Exception as e:
            db.session.rollback()
            flash('创建失败，请重试', 'error')

    # 应用多租户数据隔离
    wills_query = DigitalWill.query
    assets_query = DigitalAsset.query

    if not current_user.is_admin:
        wills_query = wills_query.filter_by(user_id=current_user.id)
        assets_query = assets_query.filter_by(user_id=current_user.id)

    wills = wills_query.order_by(DigitalWill.created_at.desc()).all()
    assets = assets_query.all()
    return render_template('wills/index.html', wills=wills, assets=assets)

@app.route('/wills/download-template/<format>')
@login_required
def download_will_template(format):
    """下载遗嘱模板"""
    if format == 'excel':
        return generate_will_excel_template()
    elif format == 'pdf':
        return generate_will_pdf_template()
    else:
        flash('不支持的模板格式', 'error')
        return redirect(url_for('wills'))

def generate_will_excel_template():
    """生成遗嘱Excel模板"""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

        wb = Workbook()
        ws = wb.active
        ws.title = "数字遗产意愿声明"

        # 设置列宽
        ws.column_dimensions['A'].width = 8
        ws.column_dimensions['B'].width = 25
        ws.column_dimensions['C'].width = 40

        # 定义样式
        title_font = Font(name='微软雅黑', size=16, bold=True, color='FFFFFF')
        title_fill = PatternFill(start_color='C00000', end_color='C00000', fill_type='solid')
        header_font = Font(name='微软雅黑', size=12, bold=True)
        header_fill = PatternFill(start_color='FFC000', end_color='FFC000', fill_type='solid')
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        # 标题
        ws.merge_cells('A1:C1')
        title_cell = ws['A1']
        title_cell.value = '数字遗产意愿声明模板'
        title_cell.font = title_font
        title_cell.fill = title_fill
        title_cell.alignment = Alignment(horizontal='center', vertical='center')

        # 基本信息
        ws.append([])
        ws.append(['基本信息'])
        ws.append(['遗嘱标题', '我的数字遗产处理意愿'])
        ws.append(['总体意愿说明', '请说明您对数字遗产的总体处理意愿'])
        ws.append(['指定继承人信息', '填写继承人的姓名、关系、联系方式等信息'])
        ws.append(['特别说明', '其他需要特别说明的事项'])

        # 数字资产处理表
        ws.append([])
        ws.append(['数字资产处理意愿'])
        headers = ['平台名称', '账号', '处理方式']
        ws.append(headers)

        # 设置表头样式
        for col in range(1, 4):
            cell = ws.cell(row=ws.max_row, column=col)
            cell.font = header_font
            cell.fill = header_fill
            cell.border = border

        # 示例数据
        sample_data = [
            ['微信', '13800138000', '指定继承人'],
            ['QQ', '123456789', '转为纪念模式'],
            ['支付宝', '13800138000', '指定继承人'],
            ['百度网盘', 'user@example.com', '委托删除'],
        ]

        for row_data in sample_data:
            ws.append(row_data)
            for col in range(1, 4):
                cell = ws.cell(row=ws.max_row, column=col)
                cell.border = border

        # 处理方式说明
        ws.append([])
        ws.append(['处理方式说明：'])
        ws.append(['1. 指定继承人：将数字资产转移给指定的继承人'])
        ws.append(['2. 转为纪念模式：保持账户活跃状态，但不进行登录操作'])
        ws.append(['3. 委托删除：授权平台或继承人删除账户'])
        ws.append(['4. 其他处理方式：根据具体情况自定义处理方式'])

        # 法律提示
        ws.append([])
        ws.append(['重要法律提示：'])
        ws.append(['本文件可作为您意愿的强烈表达，协助继承人沟通，'])
        ws.append(['但不替代正式公证遗嘱。建议咨询专业律师。'])

        # 保存到内存
        from io import BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='数字遗产意愿声明模板.xlsx'
        )
    except ImportError:
        flash('Excel模板生成功能需要安装openpyxl库', 'error')
        return redirect(url_for('wills'))
    except Exception as e:
        flash(f'模板生成失败：{str(e)}', 'error')
        return redirect(url_for('wills'))

def generate_will_pdf_template():
    """生成遗嘱PDF模板"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib import colors
        from io import BytesIO

        output = BytesIO()
        doc = SimpleDocTemplate(output, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)

        # 创建样式
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=20,
            spaceAfter=30,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20
        )

        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontName='Helvetica',
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            leading=16
        )

        warning_style = ParagraphStyle(
            'CustomWarning',
            parent=styles['BodyText'],
            fontName='Helvetica-Oblique',
            fontSize=9,
            textColor=colors.red,
            spaceAfter=20,
            alignment=TA_CENTER
        )

        story = []

        # 标题
        story.append(Paragraph("数字遗产意愿声明", title_style))
        story.append(Spacer(1, 0.3 * inch))

        # 基本信息说明
        story.append(Paragraph("<b>一、基本信息</b>", heading_style))
        story.append(Paragraph(
            "<b>遗嘱标题：</b>请填写遗嘱标题，例如：我的数字遗产处理意愿",
            body_style
        ))
        story.append(Paragraph(
            "<b>总体意愿说明：</b>请简要说明您对数字遗产的总体处理意愿",
            body_style
        ))
        story.append(Paragraph(
            "<b>指定继承人信息：</b>请填写继承人的姓名、关系、联系方式等详细信息",
            body_style
        ))
        story.append(Paragraph(
            "<b>特别说明：</b>请填写其他需要特别说明的事项",
            body_style
        ))
        story.append(Spacer(1, 0.3 * inch))

        # 数字资产处理表
        story.append(Paragraph("<b>二、数字资产处理意愿</b>", heading_style))
        story.append(Paragraph(
            "请为每个数字资产选择处理方式，并在下表中填写详细信息：",
            body_style
        ))

        table_data = [
            ['平台名称', '账号', '处理方式', '备注'],
            ['微信', '13800138000', '指定继承人', '主要社交账号'],
            ['QQ', '123456789', '转为纪念模式', '工作用QQ'],
            ['支付宝', '13800138000', '指定继承人', '主要支付账户'],
            ['百度网盘', 'user@example.com', '委托删除', '存储重要文件'],
            ['', '', '', ''],
            ['', '', '', ''],
            ['', '', '', ''],
        ]

        table = Table(table_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))

        story.append(table)
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
        story.append(Paragraph(
            "<b>微信：</b>账户所有权归腾讯公司所有，继承需要提供相关证明材料。",
            body_style
        ))
        story.append(Paragraph(
            "<b>QQ：</b>可以申请继承，需要提供死亡证明、亲属关系证明等材料。",
            body_style
        ))
        story.append(Paragraph(
            "<b>抖音：</b>继承政策相对严格，需要提供法律文件和身份证明。",
            body_style
        ))
        story.append(Spacer(1, 0.3 * inch))

        # 法律提示
        story.append(Paragraph(
            "<b>五、重要法律提示</b>",
            heading_style
        ))
        story.append(Paragraph(
            "本文件可作为您意愿的强烈表达，协助继承人沟通，但不替代正式公证遗嘱。"
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

        # 生成PDF
        doc.build(story)
        output.seek(0)

        return send_file(
            output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='数字遗产意愿声明模板.pdf'
        )
    except Exception as e:
        flash(f'PDF模板生成失败：{str(e)}', 'error')
        return redirect(url_for('wills'))

@app.route('/wills/<int:will_id>/view', methods=['GET'])
@login_required
def view_will(will_id):
    """查看数字遗嘱"""
    will = DigitalWill.query.get_or_404(will_id)

    if will.user_id != current_user.id:
        flash('无权访问此遗嘱', 'error')
        return redirect(url_for('wills'))

    return render_template('wills/view.html', will=will)

@app.route('/wills/<int:will_id>/generate_pdf', methods=['GET'])
@login_required
def generate_pdf(will_id):
    """生成遗嘱PDF"""
    will = DigitalWill.query.get_or_404(will_id)

    if will.user_id != current_user.id:
        flash('无权访问此遗嘱', 'error')
        return redirect(url_for('wills'))

    try:
        print(f"Generating PDF for will {will_id}: {will.title}")
        pdf_path = generate_will_pdf(will)
        print(f"PDF generated at: {pdf_path}")

        if pdf_path and os.path.exists(pdf_path):
            return send_file(pdf_path, as_attachment=True, download_name=f'数字遗嘱_{will.title}.pdf')
        else:
            flash('PDF文件生成失败，请稍后重试', 'error')
            return redirect(url_for('view_will', will_id=will_id))
    except Exception as e:
        print(f"PDF generation error: {e}")
        import traceback
        traceback.print_exc()
        flash(f'PDF生成失败：{str(e)}', 'error')
        return redirect(url_for('view_will', will_id=will_id))

@app.route('/wills/<int:will_id>/delete', methods=['POST'])
@login_required
def delete_will(will_id):
    """删除数字遗嘱"""
    will = DigitalWill.query.get_or_404(will_id)

    if will.user_id != current_user.id:
        flash('无权访问此遗嘱', 'error')
        return redirect(url_for('wills'))

    try:
        db.session.delete(will)
        db.session.commit()
        flash('遗嘱删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash('删除失败，请重试', 'error')

    return redirect(url_for('wills'))


@app.route('/wills/<int:will_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_will(will_id):
    """编辑数字遗嘱"""
    will = DigitalWill.query.get_or_404(will_id)

    # 权限控制：只能编辑自己的遗嘱
    if will.user_id != current_user.id:
        flash('无权访问此遗嘱', 'error')
        return redirect(url_for('wills'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        heir_info = request.form.get('heir_info', '')
        special_notes = request.form.get('special_notes', '')
        assets_data = request.form.get('assets_data', '{}')
        new_status = request.form.get('status', will.status)

        # 状态变更权限控制
        # 只有管理员可以设置confirmed或archived状态
        # 用户自己只能设置为draft状态
        if new_status != will.status:
            if not current_user.is_admin:
                if new_status != 'draft':
                    flash('只有管理员可以将遗嘱状态设置为已确认或已归档', 'error')
                    return redirect(url_for('edit_will', will_id=will_id))
            else:
                # 管理员可以更改任何状态
                will.status = new_status

        # 验证JSON格式
        try:
            if assets_data:
                import json
                assets_data_json = json.loads(assets_data)
            else:
                assets_data_json = {}
        except json.JSONDecodeError:
            assets_data_json = {}

        # 将新字段合并到assets_data中
        if heir_info:
            assets_data_json['heir_info'] = heir_info
        if special_notes:
            assets_data_json['special_notes'] = special_notes

        # 更新其他字段
        if title:
            will.title = title
        if description:
            will.description = description
        will.assets_data = assets_data_json
        will.updated_at = get_china_time()

        try:
            db.session.commit()
            flash('遗嘱更新成功', 'success')
            return redirect(url_for('wills'))
        except Exception as e:
            db.session.rollback()
            flash('更新失败，请重试', 'error')

    assets = DigitalAsset.query.filter_by(user_id=current_user.id).all()
    return render_template('wills/edit.html', will=will, assets=assets)



@app.route('/wills/<int:will_id>/status', methods=['POST'])
@login_required
def update_will_status(will_id):
    """更新遗嘱状态"""
    will = DigitalWill.query.get_or_404(will_id)

    # 权限控制
    if will.user_id != current_user.id and not current_user.is_admin:
        flash('无权访问此遗嘱', 'error')
        return redirect(url_for('wills'))

    new_status = request.json.get('status')

    # 状态值验证
    valid_statuses = ['draft', 'confirmed', 'archived']
    if new_status not in valid_statuses:
        return jsonify({'success': False, 'message': '无效的状态值'}), 400

    # 业务规则：
    # 1. 用户只能在"草稿"和"已确认"之间切换
    # 2. 用户不能将遗嘱改为"已归档"
    # 3. 管理员可以更改任何状态，无限制
    if not current_user.is_admin:
        # 非管理员用户
        # 允许在草稿和已确认之间切换
        if new_status in ['draft', 'confirmed']:
            if will.status != new_status:
                will.status = new_status
        else:
            # 用户尝试改为已归档，拒绝
            return jsonify({
                'success': False,
                'message': '只有管理员可以将遗嘱状态设置为已归档'
            }), 403
    else:
        # 管理员可以更改任何状态，无限制
        will.status = new_status

    will.updated_at = get_china_time()



    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '遗嘱状态更新成功',
            'new_status': will.status
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

# 路由：平台政策矩阵
@app.route('/policies')
def policies():
    """平台政策矩阵"""
    policies = PlatformPolicy.query.order_by(PlatformPolicy.platform_name).all()
    return render_template('policies/index.html', policies=policies)

# 路由：继承导航
@app.route('/inheritance-guide', methods=['GET', 'POST'])
def inheritance_guide():
    """数字资产继承导航"""
    if request.method == 'POST':
        platform = request.form.get('platform')
        scenario = request.form.get('scenario')
        
        # 验证参数
        if not platform or not scenario:
            flash('请选择平台和继承情景', 'error')
            return redirect(url_for('inheritance_guide'))
        
        return redirect(url_for('inheritance_result', platform=platform, scenario=scenario))

    platforms = PlatformPolicy.query.filter(PlatformPolicy.platform_name.in_(['微信', 'QQ', '抖音'])).all()
    scenarios = [
        {'id': 'scenario1', 'name': '有遗嘱+有密码', 'description': '您拥有合法的数字遗嘱和账户密码'},
        {'id': 'scenario2', 'name': '有遗嘱+无密码', 'description': '您拥有合法的数字遗嘱但没有账户密码'},
        {'id': 'scenario3', 'name': '无遗嘱+无密码', 'description': '您没有数字遗嘱和账户密码'}
    ]
    return render_template('inheritance-guide/index.html', platforms=platforms, scenarios=scenarios)

@app.route('/inheritance-result')
def inheritance_result():
    """继承导航结果"""
    platform = request.args.get('platform')
    scenario = request.args.get('scenario')

    policy = PlatformPolicy.query.filter_by(platform_name=platform).first()
    if not policy:
        flash('未找到相关平台信息', 'error')
        return redirect(url_for('inheritance_guide'))

    steps = generate_inheritance_steps(platform, scenario, policy)
    return render_template('inheritance-guide/result.html',
                         platform=platform,
                         scenario=scenario,
                         policy=policy,
                         steps=steps)

def generate_inheritance_steps(platform, scenario, policy):
    """生成继承步骤"""
    steps = []

    if scenario == 'scenario1':  # 有遗嘱+有密码
        steps = [
            {
                'step': 1,
                'title': '准备法律文件',
                'description': f'准备数字遗嘱、身份证明、死亡证明等文件',
                'materials': ['数字遗嘱原件', '继承人身份证', '逝者死亡证明', '亲属关系证明']
            },
            {
                'step': 2,
                'title': f'联系{platform}客服',
                'description': f'通过官方渠道联系{platform}客服，说明继承需求',
                'materials': [f'{platform}客服电话', f'{platform}官方邮箱']
            },
            {
                'step': 3,
                'title': '提交申请材料',
                'description': '按照平台要求提交所有必要材料',
                'materials': ['所有准备的法律文件', '继承申请表']
            },
            {
                'step': 4,
                'title': '等待审核',
                'description': '平台审核申请材料，可能需要补充材料',
                'materials': ['保持联系方式畅通', '准备补充材料']
            }
        ]
    elif scenario == 'scenario2':  # 有遗嘱+无密码
        steps = [
            {
                'step': 1,
                'title': '准备法律文件',
                'description': '准备数字遗嘱、身份证明、死亡证明等文件',
                'materials': ['数字遗嘱原件', '继承人身份证', '逝者死亡证明', '亲属关系证明']
            },
            {
                'step': 2,
                'title': f'联系{platform}客服',
                'description': f'联系{platform}客服说明情况，提供遗嘱作为依据',
                'materials': [f'{platform}客服电话', f'{platform}官方邮箱']
            },
            {
                'step': 3,
                'title': '申请账户恢复',
                'description': '根据平台政策申请账户恢复或转移',
                'materials': ['账户恢复申请表', '身份验证材料']
            },
            {
                'step': 4,
                'title': '法律途径',
                'description': f'如{platform}拒绝，可能需要通过法律途径解决',
                'materials': ['律师函', '法院诉讼材料']
            }
        ]
    elif scenario == 'scenario3':  # 无遗嘱+无密码
        steps = [
            {
                'step': 1,
                'title': '收集证明材料',
                'description': '收集所有能证明继承关系的材料',
                'materials': ['亲属关系证明', '死亡证明', '继承人身份证']
            },
            {
                'step': 2,
                'title': f'联系{platform}客服',
                'description': f'联系{platform}客服了解继承流程',
                'materials': [f'{platform}客服电话', f'{platform}官方邮箱']
            },
            {
                'step': 3,
                'title': '法律咨询',
                'description': '咨询专业律师，了解法律权益',
                'materials': ['律师咨询', '法律文书准备']
            },
            {
                'step': 4,
                'title': '司法程序',
                'description': f'可能需要通过法院程序处理{platform}账户',
                'materials': ['起诉状', '证据材料', '法院传票']
            }
        ]

    return steps

# 路由：故事墙
@app.route('/stories')
def stories():
    """数字记忆故事墙"""
    stories = Story.query.filter_by(status='approved').order_by(Story.created_at.desc()).all()
    return render_template('stories/index.html', stories=stories)


@app.route('/stories/submit', methods=['POST'])
@login_required
def submit_story():
    """提交故事"""
    try:
        title = request.form.get('title')
        category = request.form.get('category')
        content = request.form.get('content')
        author = request.form.get('author')

        if not all([title, category, content, author]):
            return jsonify({'success': False, 'message': '请填写所有必填字段'}), 400

        # 创建故事，状态设为待审核
        story = Story(
            title=title,
            category=category,
            content=content,
            author=author,
            status='pending'
        )

        db.session.add(story)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '故事提交成功！管理员将在审核后发布。'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'提交失败: {str(e)}'}), 500

# 路由：FAQ
@app.route('/faq')
def faq():
    """常见问题解答"""
    faqs = FAQ.query.order_by(FAQ.category, FAQ.order).all()
    # 按指定顺序排序分类
    category_order = ['基础概念', '保护措施', '法律问题']
    categories = sorted(set(faq.category for faq in faqs), key=lambda x: category_order.index(x) if x in category_order else 999)
    return render_template('faq/index.html', faqs=faqs, categories=categories)

# 路由：关于我们
@app.route('/about')
def about():
    """关于我们"""
    return render_template('about.html')

# 路由：后台管理
# 初始化字体和数据库
@app.before_request
def initialize_application():
    """初始化字体和数据库"""
    # 只在第一次请求时初始化
    if not hasattr(initialize_application, 'initialized'):
        try:
            # 1. 首先设置字体
            setup_fonts_on_startup()

            # 2. 然后初始化数据库
            with app.app_context():
                # 确保数据目录存在
                db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
                db_dir = os.path.dirname(db_path)

                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir, exist_ok=True)
                    print(f"Created database directory: {db_dir}")

                # 创建所有表
                db.create_all()
                print("Database tables created successfully")

                # 初始化示例数据
                initialize_sample_data()
                print("Sample data initialized successfully")

            initialize_application.initialized = True
        except Exception as e:
            print(f"Application initialization error: {e}")
            import traceback
            traceback.print_exc()
            # 即使初始化失败，也标记为已初始化，避免重复尝试
            initialize_application.initialized = True
def initialize_sample_data():
    """初始化示例数据"""
    # 检查是否已有数据
    if PlatformPolicy.query.count() > 0 and FAQ.query.count() >= 12:
        return

    # 添加平台政策
    policies = [
        PlatformPolicy(
            platform_name='微信',
            policy_content='微信账户不支持继承，账户长期不使用会被冻结。',
            attitude='明确禁止',
            inherit_possibility='低',
            legal_basis='根据《微信软件许可及服务协议》，用户仅拥有使用权，不拥有所有权',
            customer_service='400-670-0700',
            risk_warning='账户余额可能无法提取，聊天记录可能永久丢失'
        ),
        PlatformPolicy(
            platform_name='QQ',
            policy_content='QQ号码可以申请继承，需要提供相关证明材料。',
            attitude='有限支持',
            inherit_possibility='中',
            legal_basis='腾讯提供账户继承服务，但需要严格的法律文件',
            customer_service='0755-83765566',
            risk_warning='需要提供完整的法律证明文件，审核周期较长'
        ),
        PlatformPolicy(
            platform_name='抖音',
            policy_content='抖音账号继承政策尚不明确，建议联系客服咨询。',
            attitude='态度模糊',
            inherit_possibility='低',
            legal_basis='相关政策尚未明确规定',
            customer_service='400-966-0606',
            risk_warning='继承成功率较低，建议提前做好数据备份'
        )
    ]

    for policy in policies:
        db.session.add(policy)

    # 添加FAQ
    # ============================================================
    # 如何添加新的FAQ：
    # 1. 在下面的列表中添加新的 FAQ() 对象
    # 2. 填写 question（问题）、answer（答案）、category（分类）、order（排序）
    # 3. category 可以是：'基础概念'、'保护措施'、'法律问题' 或新增分类
    # 4. order 用于同一分类内的排序，数字越小越靠前
    # ============================================================
    faqs = [
        FAQ(
            question='数字遗产包括哪些内容？',
            answer='数字遗产包括但不限于：社交媒体账号（微信、QQ、抖音等）、电子邮箱、云存储文件、虚拟货币、游戏账号、在线支付账户、博客文章、个人网站、数字相册、音视频文件等。',
            category='基础概念',
            order=1
        ),
        FAQ(
            question='什么是数字遗嘱？',
            answer='数字遗嘱是指用户在生前制定的关于其数字资产如何处理的书面文件，包括账户信息、密码、处理方式等内容的详细说明。它可以指导继承人如何处理您的数字资产，避免账户丢失或数据永久消失。',
            category='基础概念',
            order=2
        ),
        FAQ(
            question='为什么需要规划数字遗产？',
            answer='1. 避免重要数据永久丢失；2. 保护隐私和个人信息；3. 确保资产（如虚拟货币）不被浪费；4. 减轻家人的心理负担；5. 让数字记忆得以传承；6. 避免平台账户被自动删除。',
            category='基础概念',
            order=3
        ),
        FAQ(
            question='数字资产的价值如何评估？',
            answer='数字资产的价值包括：经济价值（虚拟货币、游戏装备、付费内容等）、情感价值（照片、视频、聊天记录等）、实用价值（付费软件、云存储空间等）。建议定期整理和评估您的数字资产。',
            category='基础概念',
            order=4
        ),
        FAQ(
            question='如何保护我的数字遗产？',
            answer='1. 定期备份重要数据到本地或云端；2. 使用密码管理器安全存储密码；3. 创建数字遗嘱并定期更新；4. 告知家人重要账户信息；5. 了解各平台的继承政策；6. 启用双重认证；7. 定期检查账户安全设置。',
            category='保护措施',
            order=1
        ),
        FAQ(
            question='密码安全应该注意什么？',
            answer='1. 使用强密码（大小写字母、数字、特殊符号组合，至少12位）；2. 不要重复使用密码；3. 定期更换密码（每3-6个月）；4. 启用两步验证；5. 使用密码管理器（如LastPass、1Password）；6. 不要在公共场所输入密码；7. 警惕钓鱼网站。',
            category='保护措施',
            order=2
        ),
        FAQ(
            question='如何选择密码管理器？',
            answer='选择密码管理器时考虑：1. 安全性（是否使用AES-256加密）；2. 跨平台支持（手机、电脑、浏览器）；3. 云同步功能；4. 价格（免费版功能）；5. 用户评价和口碑。推荐工具：LastPass、1Password、Bitwarden、KeePass等。',
            category='保护措施',
            order=3
        ),
        FAQ(
            question='数字遗嘱有法律效力吗？',
            answer='数字遗嘱在我国法律体系中尚未明确认定，但可以作为表达意愿的重要依据。根据《民法典》，遗嘱可以采用多种形式，包括打印、录音录像等。数字遗嘱如果能证明是本人真实意愿，可能被参考。建议配合传统遗嘱使用，并咨询专业律师。',
            category='法律问题',
            order=1
        ),
        FAQ(
            question='继承人的法律权利是什么？',
            answer='根据《民法典》，继承人有权继承被继承人的合法财产。但对于数字财产，法律界定尚不明确：1. 虚拟货币（比特币等）通常被视为财产，可以继承；2. 社交媒体账号（微信、QQ等）通常被视为使用权，不可继承；3. 游戏账号和虚拟道具的继承权取决于平台政策；4. 云存储文件可以继承，但需要密码或法律证明。',
            category='法律问题',
            order=2
        ),
        FAQ(
            question='如何证明数字资产的所有权？',
            answer='证明数字资产所有权需要：1. 账户注册信息和登录记录；2. 交易记录和支付凭证（如购买虚拟货币的记录）；3. 电子邮件或聊天记录证明使用情况；4. 平台开具的资产证明；5. 公证处的公证文件；6. 银行流水证明充值记录。建议保留所有相关凭证。',
            category='法律问题',
            order=3
        ),
        FAQ(
            question='如果平台拒绝继承怎么办？',
            answer='1. 查阅平台服务协议，了解具体条款；2. 准备完整的法律文件（死亡证明、继承公证书等）；3. 联系平台客服，说明情况；4. 寻求法律援助，向法院提起诉讼；5. 向消费者协会投诉；6. 通过媒体曝光引起关注。注意：不同平台处理方式不同，需要具体情况具体分析。',
            category='法律问题',
            order=4
        ),
        FAQ(
            question='跨境数字资产继承有什么特殊问题？',
            answer='1. 法律适用问题：涉及不同国家的法律；2. 语言障碍：需要翻译文件；3. 货币兑换：虚拟货币可能需要兑换；4. 税务问题：可能涉及遗产税；5. 时效问题：各国继承时效不同；6. 证据认证：需要领事认证或海牙认证。建议咨询专业国际律师。',
            category='法律问题',
            order=5
        )
    ]

    for faq in faqs:
        db.session.add(faq)

    # 添加示例故事
    stories = [
        Story(
            title='父亲的微信账号',
            content='父亲去世后，我尝试找回他的微信账号，却遇到了重重困难。这让我意识到数字遗产规划的重要性...',
            author='匿名用户',
            category='情感故事',
            status='approved'
        ),
        Story(
            title='数字时代的告别',
            content='在这个数字时代，我们的记忆、情感都存储在云端。如何让这些珍贵的数字遗产得以延续？',
            author='编辑部',
            category='哲思文章',
            status='approved'
        )
    ]

    for story in stories:
        db.session.add(story)

    db.session.commit()

# 错误处理
@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    db.session.rollback()
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
