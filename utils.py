# utils.py（替换全部内容）
import pandas as pd
import os
import tempfile
from .models import Contact, ContactMethod, db


def export_to_excel():
    contacts = Contact.query.all()
    rows = []
    for contact in contacts:
        row = {
            'name': contact.name,
            'is_bookmarked': int(contact.is_bookmarked)
        }
        method_counts = {'phone': 0, 'email': 0, 'social': 0, 'address': 0}
        for method in contact.methods:
            method_counts[method.method_type] += 1
            col_name = f"{method.method_type}_{method_counts[method.method_type]}"
            row[col_name] = method.value
        rows.append(row)

    df = pd.DataFrame(rows)

    # ✅ 使用跨平台临时文件
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    tmp_file.close()
    df.to_excel(tmp_file.name, index=False)
    return tmp_file.name  # 返回真实路径


def import_from_excel(file_path):
    try:
        df = pd.read_excel(file_path, dtype=str)
        df = df.fillna('')
        for _, row in df.iterrows():
            name = row.get('name', '').strip()
            if not name:
                continue
            is_bookmarked = str(row.get('is_bookmarked', '0')).lower() in ['1', 'true', 'yes']
            contact = Contact(name=name, is_bookmarked=is_bookmarked)
            db.session.add(contact)
            db.session.flush()

            for col in df.columns:
                if col in ['name', 'is_bookmarked']:
                    continue
                value = str(row[col]).strip()
                if not value:
                    continue
                if '_' not in col:
                    continue
                method_type = col.rsplit('_', 1)[0]
                if method_type in ['phone', 'email', 'social', 'address']:
                    method = ContactMethod(
                        contact_id=contact.id,
                        method_type=method_type,
                        value=value
                    )
                    db.session.add(method)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e