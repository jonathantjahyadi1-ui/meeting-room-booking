"""
Model: RoomBooking
-------------------
Data booking ruang meeting.
Menyimpan semua informasi pengajuan booking, approval, dan status.
"""
from datetime import datetime
from app.extensions import db


class RoomBooking(db.Model):
    __tablename__ = 'room_bookings'

    # Status booking yang valid
    STATUS_PENDING = 'Pending'
    STATUS_APPROVED = 'Approved'
    STATUS_REJECTED = 'Rejected'
    STATUS_CANCELLED = 'Cancelled'

    VALID_STATUSES = [STATUS_PENDING, STATUS_APPROVED, STATUS_REJECTED, STATUS_CANCELLED]

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    room_id = db.Column(db.Integer, db.ForeignKey('meeting_rooms.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    division = db.Column(db.String(50), nullable=False)
    meeting_date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    participant_count = db.Column(db.Integer, nullable=False)
    purpose = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text, default='')
    attachment = db.Column(db.String(500), default=None)
    status = db.Column(db.String(20), default=STATUS_PENDING, index=True)
    reject_reason = db.Column(db.Text, default=None)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), default=None)
    approved_at = db.Column(db.DateTime, default=None)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_active_booking(self):
        """Booking yang dihitung sebagai jadwal aktif (tidak bisa bentrok)."""
        return self.status in (self.STATUS_PENDING, self.STATUS_APPROVED)

    def can_cancel_by_user(self, user):
        """Cek apakah user bisa membatalkan booking ini."""
        if self.user_id != user.id:
            return False
        return self.status == self.STATUS_PENDING

    def get_status_badge_class(self):
        """Mengembalikan class CSS Bootstrap untuk badge status."""
        return {
            self.STATUS_PENDING: 'bg-warning text-dark',
            self.STATUS_APPROVED: 'bg-success',
            self.STATUS_REJECTED: 'bg-danger',
            self.STATUS_CANCELLED: 'bg-secondary',
        }.get(self.status, 'bg-secondary')

    def __repr__(self):
        return f'<RoomBooking {self.title} [{self.status}]>'