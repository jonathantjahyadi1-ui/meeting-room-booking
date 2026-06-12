"""
Model: MeetingRoom
-------------------
Master data ruang meeting.
Hanya HRD, admin, dan direktur yang bisa mengelola.
"""
from datetime import datetime
from app.extensions import db


class MeetingRoom(db.Model):
    __tablename__ = 'meeting_rooms'

    id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    facilities = db.Column(db.Text, default='')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relasi ke booking (one-to-many)
    bookings = db.relationship('RoomBooking', backref='room', lazy='dynamic')

    def get_facilities_list(self):
        """Mengembalikan list fasilitas dari string yang dipisahkan koma."""
        if not self.facilities:
            return []
        return [f.strip() for f in self.facilities.split(',') if f.strip()]

    def __repr__(self):
        return f'<MeetingRoom {self.room_name} (cap={self.capacity})>'

    @classmethod
    def get_active_rooms(cls):
        """Ambil daftar ruangan aktif untuk dropdown form."""
        return cls.query.filter_by(is_active=True).order_by(cls.room_name).all()