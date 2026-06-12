"""
Route: Dashboard
-----------------
Dashboard yang berbeda untuk setiap role:
- karyawan: ringkasan booking pribadi
- hrd: overview semua booking + pending
- admin/direktur: statistik lengkap
"""
from datetime import date
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.extensions import db
from app.models.room_booking import RoomBooking
from app.models.meeting_room import MeetingRoom
from app.models.division import Division

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    """Redirect ke dashboard sesuai role."""
    role = current_user.role

    if role == 'karyawan':
        return _dashboard_karyawan()
    elif role == 'hrd':
        return _dashboard_hrd()
    elif role in ('admin', 'direktur'):
        return _dashboard_admin()
    else:
        return _dashboard_karyawan()


def _dashboard_karyawan():
    """Dashboard untuk role karyawan — hanya booking milik sendiri."""
    user_id = current_user.id

    total_bookings = RoomBooking.query.filter_by(user_id=user_id).count()
    pending_count = RoomBooking.query.filter_by(
        user_id=user_id, status=RoomBooking.STATUS_PENDING
    ).count()
    approved_count = RoomBooking.query.filter_by(
        user_id=user_id, status=RoomBooking.STATUS_APPROVED
    ).count()
    rejected_count = RoomBooking.query.filter_by(
        user_id=user_id, status=RoomBooking.STATUS_REJECTED
    ).count()

    recent_bookings = RoomBooking.query.filter_by(user_id=user_id).order_by(
        RoomBooking.created_at.desc()
    ).limit(5).all()

    rooms = MeetingRoom.get_active_rooms()
    divisions = Division.get_active_choices()

    return render_template(
        'dashboard/karyawan.html',
        total_bookings=total_bookings,
        pending_count=pending_count,
        approved_count=approved_count,
        rejected_count=rejected_count,
        recent_bookings=recent_bookings,
        rooms=rooms,
        divisions=divisions,
    )


def _dashboard_hrd():
    """Dashboard untuk role HRD — semua booking + pending count."""
    total_bookings = RoomBooking.query.count()
    pending_count = RoomBooking.query.filter_by(
        status=RoomBooking.STATUS_PENDING
    ).count()
    approved_count = RoomBooking.query.filter_by(
        status=RoomBooking.STATUS_APPROVED
    ).count()
    rejected_count = RoomBooking.query.filter_by(
        status=RoomBooking.STATUS_REJECTED
    ).count()

    # Booking pending terbaru
    pending_bookings = RoomBooking.query.filter_by(
        status=RoomBooking.STATUS_PENDING
    ).order_by(RoomBooking.created_at.asc()).limit(10).all()

    # Booking per divisi
    division_stats = db.session.query(
        RoomBooking.division,
        db.func.count(RoomBooking.id).label('total')
    ).group_by(RoomBooking.division).all()

    return render_template(
        'dashboard/hrd.html',
        total_bookings=total_bookings,
        pending_count=pending_count,
        approved_count=approved_count,
        rejected_count=rejected_count,
        pending_bookings=pending_bookings,
        division_stats=division_stats,
    )


def _dashboard_admin():
    """Dashboard untuk admin/direktur — statistik lengkap."""
    total_bookings = RoomBooking.query.count()
    pending_count = RoomBooking.query.filter_by(
        status=RoomBooking.STATUS_PENDING
    ).count()
    approved_count = RoomBooking.query.filter_by(
        status=RoomBooking.STATUS_APPROVED
    ).count()
    rejected_count = RoomBooking.query.filter_by(
        status=RoomBooking.STATUS_REJECTED
    ).count()
    cancelled_count = RoomBooking.query.filter_by(
        status=RoomBooking.STATUS_CANCELLED
    ).count()

    total_rooms = MeetingRoom.query.count()
    active_rooms = MeetingRoom.query.filter_by(is_active=True).count()

    # Booking terbaru (semua)
    recent_bookings = RoomBooking.query.order_by(
        RoomBooking.created_at.desc()
    ).limit(10).all()

    # Statistik per divisi
    division_stats = db.session.query(
        RoomBooking.division,
        db.func.count(RoomBooking.id).label('total')
    ).group_by(RoomBooking.division).all()

    return render_template(
        'dashboard/admin.html',
        total_bookings=total_bookings,
        pending_count=pending_count,
        approved_count=approved_count,
        rejected_count=rejected_count,
        cancelled_count=cancelled_count,
        total_rooms=total_rooms,
        active_rooms=active_rooms,
        recent_bookings=recent_bookings,
        division_stats=division_stats,
    )