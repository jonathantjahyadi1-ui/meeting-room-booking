"""
Service: Report
----------------
Business logic untuk laporan dan agregasi data booking.
Digunakan oleh halaman laporan (HRD, admin, direktur).
"""
from datetime import date, datetime
from sqlalchemy import func, extract
from app.extensions import db
from app.models.room_booking import RoomBooking
from app.models.meeting_room import MeetingRoom


class ReportService:
    """Service class untuk laporan booking."""

    @staticmethod
    def get_summary(start_date=None, end_date=None, division=None, room_id=None):
        """
        Ambil data ringkasan booking dengan filter opsional.

        Returns:
            dict dengan key: total, pending, approved, rejected, cancelled,
                            top_rooms, top_divisions, by_division, by_room
        """
        # Base query
        base_query = RoomBooking.query

        if start_date:
            base_query = base_query.filter(RoomBooking.meeting_date >= start_date)
        if end_date:
            base_query = base_query.filter(RoomBooking.meeting_date <= end_date)
        if division:
            base_query = base_query.filter(RoomBooking.division == division)
        if room_id:
            base_query = base_query.filter(RoomBooking.room_id == room_id)

        # Hitung per status
        total = base_query.count()
        pending = base_query.filter(RoomBooking.status == RoomBooking.STATUS_PENDING).count()
        approved = base_query.filter(RoomBooking.status == RoomBooking.STATUS_APPROVED).count()
        rejected = base_query.filter(RoomBooking.status == RoomBooking.STATUS_REJECTED).count()
        cancelled = base_query.filter(RoomBooking.status == RoomBooking.STATUS_CANCELLED).count()

        # Ruangan paling sering digunakan
        top_rooms = db.session.query(
            MeetingRoom.room_name,
            func.count(RoomBooking.id).label('total')
        ).join(
            RoomBooking, RoomBooking.room_id == MeetingRoom.id
        ).filter(
            RoomBooking.status == RoomBooking.STATUS_APPROVED
        )

        if start_date:
            top_rooms = top_rooms.filter(RoomBooking.meeting_date >= start_date)
        if end_date:
            top_rooms = top_rooms.filter(RoomBooking.meeting_date <= end_date)
        if division:
            top_rooms = top_rooms.filter(RoomBooking.division == division)
        if room_id:
            top_rooms = top_rooms.filter(RoomBooking.room_id == room_id)

        top_rooms = top_rooms.group_by(MeetingRoom.room_name).order_by(
            func.count(RoomBooking.id).desc()
        ).limit(5).all()

        # Divisi paling sering booking
        top_divisions = base_query.filter(
            RoomBooking.status == RoomBooking.STATUS_APPROVED
        ).with_entities(
            RoomBooking.division,
            func.count(RoomBooking.id).label('total')
        ).group_by(
            RoomBooking.division
        ).order_by(
            func.count(RoomBooking.id).desc()
        ).all()

        # Booking per divisi (semua status)
        by_division = base_query.with_entities(
            RoomBooking.division,
            func.count(RoomBooking.id).label('total')
        ).group_by(RoomBooking.division).order_by(RoomBooking.division).all()

        # Booking per ruangan (semua status)
        by_room_simple = base_query.with_entities(
            MeetingRoom.room_name,
            func.count(RoomBooking.id).label('total')
        ).join(
            MeetingRoom, RoomBooking.room_id == MeetingRoom.id
        ).group_by(MeetingRoom.room_name).order_by(MeetingRoom.room_name).all()

        return {
            'total': total,
            'pending': pending,
            'approved': approved,
            'rejected': rejected,
            'cancelled': cancelled,
            'top_rooms': [(r.room_name, r.total) for r in top_rooms],
            'top_divisions': [(d.division, d.total) for d in top_divisions],
            'by_division': [(d.division, d.total) for d in by_division],
            'by_room': [(r.room_name, r.total) for r in by_room_simple],
        }

    @staticmethod
    def get_export_data(start_date=None, end_date=None, division=None, room_id=None, status=None):
        """
        Ambil data booking untuk export ke Excel.

        Returns:
            List of RoomBooking objects dengan filter.
        """
        query = RoomBooking.query

        if start_date:
            query = query.filter(RoomBooking.meeting_date >= start_date)
        if end_date:
            query = query.filter(RoomBooking.meeting_date <= end_date)
        if division:
            query = query.filter(RoomBooking.division == division)
        if room_id:
            query = query.filter(RoomBooking.room_id == room_id)
        if status:
            query = query.filter(RoomBooking.status == status)

        return query.order_by(RoomBooking.meeting_date.desc(), RoomBooking.start_time).all()