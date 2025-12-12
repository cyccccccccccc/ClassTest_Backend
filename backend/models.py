from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_bookmarked = db.Column(db.Boolean, default=False, nullable=False)

    methods = db.relationship(
        'ContactMethod',
        backref='contact',
        cascade="all, delete-orphan",
        passive_deletes=True
    )

class ContactMethod(db.Model):
    __tablename__ = 'contact_methods'
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(
        db.Integer,
        db.ForeignKey('contacts.id', ondelete='CASCADE'),
        nullable=False
    )
    method_type = db.Column(db.Enum('phone', 'email', 'social', 'address'), nullable=False)
    value = db.Column(db.Text, nullable=False)