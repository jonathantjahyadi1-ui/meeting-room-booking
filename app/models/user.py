"""
Model: User
-----------
Menyimpan data user/karyawan yang bisa login ke sistem.
Password disimpan dalam bentuk hash (Werkzeug).
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='karyawan')
    division = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relasi ke booking (one-to-many)
    bookings = db.relationship('RoomBooking', backref='user', lazy='dynamic',
                               foreign_keys='RoomBooking.user_id')

    # Relasi ke approval (one-to-many)
    approvals = db.relationship('RoomBooking', backref='approver',
                                foreign_keys='RoomBooking.approved_by',
                                lazy='dynamic')

    def set_password(self, password):
        """Hash password dan simpan."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifikasi password terhadap hash."""
        return check_password_hash(self.password_hash, password)

    def is_role(self, *roles):
        """Cek apakah user memiliki salah satu role yang diberikan."""
        return self.role in roles

    def is_admin_or_above(self):
        """Cek apakah user adalah admin, HRD, atau direktur."""
        return self.role in ('admin', 'hrd', 'direktur')

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


@login_manager.user_loader
def load_user(user_id):
    """Callback Flask-Login untuk memuat user dari session."""
    return User.query.get(int(user_id))