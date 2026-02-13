"""
后台管理系统 - CRUD操作模块
"""
from flask import jsonify
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError

from models import db, User, DigitalAsset, DigitalWill, PlatformPolicy, Story, FAQ


# ============================================================================
# 用户CRUD
# ============================================================================

class UserCRUD:
    """用户CRUD操作"""

    @staticmethod
    def create_user(data):
        """创建用户"""
        try:
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            is_admin = data.get('is_admin', False)
            is_active = data.get('is_active', True)

            if not all([username, email, password]):
                return jsonify({'success': False, 'message': '请填写必填字段'}), 400

            # 检查用户名是否已存在
            if User.query.filter_by(username=username).first():
                return jsonify({'success': False, 'message': '用户名已存在'}), 400

            # 检查邮箱是否已存在
            if User.query.filter_by(email=email).first():
                return jsonify({'success': False, 'message': '邮箱已被注册'}), 400

            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                is_admin=is_admin,
                is_active=is_active
            )

            db.session.add(user)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': '用户创建成功',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Create failed: {str(e)}'}), 500

    @staticmethod
    def update_user(user_id, data):
        """更新用户"""
        try:
            user = User.query.get_or_404(user_id)

            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            is_admin = data.get('is_admin')
            is_active = data.get('is_active')

            if username and username != user.username:
                if User.query.filter_by(username=username).first():
                    return jsonify({'success': False, 'message': '用户名已存在'}), 400
                user.username = username

            if email and email != user.email:
                if User.query.filter_by(email=email).first():
                    return jsonify({'success': False, 'message': '邮箱已被注册'}), 400
                user.email = email

            if password:
                user.password_hash = generate_password_hash(password)

            if is_admin is not None:
                user.is_admin = is_admin

            if is_active is not None:
                user.is_active = is_active

            db.session.commit()

            return jsonify({
                'success': True,
                'message': '用户更新成功'
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Update failed: {str(e)}'}), 500

    @staticmethod
    def toggle_status(user_id):
        """切换用户状态"""
        try:
            user = User.query.get_or_404(user_id)
            user.is_active = not user.is_active
            db.session.commit()

            return jsonify({
                'success': True,
                'message': f'User status updated to {"enabled" if user.is_active else "disabled"}',
                'is_active': user.is_active
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Update failed: {str(e)}'}), 500

    @staticmethod
    def delete_user(user_id):
        """删除用户"""
        try:
            user = User.query.get_or_404(user_id)

            # 删除关联的数字资产和遗嘱
            DigitalAsset.query.filter_by(user_id=user_id).delete()
            DigitalWill.query.filter_by(user_id=user_id).delete()

            db.session.delete(user)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': '用户删除成功'
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Deletion failed: {str(e)}'}), 500


user_crud = UserCRUD()


# ============================================================================
# 资产CRUD
# ============================================================================

class AssetCRUD:
    """数字资产CRUD操作"""

    @staticmethod
    def delete_asset(asset_id):
        """删除资产"""
        try:
            asset = DigitalAsset.query.get_or_404(asset_id)
            db.session.delete(asset)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': '资产删除成功'
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Deletion failed: {str(e)}'}), 500


asset_crud = AssetCRUD()


# ============================================================================
# 遗嘱CRUD
# ============================================================================

class WillCRUD:
    """数字遗嘱CRUD操作"""

    @staticmethod
    def delete_will(will_id):
        """删除遗嘱"""
        try:
            will = DigitalWill.query.get_or_404(will_id)
            db.session.delete(will)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': '遗嘱删除成功'
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Deletion failed: {str(e)}'}), 500

    @staticmethod
    def update_will_status(will_id, data):
        """更新遗嘱状态"""
        try:
            will = DigitalWill.query.get_or_404(will_id)
            new_status = data.get('status')

            # 验证状态值
            valid_statuses = ['draft', 'confirmed', 'archived']
            if new_status not in valid_statuses:
                return jsonify({
                    'success': False,
                    'message': f'无效的状态值，必须是: {", ".join(valid_statuses)}'
                }), 400

            will.status = new_status
            db.session.commit()

            return jsonify({
                'success': True,
                'message': f'遗嘱状态已更新为: {new_status}'
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Update failed: {str(e)}'}), 500


will_crud = WillCRUD()


# ============================================================================
# 内容CRUD
# ============================================================================

class ContentCRUD:
    """内容CRUD操作"""

    @staticmethod
    def create_policy(data):
        """创建平台政策"""
        try:
            platform_name = data.get('platform_name')
            policy_content = data.get('policy_content')
            attitude = data.get('attitude')
            inherit_possibility = data.get('inherit_possibility')
            legal_basis = data.get('legal_basis', '')
            customer_service = data.get('customer_service', '')
            risk_warning = data.get('risk_warning', '')

            if not all([platform_name, policy_content, attitude, inherit_possibility]):
                return jsonify({'success': False, 'message': '请填写必填字段'}), 400

            policy = PlatformPolicy(
                platform_name=platform_name,
                policy_content=policy_content,
                attitude=attitude,
                inherit_possibility=inherit_possibility,
                legal_basis=legal_basis,
                customer_service=customer_service,
                risk_warning=risk_warning
            )

            db.session.add(policy)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': '政策创建成功'
            }), 201

        except IntegrityError:
            db.session.rollback()
            return jsonify({'success': False, 'message': '该平台已存在'}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Create failed: {str(e)}'}), 500

    @staticmethod
    def update_policy(policy_id, data):
        """更新平台政策"""
        try:
            policy = PlatformPolicy.query.get_or_404(policy_id)

            for field in ['platform_name', 'policy_content', 'attitude',
                         'inherit_possibility', 'legal_basis', 'customer_service', 'risk_warning']:
                if field in data:
                    setattr(policy, field, data[field])

            db.session.commit()

            return jsonify({
                'success': True,
                'message': '政策更新成功'
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Update failed: {str(e)}'}), 500

    @staticmethod
    def delete_policy(policy_id):
        """删除平台政策"""
        try:
            policy = PlatformPolicy.query.get_or_404(policy_id)
            db.session.delete(policy)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': '政策删除成功'
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Deletion failed: {str(e)}'}), 500

    @staticmethod
    def create_faq(data):
        """创建FAQ"""
        try:
            question = data.get('question')
            answer = data.get('answer')
            category = data.get('category')
            order = data.get('order', 0)

            if not all([question, answer, category]):
                return jsonify({'success': False, 'message': '请填写必填字段'}), 400

            faq = FAQ(
                question=question,
                answer=answer,
                category=category,
                order=order
            )

            db.session.add(faq)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'FAQ创建成功'
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Create failed: {str(e)}'}), 500

    @staticmethod
    def update_faq(faq_id, data):
        """更新FAQ"""
        try:
            faq = FAQ.query.get_or_404(faq_id)

            for field in ['question', 'answer', 'category', 'order']:
                if field in data:
                    setattr(faq, field, data[field])

            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'FAQ更新成功'
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Update failed: {str(e)}'}), 500

    @staticmethod
    def delete_faq(faq_id):
        """删除FAQ"""
        try:
            faq = FAQ.query.get_or_404(faq_id)
            db.session.delete(faq)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'FAQ删除成功'
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Deletion failed: {str(e)}'}), 500

    @staticmethod
    def approve_story(story_id):
        """审核通过故事"""
        try:
            story = Story.query.get_or_404(story_id)
            story.status = 'approved'
            db.session.commit()

            return jsonify({
                'success': True,
                'message': '故事已通过审核'
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Operation failed: {str(e)}'}), 500

    @staticmethod
    def reject_story(story_id):
        """审核拒绝故事"""
        try:
            story = Story.query.get_or_404(story_id)
            story.status = 'rejected'
            db.session.commit()

            return jsonify({
                'success': True,
                'message': '故事已拒绝'
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Operation failed: {str(e)}'}), 500

    @staticmethod
    def delete_story(story_id):
        """删除故事"""
        try:
            story = Story.query.get_or_404(story_id)
            db.session.delete(story)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': '故事删除成功'
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Deletion failed: {str(e)}'}), 500


content_crud = ContentCRUD()
