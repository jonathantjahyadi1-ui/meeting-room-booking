"""
Model: Division
----------------
Master data divisi perusahaan.
Digunakan pada register, form booking, dan filter laporan.
"""
from datetime import datetime
from app.extensions import db


class Division(db.Model):
    __tablename__ = 'divisions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Division {self.name}>'

    @classmethod
    def seed_defaults(cls):
        """
        Isi data awal divisi jika tabel masih kosong.
        Dipanggil setelah database dibuat pertama kali.
        """
        defaults = [
            'IT', 'Operational', 'HRD', 'Marketing',
            'Creative', 'Hostlive', 'Finance', 'Direktur'
]
        for name in defaults:
            if not cls.query.filter_by(name=name).first():
                db.session.add(cls(name=name))
        db.session.commit()

    @classmethod
    def get_active_choices(cls):
        """Ambil daftar divisi aktif untuk dropdown form."""
        return [(d.name, d.name) for d in cls.query.filter_by(is_active=True).order_by(cls.name).all()]