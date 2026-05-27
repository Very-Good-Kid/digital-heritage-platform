"""重置管理员密码"""
import sys
sys.path.insert(0, '.')
from app import app
from models import db, User

with app.app_context():
    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        print("系统中没有管理员账号，请先运行 python scripts/create_admin.py")
        sys.exit(1)
    
    print(f"找到管理员: {admin.username} ({admin.email})")
    new_pwd = input("请输入新密码: ").strip()
    if len(new_pwd) < 6:
        print("密码不能少于6位")
        sys.exit(1)
    
    admin.set_password(new_pwd)
    db.session.commit()
    print(f"管理员 {admin.username} 密码已重置成功！")
