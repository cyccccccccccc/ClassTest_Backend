from flask import Flask, request, jsonify, send_file
from .models import db, Contact, ContactMethod
from .utils import export_to_excel, import_from_excel
import os
import tempfile
from sqlalchemy.exc import IntegrityError
def create_app():
    app = Flask(__name__)
    # ⚠️ 请根据你的 MySQL 用户名/密码修改
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/contact_book?charset=utf8mb4'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/api/contacts', methods=['GET'])
    def get_contacts():
        contacts = Contact.query.all()
        result = []
        for c in contacts:
            methods = [{'type': m.method_type, 'value': m.value} for m in c.methods]
            result.append({
                'id': c.id,
                'name': c.name,
                'is_bookmarked': c.is_bookmarked,
                'methods': methods
            })
        return jsonify(result)

    @app.route('/api/contacts', methods=['POST'])
    def add_contact():
        data = request.get_json()
        name = data.get('name', '').strip()
        if not name:
            return jsonify({'error': 'Name is required'}), 400
        contact = Contact(
            name=name,
            is_bookmarked=bool(data.get('is_bookmarked', False))
        )
        db.session.add(contact)
        db.session.flush()

        methods = data.get('methods', [])
        for m in methods:
            m_type = m.get('type')
            m_value = str(m.get('value', '')).strip()
            if m_type in ['phone', 'email', 'social', 'address'] and m_value:
                method = ContactMethod(contact_id=contact.id, method_type=m_type, value=m_value)
                db.session.add(method)
        db.session.commit()
        return jsonify({'id': contact.id}), 201

    @app.route('/api/contacts/<int:id>/bookmark', methods=['PUT'])
    def toggle_bookmark(id):
        contact = Contact.query.get_or_404(id)
        contact.is_bookmarked = not contact.is_bookmarked
        db.session.commit()
        return jsonify({'is_bookmarked': contact.is_bookmarked})

    @app.route('/api/export', methods=['GET'])
    def export():
        try:
            file_path = export_to_excel()

            def cleanup():
                try:
                    os.unlink(file_path)
                except:
                    pass

            response = send_file(file_path, as_attachment=True, download_name='contacts.xlsx')
            response.call_on_close(cleanup)
            return response
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/import', methods=['POST'])
    def import_excel():
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        if not file.filename.endswith('.xlsx'):
            return jsonify({'error': 'Only .xlsx files allowed'}), 400

        # ✅ 使用临时文件（跨平台）
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        filepath = tmp_file.name
        tmp_file.close()
        file.save(filepath)

        try:
            import_from_excel(filepath)
            return jsonify({'message': 'Import successful'}), 200
        except Exception as e:
            return jsonify({'error': f'Import failed: {str(e)}'}), 500
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    # 删除联系人
    @app.route('/api/contacts/<int:contact_id>', methods=['DELETE'])
    def delete_contact(contact_id):
        contact = Contact.query.get_or_404(contact_id)
        db.session.delete(contact)
        db.session.commit()
        return jsonify({'message': '联系人已删除'}), 200
    # return app
    @app.route('/api/contacts/<int:id>', methods=['PUT'])
    def update_contact(id):
        contact = Contact.query.get_or_404(id)
        data = request.get_json()

        # 验证姓名
        name = (data.get('name') or '').strip()
        if not name:
            return jsonify({'error': 'Name is required'}), 400
        if len(name) > 100:
            return jsonify({'error': 'Name must be at most 100 characters'}), 400

        # 更新主字段
        contact.name = name
        contact.is_bookmarked = bool(data.get('is_bookmarked', False))

        # 处理联系方式：构建新的 ContactMethod 对象列表
        methods_data = data.get('methods', [])
        new_methods = []

        for m in methods_data:
            m_type = m.get('type')
            m_value = str(m.get('value', '')).strip()

            # 跳过空值
            if not m_value:
                continue

            # 验证 method_type 是否合法（匹配 Enum）
            if m_type not in {'phone', 'email', 'social', 'address'}:
                return jsonify({'error': f'Invalid contact method type: {m_type}'}), 400

            new_methods.append(ContactMethod(method_type=m_type, value=m_value))

        # 至少需要一个有效联系方式
        if not new_methods:
            return jsonify({'error': 'At least one valid contact method is required'}), 400

        # ⭐ 关键：直接赋值，SQLAlchemy 自动删除旧的 orphaned 记录
        contact.methods = new_methods

        try:
            db.session.commit()
            return jsonify({'message': 'Contact updated successfully'}), 200
        except IntegrityError as e:
            db.session.rollback()
            return jsonify({'error': 'Database integrity error'}), 500
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'An unexpected error occurred'}), 500

    return app